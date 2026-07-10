from supabase import create_client, Client
from app.config import settings

_supabase: Client | None = None


def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(
            settings.supabase_url,
            settings.supabase_service_key or settings.supabase_anon_key,
        )
    return _supabase


async def get_user_by_id(user_id: str) -> dict | None:
    supabase = get_supabase()
    result = supabase.table("profiles").select("*").eq("id", user_id).execute()
    return result.data[0] if result.data else None


async def create_or_update_profile(user_id: str, data: dict) -> dict:
    supabase = get_supabase()
    existing = await get_user_by_id(user_id)
    if existing:
        result = supabase.table("profiles").update(data).eq("id", user_id).execute()
    else:
        data["id"] = user_id
        result = supabase.table("profiles").insert(data).execute()
    return result.data[0] if result.data else data
