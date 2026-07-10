from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class UserProfile(BaseModel):
    id: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


class MoodCreate(BaseModel):
    mood_score: int
    mood_label: Optional[str] = None
    note: Optional[str] = None


class MoodEntry(BaseModel):
    id: str
    user_id: str
    mood_score: int
    mood_label: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime
