"""
Pydantic models for Chatbot API requests and responses
Matches frontend TypeScript interfaces exactly
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Request Models
class ChatRequest(BaseModel):
    """Chat message request from frontend"""
    user_id: str
    message: str


class AssessmentResponse(BaseModel):
    """User's response to an assessment question"""
    question_id: str
    option_id: str
    response_time_ms: int


class MoodRequest(BaseModel):
    """Manual mood setting request"""
    user_id: str
    mood: str


# Response Models - Sentiment Analysis
class SentimentData(BaseModel):
    """Sentiment analysis data for a single message"""
    detected_emotion: str = Field(..., description="Detected emotion (happy, sad, angry, etc.)")
    polarity: str = Field(..., description="Polarity: positive, negative, neutral")
    polarity_score: float = Field(..., ge=0.0, le=1.0, description="Score 0.0-1.0")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence 0.0-1.0")
    intensity: str = Field(..., description="Intensity: low, medium, high")
    emotion_scores: Dict[str, float] = Field(..., description="Scores for each emotion")


# Response Models - Main Responses
class ChatResponse(BaseModel):
    """Response to a chat message"""
    reply: str = Field(..., description="AI-generated response")
    follow_up: Optional[str] = Field(None, description="Optional follow-up question")
    sentiment: SentimentData = Field(..., description="Sentiment analysis")
    tracked_mood: str = Field(..., description="Detected user mood")
    mood_source: str = Field(..., description="Source of mood: conversation, explicit, etc.")
    technique_used: Optional[str] = Field(None, description="Mental health technique applied")
    crisis_detected: bool = Field(False, description="Whether crisis was detected")
    crisis_resources: Optional[List[str]] = Field(None, description="Resources if crisis detected")


class ConversationMessage(BaseModel):
    """A message in conversation history"""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str
    timestamp: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SentimentTrendResponse(BaseModel):
    """Sentiment trend analysis"""
    trend: str = Field(..., description="Trend: improving, declining, stable")
    average_polarity: float = Field(..., ge=0.0, le=1.0)
    recent_average: float = Field(..., ge=0.0, le=1.0)
    dominant_emotion: str
    records: int = Field(..., description="Number of messages analyzed")


class MoodStatusResponse(BaseModel):
    """Current mood status"""
    mood: str = Field(..., description="User-facing mood name")
    clinical_mood: str = Field(..., description="Clinical mood category")
    confidence: float = Field(..., ge=0.0, le=1.0)
    source: str = Field(..., description="How mood was determined")
    description: str = Field(..., description="Description of current mood")


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="ok", description="API status")
    timestamp: str
    version: str = Field(default="1.0.0")


# Assessment Models (if needed for future integration)
class AssessmentQuestion(BaseModel):
    """Single assessment question"""
    question_id: str
    category: str
    question_text: str
    question_type: str
    options: List[Dict[str, Any]]


class AssessmentStartResponse(BaseModel):
    """Response when starting assessment"""
    session_id: str
    questions: List[AssessmentQuestion]
    total_questions: int


class MoodResultResponse(BaseModel):
    """Results after mood assessment"""
    session_id: str
    user_facing_mood: str
    mood_description: str
    confidence: float
    content_tags: Optional[List[str]] = None
    severity: Optional[int] = None
    requires_monitoring: Optional[bool] = None
    refresh_minutes: int = 30
    validation_message: Optional[str] = None
    next_steps: Optional[str] = None
