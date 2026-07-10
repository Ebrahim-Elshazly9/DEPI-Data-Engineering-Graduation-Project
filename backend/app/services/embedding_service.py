from app.database import get_supabase
from app.services.rag_service import generate_embedding


async def embed_and_store_knowledge_base():
    supabase = get_supabase()
    articles = supabase.table("knowledge_base").select("*").is_("embedding", "null").execute()
    if not articles.data:
        return

    for article in articles.data:
        text = article["title"] + " " + article["content"]
        embedding = await generate_embedding(text)
        supabase.table("knowledge_base").update({"embedding": embedding}).eq("id", article["id"]).execute()


async def embed_and_store_document_chunks(document_id: str):
    supabase = get_supabase()
    chunks = supabase.table("document_chunks") \
        .select("*") \
        .eq("document_id", document_id) \
        .is_("embedding", "null") \
        .execute()
    if not chunks.data:
        return

    for chunk in chunks.data:
        embedding = await generate_embedding(chunk["content"])
        supabase.table("document_chunks").update({"embedding": embedding}).eq("id", chunk["id"]).execute()


async def embed_conversation_memory(memory_id: str, text: str):
    supabase = get_supabase()
    embedding = await generate_embedding(text)
    supabase.table("conversation_memory").update({"embedding": embedding}).eq("id", memory_id).execute()
