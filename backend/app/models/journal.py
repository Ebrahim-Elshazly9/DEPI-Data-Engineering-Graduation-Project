from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class JournalEntryCreate(BaseModel):
    title: Optional[str] = None
    content: str
    mood: Optional[str] = None
    mood_score: Optional[int] = None
    tags: list[str] = []


class JournalEntryResponse(BaseModel):
    id: str
    user_id: str
    title: Optional[str] = None
    content: str
    mood: Optional[str] = None
    mood_score: Optional[int] = None
    tags: list[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
