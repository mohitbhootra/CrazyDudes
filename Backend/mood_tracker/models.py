"""
Pydantic models for Mood Tracker API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Request Models
class MoodAssessmentRequest(BaseModel):
    """Mood assessment request from frontend"""
    user_id: str
    responses: Dict[str, str]  # question_id -> option_id mapping
    metadata: Optional[Dict[str, Any]] = None


class MoodLogRequest(BaseModel):
    """Manual mood logging"""
    user_id: str
    mood: str
    intensity: int = Field(..., ge=1, le=10, description="1-10 intensity scale")
    context: Optional[str] = None


class MoodCheckInRequest(BaseModel):
    """Quick mood check-in"""
    user_id: str
    emotion: str
    notes: Optional[str] = None


# Response Models
class MoodClassificationResponse(BaseModel):
    """Response from ML mood classification"""
    user_id: str
    predicted_mood: str
    clinical_mood: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    severity: Optional[int] = None
    recommendations: List[str]
    timestamp: datetime


class MoodTrendResponse(BaseModel):
    """Historical mood trend data"""
    user_id: str
    time_period: str  # "daily", "weekly", "monthly"
    trend_direction: str  # "improving", "declining", "stable"
    average_mood: str
    dominant_emotion: str
    emotion_distribution: Dict[str, float]
    data_points: int
    recommendations: List[str]


class MoodStatsResponse(BaseModel):
    """Mood statistics for a user"""
    user_id: str
    total_assessments: int
    average_mood: str
    most_common_mood: str
    mood_variety: float  # 0-1, how varied moods are
    last_assessment: datetime
    streak_days: int
    weekly_average_intensity: float


class MoodHistoryResponse(BaseModel):
    """Historical mood records"""
    user_id: str
    records: List[Dict[str, Any]]
    total_records: int
    date_range: Dict[str, datetime]


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    ml_models_loaded: bool


class AssessmentQuestionResponse(BaseModel):
    """Assessment question response"""
    question_id: str
    category: str
    question_text: str
    question_type: str  # "multiple_choice", "scale", "open_text"
    options: List[Dict[str, Any]]


class AssessmentSessionResponse(BaseModel):
    """Assessment session response"""
    session_id: str
    user_id: str
    total_questions: int
    questions: List[AssessmentQuestionResponse]
    estimated_duration_minutes: int


class MoodUpdateResponse(BaseModel):
    """Response when mood is updated"""
    user_id: str
    recorded_mood: str
    timestamp: datetime
    message: str
