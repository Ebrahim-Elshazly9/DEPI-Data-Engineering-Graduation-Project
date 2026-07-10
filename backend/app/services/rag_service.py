from app.database import get_supabase
from app.config import settings
from typing import Optional
import json
import httpx


async def generate_embedding(text: str) -> list[float]:
    if settings.ai_provider == "openai" and settings.openai_api_key:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={"model": settings.embedding_model, "input": text},
            )
            data = resp.json()
            return data["data"][0]["embedding"]

    return [0.0] * 1536


async def search_knowledge_base(query: str, limit: int = 5) -> list[dict]:
    supabase = get_supabase()
    try:
        embedding = await generate_embedding(query)
        embedding_str = "[" + ",".join(str(v) for v in embedding) + "]"
        result = supabase.rpc(
            "match_knowledge_base",
            {"query_embedding": embedding_str, "match_threshold": 0.3, "match_count": limit},
        ).execute()
        if result.data:
            return result.data
    except Exception:
        pass

    result = supabase.table("knowledge_base").select("*").limit(limit).execute()
    return result.data if result.data else []


async def search_documents(user_id: str, query: str, limit: int = 3) -> list[dict]:
    supabase = get_supabase()
    try:
        embedding = await generate_embedding(query)
        embedding_str = "[" + ",".join(str(v) for v in embedding) + "]"
        result = supabase.rpc(
            "match_document_chunks",
            {"query_embedding": embedding_str, "match_threshold": 0.3, "match_count": limit},
        ).execute()
        if result.data:
            return result.data
    except Exception:
        pass
    return []


async def retrieve_context(
    user_id: str,
    message: str,
    include_history: bool = True,
    include_kb: bool = True,
    include_docs: bool = True,
) -> dict:
    context_parts = []

    if include_kb:
        kb_results = await search_knowledge_base(message)
        if kb_results:
            context_parts.append("=== Knowledge Base ===")
            for r in kb_results:
                context_parts.append(f"Source ({r.get('source', 'General')}): {r.get('content', '')[:500]}")

    if include_docs and user_id:
        doc_results = await search_documents(user_id, message)
        if doc_results:
            context_parts.append("=== Your Documents ===")
            for r in doc_results:
                context_parts.append(r.get("content", "")[:500])

    if include_history and user_id:
        supabase = get_supabase()
        recent = supabase.table("conversation_memory") \
            .select("summary") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(3) \
            .execute()
        if recent.data:
            context_parts.append("=== Conversation History ===")
            for r in recent.data:
                context_parts.append(r.get("summary", ""))

    return {"context": "\n\n".join(context_parts) if context_parts else "", "sources": kb_results if include_kb else []}
