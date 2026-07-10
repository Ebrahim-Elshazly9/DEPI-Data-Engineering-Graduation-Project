from fastapi import APIRouter, Depends
from app.database import get_supabase
from app.middleware.auth import verify_supabase_token
from app.models.nlp import RecommendationResponse
from typing import Optional, List

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.get("")
async def get_recommendations(
    user: dict = Depends(verify_supabase_token),
    category: Optional[str] = None,
) -> List[RecommendationResponse]:
    supabase = get_supabase()
    query = supabase.table("recommendations") \
        .select("*") \
        .eq("user_id", user["id"]) \
        .order("priority", asc=True)
    if category:
        query = query.eq("category", category)
    result = query.execute()
    return [RecommendationResponse(**r) for r in (result.data or [])]


@router.put("/{id}/complete")
async def toggle_recommendation(
    id: str,
    data: dict,
    user: dict = Depends(verify_supabase_token),
) -> dict:
    supabase = get_supabase()
    completed = data.get("completed", True)
    supabase.table("recommendations") \
        .update({"completed": completed}) \
        .eq("id", id) \
        .eq("user_id", user["id"]) \
        .execute()
    return {"ok": True}
