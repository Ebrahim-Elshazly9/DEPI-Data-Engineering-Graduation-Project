from fastapi import APIRouter, Depends, HTTPException
from app.database import get_supabase
from app.middleware.auth import verify_supabase_token
from app.models.journal import JournalEntryCreate, JournalEntryResponse
from typing import List

router = APIRouter(prefix="/api/journal", tags=["Journal"])


@router.post("")
async def create_journal_entry(
    data: JournalEntryCreate,
    user: dict = Depends(verify_supabase_token),
) -> JournalEntryResponse:
    supabase = get_supabase()
    result = supabase.table("journals").insert({
        "user_id": user["id"],
        "title": data.title,
        "content": data.content,
        "mood": data.mood,
        "mood_score": data.mood_score,
        "tags": data.tags,
    }).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create journal entry")
    return JournalEntryResponse(**result.data[0])


@router.get("")
async def list_journal_entries(user: dict = Depends(verify_supabase_token)) -> list[JournalEntryResponse]:
    supabase = get_supabase()
    result = supabase.table("journals") \
        .select("*") \
        .eq("user_id", user["id"]) \
        .order("created_at", desc=True) \
        .execute()
    return [JournalEntryResponse(**r) for r in (result.data or [])]


@router.get("/{id}")
async def get_journal_entry(
    id: str,
    user: dict = Depends(verify_supabase_token),
) -> JournalEntryResponse:
    supabase = get_supabase()
    result = supabase.table("journals") \
        .select("*") \
        .eq("id", id) \
        .eq("user_id", user["id"]) \
        .single() \
        .execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return JournalEntryResponse(**result.data)


@router.put("/{id}")
async def update_journal_entry(
    id: str,
    data: JournalEntryCreate,
    user: dict = Depends(verify_supabase_token),
) -> JournalEntryResponse:
    supabase = get_supabase()
    update_data = data.model_dump(exclude_none=True)
    update_data["updated_at"] = "now()"
    result = supabase.table("journals") \
        .update(update_data) \
        .eq("id", id) \
        .eq("user_id", user["id"]) \
        .execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return JournalEntryResponse(**result.data[0])


@router.delete("/{id}")
async def delete_journal_entry(
    id: str,
    user: dict = Depends(verify_supabase_token),
) -> dict:
    supabase = get_supabase()
    result = supabase.table("journals") \
        .delete() \
        .eq("id", id) \
        .eq("user_id", user["id"]) \
        .execute()
    return {"ok": True}


@router.post("/analyze")
async def analyze_journal_text(
    data: dict,
    user: dict = Depends(verify_supabase_token),
) -> dict:
    from app.services.nlp_service import run_nlp_pipeline
    from app.services.prediction_service import generate_predictions

    text = data.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")

    nlp = await run_nlp_pipeline(text)
    preds = await generate_predictions(nlp, user["id"])

    return {
        "nlp": nlp,
        "predictions": preds["predictions"],
        "risk_category": preds["risk_category"],
        "recommendations": preds["recommendations"][:3],
    }
