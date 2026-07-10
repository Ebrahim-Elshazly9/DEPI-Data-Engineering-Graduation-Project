from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AssessmentQuestion(BaseModel):
    id: str
    text: str
    type: str = "scale"
    category: Optional[str] = None
    options: Optional[list[dict]] = None


class AssessmentDefinition(BaseModel):
    id: str
    type: str
    title: str
    description: str
    icon: str
    questions: list[AssessmentQuestion]
    scoring_guide: list[dict]
    estimated_minutes: int


class AssessmentCreate(BaseModel):
    type: str
    title: str
    answers: dict
    score: int
    max_score: int
    severity: str
    label: str
    status: str = "completed"


class AssessmentAnswer(BaseModel):
    question_id: str
    value: Optional[float] = None
    text_value: Optional[str] = None


class AssessmentResponse(BaseModel):
    id: str
    patient_id: str
    type: Optional[str] = None
    title: Optional[str] = None
    score: Optional[int] = None
    max_score: Optional[int] = None
    severity: Optional[str] = None
    label: Optional[str] = None
    answers: Optional[dict] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None


class AssessmentReportResponse(BaseModel):
    id: str
    assessment_id: str
    user_id: str
    type: str
    score: float
    risk_category: Optional[str] = None
    predicted_state: Optional[str] = None
    confidence_score: Optional[float] = None
    emotions_detected: list[str] = []
    topics_detected: list[str] = []
    ai_summary: Optional[str] = None
    recommendations: list[str] = []
    suggested_activities: list[str] = []
    suggested_breathing: Optional[str] = None
    suggested_journal_prompt: Optional[str] = None
    suggested_goals: list[str] = []
    follow_up_date: Optional[datetime] = None
    doctor_notes: Optional[str] = None
    report_pdf_url: Optional[str] = None
    created_at: Optional[datetime] = None


class AssessmentType:
    PHQ9 = "phq-9"
    GAD7 = "gad-7"
    PSS = "pss"
    MOOD = "mood"
    SLEEP = "sleep"
    BURNOUT = "burnout"
    LIFESTYLE = "lifestyle"
    DAILY_WELLNESS = "daily-wellness"


SCALE_OPTIONS = [
    {"label": "Not at all", "value": 0},
    {"label": "Several days", "value": 1},
    {"label": "More than half the days", "value": 2},
    {"label": "Nearly every day", "value": 3},
]

ASSESSMENTS: dict[str, AssessmentDefinition] = {
    "phq-9": AssessmentDefinition(
        id="phq-9",
        type="phq-9",
        title="PHQ-9",
        description="Patient Health Questionnaire for depression screening",
        icon="heart",
        questions=[
            AssessmentQuestion(id="phq-1", text="Little interest or pleasure in doing things", category="depression"),
            AssessmentQuestion(id="phq-2", text="Feeling down, depressed, or hopeless", category="depression"),
            AssessmentQuestion(id="phq-3", text="Trouble falling or staying asleep, or sleeping too much", category="sleep"),
            AssessmentQuestion(id="phq-4", text="Feeling tired or having little energy", category="energy"),
            AssessmentQuestion(id="phq-5", text="Poor appetite or overeating", category="appetite"),
            AssessmentQuestion(id="phq-6", text="Feeling bad about yourself — or that you are a failure", category="self-worth"),
            AssessmentQuestion(id="phq-7", text="Trouble concentrating on things", category="cognitive"),
            AssessmentQuestion(id="phq-8", text="Moving or speaking slowly, or the opposite — being fidgety", category="psychomotor"),
            AssessmentQuestion(id="phq-9", text="Thoughts that you would be better off dead or hurting yourself", category="suicidal"),
        ],
        scoring_guide=[
            {"range": [0, 4], "label": "Minimal", "severity": "none"},
            {"range": [5, 9], "label": "Mild", "severity": "low"},
            {"range": [10, 14], "label": "Moderate", "severity": "medium"},
            {"range": [15, 19], "label": "Moderately Severe", "severity": "high"},
            {"range": [20, 27], "label": "Severe", "severity": "critical"},
        ],
        estimated_minutes=5,
    ),
    "gad-7": AssessmentDefinition(
        id="gad-7",
        type="gad-7",
        title="GAD-7",
        description="Generalized Anxiety Disorder assessment",
        icon="activity",
        questions=[
            AssessmentQuestion(id="gad-1", text="Feeling nervous, anxious, or on edge", category="anxiety"),
            AssessmentQuestion(id="gad-2", text="Not being able to stop or control worrying", category="anxiety"),
            AssessmentQuestion(id="gad-3", text="Worrying too much about different things", category="anxiety"),
            AssessmentQuestion(id="gad-4", text="Trouble relaxing", category="anxiety"),
            AssessmentQuestion(id="gad-5", text="Being so restless that it is hard to sit still", category="anxiety"),
            AssessmentQuestion(id="gad-6", text="Becoming easily annoyed or irritable", category="irritability"),
            AssessmentQuestion(id="gad-7", text="Feeling afraid as if something awful might happen", category="fear"),
        ],
        scoring_guide=[
            {"range": [0, 4], "label": "Minimal", "severity": "none"},
            {"range": [5, 9], "label": "Mild", "severity": "low"},
            {"range": [10, 14], "label": "Moderate", "severity": "medium"},
            {"range": [15, 21], "label": "Severe", "severity": "high"},
        ],
        estimated_minutes=3,
    ),
}
