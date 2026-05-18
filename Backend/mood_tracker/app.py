"""
KAIROS Mood Tracker API - FastAPI Application
Port: 8000
Endpoints: Mood assessment, tracking, analytics, and trend analysis
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List

from models import (
    MoodAssessmentRequest, MoodLogRequest, MoodCheckInRequest,
    MoodClassificationResponse, MoodTrendResponse, MoodStatsResponse,
    MoodHistoryResponse, HealthCheckResponse, AssessmentSessionResponse,
    MoodUpdateResponse
)
from ml_models import mood_classifier, trend_analyzer
from database import db


# ── FastAPI App Setup ─────────────────────────────────────────────────
app = FastAPI(
    title="KAIROS Mood Tracker API",
    description="Mood tracking and analytics API with ML-powered classification",
    version="1.0.0"
)

# ── CORS Configuration ────────────────────────────────────────────────
# Allow frontend to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4173",      # Dev server
        "http://127.0.0.1:4173",      # Dev server (127.0.0.1)
        "http://localhost:5173",      # Alternative dev port
        "http://localhost:3000",      # Alternative dev port
        "http://localhost:8080",      # Alternative dev port
        "http://localhost:8001",      # Chatbot API
        "https://kairos.vercel.app",  # Production (if deployed)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Train the model on startup
@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    mood_classifier.train()
    print("✅ ML models trained and ready")


# ── Health Check ──────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="ok",
        timestamp=datetime.now(),
        version="1.0.0",
        ml_models_loaded=mood_classifier.is_trained
    )


# ── Mood Recording & Check-in ─────────────────────────────────────────

@app.post("/mood/checkin", response_model=MoodUpdateResponse)
async def quick_mood_checkin(request: MoodCheckInRequest):
    """
    Quick mood check-in (simple emotion selection)
    
    Args:
        user_id: User identifier
        emotion: Emotion to log
        notes: Optional notes
        
    Returns:
        MoodUpdateResponse with recorded mood
    """
    if not request.emotion:
        raise HTTPException(status_code=400, detail="Emotion cannot be empty")
    
    # Map emotion to clinical mood
    emotion_to_mood = {
        "happy": "energized_positive",
        "excited": "energized_positive",
        "calm": "calm_content",
        "neutral": "neutral_balanced",
        "anxious": "anxious_overwhelmed",
        "sad": "sad_withdrawn",
        "angry": "frustrated_irritable",
    }
    
    mood = emotion_to_mood.get(request.emotion.lower(), "neutral_balanced")
    
    # Record mood
    record = db.record_mood(
        user_id=request.user_id,
        mood=mood,
        context=request.notes
    )
    
    return MoodUpdateResponse(
        user_id=request.user_id,
        recorded_mood=mood,
        timestamp=record.timestamp,
        message=f"Mood '{request.emotion}' recorded successfully"
    )


@app.post("/mood/log", response_model=MoodUpdateResponse)
async def log_mood(request: MoodLogRequest):
    """
    Log mood with intensity
    
    Args:
        user_id: User identifier
        mood: Mood category
        intensity: 1-10 intensity scale
        context: Optional context
        
    Returns:
        MoodUpdateResponse
    """
    if not request.mood:
        raise HTTPException(status_code=400, detail="Mood cannot be empty")
    
    # Record mood with intensity
    record = db.record_mood(
        user_id=request.user_id,
        mood=request.mood,
        intensity=request.intensity,
        context=request.context
    )
    
    return MoodUpdateResponse(
        user_id=request.user_id,
        recorded_mood=request.mood,
        timestamp=record.timestamp,
        message=f"Mood logged with intensity {request.intensity}/10"
    )


# ── Assessment ────────────────────────────────────────────────────────

@app.post("/assessment/start", response_model=AssessmentSessionResponse)
async def start_assessment(user_id: str):
    """
    Start a mood assessment session
    
    Args:
        user_id: User identifier
        
    Returns:
        Assessment session with questions
    """
    # Create assessment questions
    questions_data = {
        "q1": {
            "id": "q1",
            "category": "mood",
            "text": "How would you rate your current mood?",
            "type": "scale",
            "options": [
                {"id": "1", "label": "Very Bad"},
                {"id": "2", "label": "Bad"},
                {"id": "3", "label": "Neutral"},
                {"id": "4", "label": "Good"},
                {"id": "5", "label": "Excellent"}
            ]
        },
        "q2": {
            "id": "q2",
            "category": "emotions",
            "text": "What emotions are you experiencing?",
            "type": "multiple_choice",
            "options": [
                {"id": "happy", "label": "Happy"},
                {"id": "anxious", "label": "Anxious"},
                {"id": "sad", "label": "Sad"},
                {"id": "angry", "label": "Angry"},
                {"id": "calm", "label": "Calm"},
                {"id": "neutral", "label": "Neutral"}
            ]
        },
        "q3": {
            "id": "q3",
            "category": "energy",
            "text": "What is your current energy level?",
            "type": "scale",
            "options": [
                {"id": "1", "label": "Very Low"},
                {"id": "2", "label": "Low"},
                {"id": "3", "label": "Moderate"},
                {"id": "4", "label": "High"},
                {"id": "5", "label": "Very High"}
            ]
        }
    }
    
    # Create session
    session_id = db.create_assessment_session(user_id, questions_data)
    
    return AssessmentSessionResponse(
        session_id=session_id,
        user_id=user_id,
        total_questions=len(questions_data),
        questions=[],
        estimated_duration_minutes=5
    )


@app.post("/assessment/submit")
async def submit_assessment(user_id: str, session_id: str, responses: dict):
    """
    Submit assessment responses
    
    Args:
        user_id: User identifier
        session_id: Assessment session ID
        responses: User's responses to questions
        
    Returns:
        Mood classification results
    """
    session = db.get_assessment_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Extract emotions from responses
    emotions = responses.get("emotions", [])
    mood_text = " ".join(emotions) if emotions else "neutral"
    
    # Classify mood using ML
    predicted_mood, confidence, scores = mood_classifier.predict_with_confidence(mood_text)
    
    # Record mood
    db.record_mood(
        user_id=user_id,
        mood=predicted_mood,
        confidence=confidence,
        context="assessment"
    )
    
    # Complete session
    db.complete_assessment_session(session_id, {
        "predicted_mood": predicted_mood,
        "confidence": confidence
    })
    
    return {
        "session_id": session_id,
        "predicted_mood": predicted_mood,
        "confidence": confidence,
        "all_scores": scores,
        "message": "Assessment completed"
    }


# ── Mood History & Analytics ──────────────────────────────────────────

@app.get("/mood/history", response_model=MoodHistoryResponse)
async def get_mood_history(user_id: str, days: int = 30, limit: int = 100):
    """
    Get mood history for user
    
    Args:
        user_id: User identifier
        days: Number of days to retrieve (default 30)
        limit: Maximum records to return
        
    Returns:
        MoodHistoryResponse with mood records
    """
    history = db.get_mood_history(user_id, limit=limit, days=days)
    
    records = [
        {
            "timestamp": r.timestamp.isoformat(),
            "mood": r.mood,
            "intensity": r.intensity,
            "context": r.context,
            "confidence": r.confidence
        }
        for r in history
    ]
    
    date_range = {
        "start": history[0].timestamp.isoformat() if history else None,
        "end": history[-1].timestamp.isoformat() if history else None
    }
    
    return MoodHistoryResponse(
        user_id=user_id,
        records=records,
        total_records=len(records),
        date_range=date_range
    )


@app.get("/mood/current")
async def get_current_mood(user_id: str):
    """Get user's current mood"""
    user = db.get_or_create_user(user_id)
    
    if not user.current_mood:
        return {
            "user_id": user_id,
            "current_mood": None,
            "message": "No mood recorded yet"
        }
    
    return {
        "user_id": user_id,
        "current_mood": user.current_mood,
        "last_assessment": user.last_assessment.isoformat() if user.last_assessment else None
    }


@app.get("/mood/stats", response_model=MoodStatsResponse)
async def get_mood_statistics(user_id: str, days: int = 30):
    """
    Get mood statistics for user
    
    Args:
        user_id: User identifier
        days: Number of days to analyze (default 30)
        
    Returns:
        MoodStatsResponse with statistics
    """
    user = db.get_or_create_user(user_id)
    stats = db.get_mood_statistics(user_id, days=days)
    
    if not stats or stats.get("total_records", 0) == 0:
        return MoodStatsResponse(
            user_id=user_id,
            total_assessments=0,
            average_mood="neutral_balanced",
            most_common_mood="neutral_balanced",
            mood_variety=0.0,
            last_assessment=None,
            streak_days=0,
            weekly_average_intensity=0.0
        )
    
    return MoodStatsResponse(
        user_id=user_id,
        total_assessments=stats.get("total_records", 0),
        average_mood=stats.get("most_common_mood", "neutral_balanced"),
        most_common_mood=stats.get("most_common_mood", "neutral_balanced"),
        mood_variety=0.5,
        last_assessment=user.last_assessment,
        streak_days=stats.get("streak_days", 0),
        weekly_average_intensity=stats.get("average_intensity", 0.0) or 0.0
    )


@app.get("/mood/trends", response_model=MoodTrendResponse)
async def get_mood_trends(user_id: str, period: str = "weekly"):
    """
    Get mood trends for user
    
    Args:
        user_id: User identifier
        period: Time period (daily, weekly, monthly)
        
    Returns:
        MoodTrendResponse with trend analysis
    """
    # Get mood history
    if period == "daily":
        history = db.get_mood_history(user_id, days=1)
    elif period == "monthly":
        history = db.get_mood_history(user_id, days=30)
    else:  # weekly
        history = db.get_mood_history(user_id, days=7)
    
    # Convert to dict format for analyzer
    mood_records = [
        {"mood": r.mood, "timestamp": r.timestamp}
        for r in history
    ]
    
    # Analyze trends
    trend_data = trend_analyzer.calculate_trend(mood_records)
    stats = trend_analyzer.calculate_statistics(mood_records)
    
    # Get emotion distribution
    moods = [r["mood"] for r in mood_records]
    emotion_dist = {}
    for mood in moods:
        emotion_dist[mood] = emotion_dist.get(mood, 0) + 1
    
    return MoodTrendResponse(
        user_id=user_id,
        time_period=period,
        trend_direction=trend_data.get("trend_direction", "stable"),
        average_mood=trend_data.get("average_mood", "neutral_balanced"),
        dominant_emotion=stats.get("most_common", "neutral_balanced"),
        emotion_distribution=emotion_dist if emotion_dist else {"neutral_balanced": 1},
        data_points=len(mood_records),
        recommendations=trend_data.get("recommendations", [])
    )


# ── Data Management ────────────────────────────────────────────────────

@app.get("/user/export")
async def export_user_data(user_id: str):
    """Export all user data (GDPR compliance)"""
    data = db.export_user_data(user_id)
    
    if not data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return data


@app.delete("/user/delete")
async def delete_user_data(user_id: str):
    """Delete all user data (GDPR compliance)"""
    success = db.delete_user_data(user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User data deleted successfully"}


# ── Testing Endpoints ─────────────────────────────────────────────────

@app.post("/test/classify")
async def test_mood_classification(text: str):
    """Test mood classification with custom text"""
    predicted_mood, confidence, scores = mood_classifier.predict_with_confidence(text)
    
    return {
        "input_text": text,
        "predicted_mood": predicted_mood,
        "confidence": confidence,
        "all_scores": scores
    }
