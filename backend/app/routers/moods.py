from fastapi import APIRouter, Depends, HTTPException
from app.database import get_supabase
from app.middleware.auth import verify_supabase_token
from app.models.user import MoodCreate, MoodEntry
from typing import List

router = APIRouter(prefix="/api/moods", tags=["Moods"])


@router.post("")
async def create_mood(data: MoodCreate, user: dict = Depends(verify_supabase_token)) -> MoodEntry:
    supabase = get_supabase()
    result = supabase.table("moods").insert({
        "user_id": user["id"],
        "mood_score": data.mood_score,
        "mood_label": data.mood_label,
        "note": data.note,
    }).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to save mood")
    return MoodEntry(**result.data[0])


@router.get("")
async def list_moods(user: dict = Depends(verify_supabase_token)) -> list[MoodEntry]:
    supabase = get_supabase()
    result = supabase.table("moods") \
        .select("*") \
        .eq("user_id", user["id"]) \
        .order("created_at", desc=True) \
        .limit(30) \
        .execute()
    return [MoodEntry(**r) for r in (result.data or [])]
