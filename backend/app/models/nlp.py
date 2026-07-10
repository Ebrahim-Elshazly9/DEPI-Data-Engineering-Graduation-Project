from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NLPResult(BaseModel):
    sentiment_score: float
    sentiment_label: str
    primary_emotion: str
    secondary_emotions: list[str]
    stress_level: float
    anxiety_indicators: float
    depression_indicators: float
    burnout_indicators: float
    sleep_issues: bool
    social_isolation: bool
    confidence_level: float
    urgency_score: float
    keywords: list[str]
    topics: list[str]
    entities: list[str]
    user_goals: list[str]
    behavioral_patterns: list[str]


class PredictionResponse(BaseModel):
    id: Optional[str] = None
    user_id: str
    type: str
    score: float
    confidence: float
    reasoning: Optional[str] = None
    risk_category: str
    recommendations: list[str] = []
    created_at: Optional[datetime] = None


class RecommendationResponse(BaseModel):
    id: Optional[str] = None
    user_id: str
    category: str
    title: str
    description: Optional[str] = None
    priority: int = 5
    estimated_time: Optional[str] = None
    difficulty: Optional[str] = None
    reason: Optional[str] = None
    expected_benefit: Optional[str] = None
    completed: bool = False


class AISettings(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 2048
