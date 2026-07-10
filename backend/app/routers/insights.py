from fastapi import APIRouter, Depends
from app.database import get_supabase
from app.middleware.auth import verify_supabase_token
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/insights", tags=["Insights"])


@router.get("/dashboard")
async def get_dashboard_insights(user: dict = Depends(verify_supabase_token)) -> dict:
    supabase = get_supabase()
    user_id = user["id"]

    # Get latest assessment
    latest_assessment = supabase.table("assessments") \
        .select("*") \
        .eq("patient_id", user_id) \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute()

    # Get recent mood data
    moods = supabase.table("moods") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .limit(14) \
        .execute()

    # Get recent predictions
    predictions = supabase.table("predictions") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .limit(10) \
        .execute()

    # Get activity counts
    chat_count = supabase.table("chat_sessions") \
        .select("id", count="exact") \
        .eq("user_id", user_id) \
        .execute()
    journal_count = supabase.table("journals") \
        .select("id", count="exact") \
        .eq("user_id", user_id) \
        .execute()
    assessment_count = supabase.table("assessments") \
        .select("id", count="exact") \
        .eq("patient_id", user_id) \
        .execute()

    # Get AI insights
    ai_insights = supabase.table("ai_insights") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute()

    return {
        "latest_assessment": latest_assessment.data[0] if latest_assessment.data else None,
        "mood_trend": [{"score": m["mood_score"], "label": m.get("mood_label"), "date": m["created_at"]} for m in (moods.data or [])],
        "predictions": predictions.data or [],
        "activity": {
            "chat_sessions": chat_count.count if hasattr(chat_count, 'count') else len(chat_count.data or []),
            "journal_entries": journal_count.count if hasattr(journal_count, 'count') else len(journal_count.data or []),
            "assessments": assessment_count.count if hasattr(assessment_count, 'count') else len(assessment_count.data or []),
        },
        "ai_insights": ai_insights.data[0] if ai_insights.data else None,
    }


@router.get("/nlp-history")
async def get_nlp_history(user: dict = Depends(verify_supabase_token)) -> dict:
    supabase = get_supabase()
    user_id = user["id"]

    emotions = supabase.table("emotion_analysis") \
        .select("primary_emotion,stress_level,sentiment_score,created_at") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .limit(50) \
        .execute()

    sentiment = supabase.table("sentiment_analysis") \
        .select("sentiment_score,sentiment_label,keywords,topics,created_at") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .limit(50) \
        .execute()

    return {
        "emotions": emotions.data or [],
        "sentiment": sentiment.data or [],
    }
