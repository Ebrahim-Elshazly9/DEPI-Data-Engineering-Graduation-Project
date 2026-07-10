from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.database import get_supabase
from app.middleware.auth import verify_supabase_token
from app.models.assessment import (
    AssessmentCreate,
    AssessmentResponse,
    AssessmentReportResponse,
    ASSESSMENTS,
)
from app.services.nlp_service import run_nlp_pipeline
from app.services.prediction_service import generate_predictions
from app.services.pdf_service import generate_assessment_pdf
from typing import List

router = APIRouter(prefix="/api/assessments", tags=["Assessments"])


@router.get("/definitions")
async def get_assessment_definitions() -> dict:
    return {"assessments": {k: v.model_dump() for k, v in ASSESSMENTS.items()}}


@router.get("/definition/{type}")
async def get_assessment_definition(type: str):
    if type not in ASSESSMENTS:
        raise HTTPException(status_code=404, detail="Assessment type not found")
    return ASSESSMENTS[type].model_dump()


@router.post("")
async def create_assessment(
    data: AssessmentCreate,
    user: dict = Depends(verify_supabase_token),
) -> AssessmentResponse:
    supabase = get_supabase()
    result = supabase.table("assessments").insert({
        "patient_id": user["id"],
        "type": data.type,
        "title": data.title,
        "score": data.score,
        "max_score": data.max_score,
        "severity": data.severity,
        "label": data.label,
        "answers": data.answers,
        "status": data.status,
    }).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create assessment")
    return AssessmentResponse(**result.data[0])


@router.get("")
async def get_assessments(user: dict = Depends(verify_supabase_token)) -> list[AssessmentResponse]:
    supabase = get_supabase()
    result = supabase.table("assessments") \
        .select("*") \
        .eq("patient_id", user["id"]) \
        .order("created_at", desc=True) \
        .execute()
    return [AssessmentResponse(**r) for r in (result.data or [])]


@router.get("/latest")
async def get_latest_assessment(user: dict = Depends(verify_supabase_token)) -> AssessmentResponse | None:
    supabase = get_supabase()
    result = supabase.table("assessments") \
        .select("*") \
        .eq("patient_id", user["id"]) \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute()
    if not result.data:
        return None
    return AssessmentResponse(**result.data[0])


@router.get("/{id}")
async def get_assessment(id: str, user: dict = Depends(verify_supabase_token)) -> AssessmentResponse:
    supabase = get_supabase()
    result = supabase.table("assessments") \
        .select("*") \
        .eq("id", id) \
        .eq("patient_id", user["id"]) \
        .single() \
        .execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return AssessmentResponse(**result.data)


@router.post("/{id}/analyze")
async def analyze_assessment(
    id: str,
    background_tasks: BackgroundTasks,
    user: dict = Depends(verify_supabase_token),
) -> dict:
    supabase = get_supabase()
    result = supabase.table("assessments") \
        .select("*") \
        .eq("id", id) \
        .eq("patient_id", user["id"]) \
        .single() \
        .execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Assessment not found")

    assessment = result.data
    text_for_analysis = str(assessment.get("answers", {}))
    if assessment.get("text_input"):
        text_for_analysis += " " + assessment["text_input"]

    nlp = await run_nlp_pipeline(text_for_analysis)
    preds = await generate_predictions(nlp, user["id"])

    report_data = {
        "assessment_id": id,
        "user_id": user["id"],
        "type": assessment.get("type", "unknown"),
        "score": assessment.get("score", 0),
        "risk_category": preds["risk_category"],
        "predicted_state": preds["predictions"].get("wellness_score", 5),
        "confidence_score": preds["predictions"].get("emotional_stability", 5) / 10,
        "emotions_detected": [nlp["emotions"]["primary"]] + nlp["emotions"]["secondary"],
        "topics_detected": nlp["topics"],
        "ai_summary": preds["reasoning"],
        "recommendations": [r["description"] for r in preds["recommendations"]],
        "suggested_activities": [r["title"] for r in preds["recommendations"][:3]],
        "suggested_breathing": next((r["title"] for r in preds["recommendations"] if r["category"] == "Breathing Exercises"), None),
        "suggested_journal_prompt": f"Reflect on your {assessment.get('type', 'assessment')} results. How do you feel about your score? What steps can you take today?",
        "suggested_goals": [r["title"] for r in preds["recommendations"][:2]],
    }

    report = supabase.table("assessment_reports").insert(report_data).execute()

    if nlp["crisis_detected"]:
        supabase.table("critical_alerts").insert({
            "patient_id": user["id"],
            "assessment_id": id,
            "risk_score": assessment.get("score", 0),
            "status": "open",
            "notes": "Crisis indicators detected during assessment analysis",
        }).execute()

    return {
        "nlp": nlp,
        "predictions": preds["predictions"],
        "risk_category": preds["risk_category"],
        "reasoning": preds["reasoning"],
        "recommendations": preds["recommendations"],
        "report": report.data[0] if report.data else None,
        "crisis_detected": nlp["crisis_detected"],
    }


@router.get("/{id}/report")
async def get_assessment_report(
    id: str,
    user: dict = Depends(verify_supabase_token),
) -> AssessmentReportResponse | None:
    supabase = get_supabase()
    result = supabase.table("assessment_reports") \
        .select("*") \
        .eq("assessment_id", id) \
        .eq("user_id", user["id"]) \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute()
    if not result.data:
        return None
    return AssessmentReportResponse(**result.data[0])


@router.get("/{id}/report/pdf")
async def download_assessment_pdf(
    id: str,
    user: dict = Depends(verify_supabase_token),
):
    from fastapi.responses import Response

    supabase = get_supabase()
    result = supabase.table("assessment_reports") \
        .select("*") \
        .eq("assessment_id", id) \
        .eq("user_id", user["id"]) \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Report not found")

    report = result.data[0]
    profile = supabase.table("profiles").select("*").eq("id", user["id"]).single().execute()
    profile_data = profile.data if profile.data else {}

    pdf_bytes = await generate_assessment_pdf(report, profile_data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=mindguard-report-{id[:8]}.pdf"},
    )
