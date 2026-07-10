from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.database import get_supabase
from app.middleware.auth import verify_supabase_token
from app.services.rag_service import generate_embedding
from typing import List
import uuid

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user: dict = Depends(verify_supabase_token),
) -> dict:
    content = await file.read()
    text = content.decode("utf-8", errors="replace")

    supabase = get_supabase()
    doc_result = supabase.table("uploaded_documents").insert({
        "user_id": user["id"],
        "filename": file.filename,
        "file_type": file.filename.split(".")[-1] if "." in file.filename else "txt",
        "file_size": len(content),
        "text_content": text,
        "status": "processing",
    }).execute()

    if not doc_result.data:
        raise HTTPException(status_code=500, detail="Failed to upload document")

    doc_id = doc_result.data[0]["id"]
    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        supabase.table("document_chunks").insert({
            "document_id": doc_id,
            "chunk_index": i,
            "content": chunk,
        }).execute()
        embedding = await generate_embedding(chunk)
        supabase.table("document_chunks").update({"embedding": embedding}).eq("document_id", doc_id).eq("chunk_index", i).execute()

    supabase.table("uploaded_documents").update({"status": "ready"}).eq("id", doc_id).execute()

    return {"id": doc_id, "filename": file.filename, "chunks": len(chunks), "status": "ready"}


@router.get("")
async def list_documents(user: dict = Depends(verify_supabase_token)) -> list[dict]:
    supabase = get_supabase()
    result = supabase.table("uploaded_documents") \
        .select("id,filename,file_type,file_size,status,created_at") \
        .eq("user_id", user["id"]) \
        .order("created_at", desc=True) \
        .execute()
    return result.data or []


@router.delete("/{id}")
async def delete_document(id: str, user: dict = Depends(verify_supabase_token)) -> dict:
    supabase = get_supabase()
    supabase.table("document_chunks").delete().eq("document_id", id).execute()
    supabase.table("uploaded_documents").delete().eq("id", id).eq("user_id", user["id"]).execute()
    return {"ok": True}


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks if chunks else [text[:500]]
