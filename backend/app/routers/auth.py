from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_supabase, create_or_update_profile
from app.middleware.auth import verify_supabase_token
from app.models.user import UserProfile, UserProfileUpdate
from typing import Optional

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.get("/me")
async def get_current_user(user: dict = Depends(verify_supabase_token)) -> dict:
    return {
        "id": user["id"],
        "email": user.get("email", ""),
        "user_metadata": {k: v for k, v in user.items() if k not in ("id", "email", "aud", "role")},
    }


@router.get("/profile")
async def get_profile(user: dict = Depends(verify_supabase_token)) -> Optional[UserProfile]:
    supabase = get_supabase()
    result = supabase.table("profiles").select("*").eq("id", user["id"]).execute()
    if not result.data:
        return None
    return UserProfile(**result.data[0])


@router.put("/profile")
async def update_profile(
    data: UserProfileUpdate,
    user: dict = Depends(verify_supabase_token),
) -> UserProfile:
    updated = await create_or_create_profile(user["id"], data.model_dump(exclude_none=True))
    return UserProfile(**updated)
