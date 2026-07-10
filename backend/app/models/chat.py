from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SessionCreate(BaseModel):
    title: str = "New Chat"


class SessionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    summary: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MessageCreate(BaseModel):
    session_id: str
    role: str = "user"
    content: str


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    metadata: Optional[dict] = None
    created_at: Optional[datetime] = None


class ChatRequest(BaseModel):
    session_id: str
    message: str
    include_context: bool = True


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    nlp_result: Optional[dict] = None
    predictions: Optional[dict] = None
    recommendations: Optional[list[dict]] = None
    crisis_detected: bool = False
    sources: Optional[list[dict]] = None
