from fastapi import APIRouter, Depends
from app.database import get_supabase
from app.middleware.auth import verify_supabase_token

router = APIRouter(prefix="/api/admin", tags=["Admin"])


async def require_admin(user: dict = Depends(verify_supabase_token)) -> dict:
    supabase = get_supabase()
    role_check = supabase.table("user_roles") \
        .select("role") \
        .eq("user_id", user["id"]) \
        .execute()
    is_admin = False
    if role_check.data:
        is_admin = any(r.get("role") == "admin" for r in role_check.data)

    if not is_admin:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


@router.get("/users")
async def list_users(admin: dict = Depends(require_admin)) -> list[dict]:
    supabase = get_supabase()
    result = supabase.table("profiles").select("*").limit(100).execute()
    return result.data or []


@router.get("/assessments")
async def all_assessments(admin: dict = Depends(require_admin)) -> list[dict]:
    supabase = get_supabase()
    result = supabase.table("assessments") \
        .select("*") \
        .order("created_at", desc=True) \
        .limit(100) \
        .execute()
    return result.data or []


@router.get("/critical-alerts")
async def critical_alerts(admin: dict = Depends(require_admin)) -> list[dict]:
    supabase = get_supabase()
    result = supabase.table("critical_alerts") \
        .select("*, assessments!inner(patient_id)") \
        .order("created_at", desc=True) \
        .limit(50) \
        .execute()
    return result.data or []


@router.put("/critical-alerts/{id}")
async def update_alert(
    id: str,
    data: dict,
    admin: dict = Depends(require_admin),
) -> dict:
    supabase = get_supabase()
    allowed = {"status", "notes"}
    update_data = {k: v for k, v in data.items() if k in allowed}
    if "status" in update_data and update_data["status"] == "resolved":
        update_data["resolved_at"] = "now()"
    supabase.table("critical_alerts").update(update_data).eq("id", id).execute()
    return {"ok": True}


@router.get("/analytics")
async def platform_analytics(admin: dict = Depends(require_admin)) -> dict:
    supabase = get_supabase()

    total_users = supabase.table("profiles").select("id", count="exact").execute()
    total_assessments = supabase.table("assessments").select("id", count="exact").execute()
    total_chats = supabase.table("chat_sessions").select("id", count="exact").execute()
    total_journals = supabase.table("journals").select("id", count="exact").execute()
    open_alerts = supabase.table("critical_alerts") \
        .select("id", count="exact") \
        .eq("status", "open") \
        .execute()

    return {
        "total_users": getattr(total_users, 'count', len(total_users.data or [])),
        "total_assessments": getattr(total_assessments, 'count', len(total_assessments.data or [])),
        "total_chat_sessions": getattr(total_chats, 'count', len(total_chats.data or [])),
        "total_journal_entries": getattr(total_journals, 'count', len(total_journals.data or [])),
        "open_critical_alerts": getattr(open_alerts, 'count', len(open_alerts.data or [])),
    }
