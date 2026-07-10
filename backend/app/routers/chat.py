from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.database import get_supabase
from app.middleware.auth import verify_supabase_token
from app.models.chat import (
    SessionCreate, SessionResponse, MessageCreate,
    MessageResponse, ChatRequest, ChatResponse,
)
from app.services.nlp_service import run_nlp_pipeline
from app.services.prediction_service import generate_predictions
from app.services.rag_service import retrieve_context
from app.services.llm_service import generate_chat_response
from typing import List

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/sessions")
async def create_session(
    data: SessionCreate,
    user: dict = Depends(verify_supabase_token),
) -> SessionResponse:
    supabase = get_supabase()
    result = supabase.table("chat_sessions").insert({
        "user_id": user["id"],
        "title": data.title,
    }).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create session")
    return SessionResponse(**result.data[0])


@router.get("/sessions")
async def list_sessions(user: dict = Depends(verify_supabase_token)) -> list[SessionResponse]:
    supabase = get_supabase()
    result = supabase.table("chat_sessions") \
        .select("*") \
        .eq("user_id", user["id"]) \
        .order("updated_at", desc=True) \
        .execute()
    return [SessionResponse(**r) for r in (result.data or [])]


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    user: dict = Depends(verify_supabase_token),
) -> SessionResponse:
    supabase = get_supabase()
    result = supabase.table("chat_sessions") \
        .select("*") \
        .eq("id", session_id) \
        .eq("user_id", user["id"]) \
        .single() \
        .execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(**result.data)


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    user: dict = Depends(verify_supabase_token),
) -> dict:
    supabase = get_supabase()
    supabase.table("chat_sessions") \
        .delete() \
        .eq("id", session_id) \
        .eq("user_id", user["id"]) \
        .execute()
    return {"ok": True}


@router.get("/sessions/{session_id}/messages")
async def get_messages(
    session_id: str,
    user: dict = Depends(verify_supabase_token),
) -> list[MessageResponse]:
    supabase = get_supabase()
    result = supabase.table("chat_messages") \
        .select("*") \
        .eq("session_id", session_id) \
        .order("created_at", asc=True) \
        .execute()
    return [MessageResponse(**r) for r in (result.data or [])]


@router.post("/message")
async def send_message(
    data: ChatRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(verify_supabase_token),
) -> ChatResponse:
    supabase = get_supabase()

    session = supabase.table("chat_sessions") \
        .select("*") \
        .eq("id", data.session_id) \
        .eq("user_id", user["id"]) \
        .single() \
        .execute()
    if not session.data:
        raise HTTPException(status_code=404, detail="Session not found")

    supabase.table("chat_messages").insert({
        "session_id": data.session_id,
        "user_id": user["id"],
        "role": "user",
        "content": data.message,
    }).execute()

    nlp = await run_nlp_pipeline(data.message)
    crisis = nlp["crisis_detected"]

    if crisis:
        reply = (
            "I notice you're going through an extremely difficult time right now. "
            "Your wellbeing is the most important thing. "
            "Please reach out for immediate support:\n\n"
            "**Emergency & Crisis Resources:**\n"
            "• **988 Suicide & Crisis Lifeline** — Call or text 988\n"
            "• **Crisis Text Line** — Text HOME to 741741\n"
            "• **Emergency Services** — Call 911 (US) or your local emergency number\n\n"
            "You are not alone, and there are people who care about you and want to help. "
            "Would you like me to help you find additional resources or support?"
        )
        preds = None
        recs = None
        sources = None
    else:
        rag = await retrieve_context(user["id"], data.message)
        preds_result = await generate_predictions(nlp, user["id"])
        preds = preds_result["predictions"]
        recs = preds_result["recommendations"]
        sources = rag.get("sources", [])
        context = rag.get("context", "")

        system_prompt = (
            "You are MindGuard, an AI wellness coach. You provide empathetic, "
            "evidence-based mental health support. Be conversational, warm, and concise (2-4 sentences). "
            "Use the NLP analysis and context to personalize your response. "
            "NEVER make a medical diagnosis. Always encourage professional help when appropriate."
        )

        context_info = ""
        if context:
            context_info = f"\n\nRelevant context for personalization:\n{context[:1500]}"
        if preds:
            context_info += (
                f"\n\nUser's current state from NLP analysis: "
                f"Wellness: {preds.get('wellness_score', 'N/A')}/10, "
                f"Stress: {preds.get('stress_level', 'N/A')}/10, "
                f"Mood: {preds.get('mood_trend', 'N/A')}, "
                f"Depression Risk: {preds.get('depression_risk', 'N/A')}, "
                f"Anxiety Risk: {preds.get('anxiety_risk', 'N/A')}"
            )

        user_prompt = (
            f"The user says: \"{data.message}\"\n"
            f"Their detected emotion is: {nlp['emotions']['primary']}, "
            f"Topics: {', '.join(nlp['topics'])}{context_info}"
        )

        ai_reply = await generate_chat_response(system_prompt, data.message, context)
        if ai_reply:
            reply = ai_reply
        else:
            reply = (
                f"Thank you for sharing that with me. I've analyzed your message and here's what I can see:\n\n"
                f"**Wellness Overview:**\n"
                f"• Wellness Score: {preds.get('wellness_score', 'N/A')}/10\n"
                f"• Stress Level: {preds.get('stress_level', 'N/A')}/10\n"
                f"• Mood Trend: {preds.get('mood_trend', 'N/A')}\n\n"
                f"**Risk Assessment:**\n"
                f"• Depression Risk: {preds.get('depression_risk', 'N/A')}\n"
                f"• Anxiety Risk: {preds.get('anxiety_risk', 'N/A')}\n"
                f"• Burnout Risk: {preds.get('burnout_risk', 'N/A')}\n\n"
                f"**Recommendation:**\n"
                f"{recs[0]['description'] if recs else 'Keep maintaining healthy habits.'}"
            )

    supabase.table("chat_messages").insert({
        "session_id": data.session_id,
        "user_id": user["id"],
        "role": "assistant",
        "content": reply,
        "metadata": {
            "nlp": nlp,
            "predictions": preds,
            "crisis_detected": crisis,
        },
    }).execute()

    supabase.table("chat_sessions") \
        .update({"updated_at": "now()"}) \
        .eq("id", data.session_id) \
        .execute()

    return ChatResponse(
        reply=reply,
        session_id=data.session_id,
        nlp_result=nlp,
        predictions=preds,
        recommendations=recs if not crisis else None,
        crisis_detected=crisis,
        sources=sources if not crisis else None,
    )
