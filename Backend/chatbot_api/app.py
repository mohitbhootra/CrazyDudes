"""
KAIROS Chatbot API - FastAPI Application
Port: 8001
Endpoints: Chat, Sentiment Analysis, Mood Tracking, Crisis Detection
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List

from models import (
    ChatRequest, ChatResponse, SentimentData, ConversationMessage,
    MoodRequest, MoodStatusResponse, SentimentTrendResponse, HealthCheckResponse
)
from sentiment_analyzer import analyzer
from database import db
from llm_engine import llm_engine


# ── FastAPI App Setup ─────────────────────────────────────────────────
app = FastAPI(
    title="KAIROS Chatbot API",
    description="Mental health chatbot API with sentiment analysis and mood tracking",
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
        "http://localhost:8000",      # Local testing
        "https://kairos.vercel.app",  # Production (if deployed)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Mood Mapping ──────────────────────────────────────────────────────
# Map detected emotions to clinical moods
MOOD_MAPPING = {
    "happy": {"display": "Happy", "clinical": "energized_positive"},
    "excited": {"display": "Excited", "clinical": "energized_positive"},
    "hopeful": {"display": "Hopeful", "clinical": "calm_content"},
    "calm": {"display": "Calm", "clinical": "calm_content"},
    "neutral": {"display": "Neutral", "clinical": "neutral_balanced"},
    "anxious": {"display": "Anxious", "clinical": "anxious_overwhelmed"},
    "sad": {"display": "Sad", "clinical": "sad_withdrawn"},
    "angry": {"display": "Frustrated", "clinical": "frustrated_irritable"},
    "frustrated": {"display": "Frustrated", "clinical": "frustrated_irritable"},
    "depressed": {"display": "Down", "clinical": "sad_withdrawn"},
}

CRISIS_RESOURCES = [
    "National Suicide Prevention Lifeline: 1-800-273-8255 (24/7, free, confidential)",
    "Crisis Text Line: Text HOME to 741741",
    "International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/",
    "NAMI Helpline: 1-800-950-NAMI (6264)",
]


# ── API Endpoints ─────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Health check endpoint with LLM status"""
    llm_status = llm_engine.get_provider_status()
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "llm_integration": {
            "groq_available": llm_status.get("groq_available", False),
            "gemini_available": llm_status.get("gemini_available", False),
            "active_provider": llm_status.get("active_provider"),
            "fallback_enabled": llm_status.get("fallback_enabled", True),
            "fallback_status": "using rule-based responses" if not (llm_status.get("groq_available") or llm_status.get("gemini_available")) else "LLM active"
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message and receive emotion-aware response
    
    Args:
        user_id: Unique user identifier
        message: User's message
        
    Returns:
        ChatResponse with reply, sentiment analysis, mood, and crisis detection
    """
    if not request.message or len(request.message.strip()) == 0:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    user_id = request.user_id
    message = request.message.strip()

    # Store user message
    db.add_message(user_id, "user", message)

    # Analyze sentiment and emotion
    sentiment_analysis = analyzer.analyze_sentiment(message)
    primary_emotion, emotion_confidence = analyzer.detect_emotion(message)
    polarity_str, polarity_score = analyzer.get_polarity(message)
    is_crisis = analyzer.detect_crisis(message)

    # Try to generate response using LLM first, fallback to rule-based
    response_text = None
    technique = "llm_generated"
    llm_used = False
    
    if llm_engine.is_llm_available():
        llm_response, success, error = llm_engine.generate_response(
            user_message=message,
            emotion=primary_emotion,
            polarity=polarity_str,
            system_context=f"User ID: {user_id}"
        )
        
        if success and llm_response:
            response_text = llm_response
            llm_used = True
        else:
            # LLM failed, try rule-based
            if error:
                print(f"LLM Error: {error}")
            response_text, technique = analyzer.get_mental_health_response(
                primary_emotion, polarity_str, message
            )
    else:
        # No LLM available, use rule-based responses
        response_text, technique = analyzer.get_mental_health_response(
            primary_emotion, polarity_str, message
        )

    # Determine mood
    mood_mapping = MOOD_MAPPING.get(
        primary_emotion,
        {"display": "Uncertain", "clinical": "uncertain"}
    )

    mood = mood_mapping["clinical"]
    display_mood = mood_mapping["display"]

    # Store mood and sentiment record
    db.set_mood(
        user_id,
        mood,
        source="conversation",
        confidence=emotion_confidence,
        metadata={
            "emotion": primary_emotion,
            "polarity": polarity_str,
            "message_length": len(message)
        }
    )

    db.add_sentiment_record(user_id, sentiment_analysis)

    # Store assistant response
    db.add_message(
        user_id, "assistant", response_text,
        metadata={
            "technique": technique,
            "emotion": primary_emotion,
            "polarity": polarity_str
        }
    )

    # Build response
    return ChatResponse(
        reply=response_text,
        follow_up="How does that feel? Is there anything else you'd like to talk about?" if not is_crisis else None,
        sentiment=SentimentData(
            detected_emotion=primary_emotion,
            polarity=polarity_str,
            polarity_score=polarity_score,
            confidence=emotion_confidence,
            intensity=analyzer.get_intensity(sentiment_analysis["emotion_scores"]),
            emotion_scores=sentiment_analysis["emotion_scores"]
        ),
        tracked_mood=mood,
        mood_source="conversation",
        technique_used=technique if technique != "crisis_intervention" else None,
        crisis_detected=is_crisis,
        crisis_resources=CRISIS_RESOURCES if is_crisis else None
    )


@app.get("/chat/history")
async def get_chat_history(user_id: str, limit: int = 50):
    """
    Get conversation history for a user
    
    Args:
        user_id: User identifier
        limit: Maximum number of messages to return (default 50)
        
    Returns:
        List of ConversationMessage objects
    """
    history = db.get_conversation_history(user_id, limit)
    
    return [
        ConversationMessage(
            role=msg["role"],
            content=msg["content"],
            timestamp=msg["timestamp"],
            metadata=msg.get("metadata", {})
        )
        for msg in history
    ]


@app.get("/chat/sentiment", response_model=SentimentTrendResponse)
async def get_sentiment_trend(user_id: str, days: int = 7):
    """
    Get sentiment trend analysis
    
    Args:
        user_id: User identifier
        days: Number of days to analyze (default 7)
        
    Returns:
        Sentiment trend with average polarity and dominant emotion
    """
    trend_data = db.get_sentiment_trend(user_id, days)

    if not trend_data or trend_data.get("records", 0) == 0:
        return SentimentTrendResponse(
            trend="no_data",
            average_polarity=0.5,
            recent_average=0.5,
            dominant_emotion="neutral",
            records=0
        )

    return SentimentTrendResponse(**trend_data)


@app.post("/chat/clear")
async def clear_chat(user_id: str):
    """
    Clear conversation history for a user
    
    Args:
        user_id: User identifier
        
    Returns:
        Success message
    """
    db.clear_conversation(user_id)
    return {"status": "success", "message": "Conversation cleared"}


@app.get("/mood/current", response_model=MoodStatusResponse)
async def get_current_mood(user_id: str):
    """
    Get current mood status
    
    Args:
        user_id: User identifier
        
    Returns:
        Current mood with confidence and description
    """
    mood_entry = db.get_current_mood(user_id)

    if not mood_entry:
        return MoodStatusResponse(
            mood="uncertain",
            clinical_mood="uncertain",
            confidence=0.0,
            source="none",
            description="No mood data available yet"
        )

    mood_name = mood_entry.get("mood", "uncertain")
    mood_mapping = MOOD_MAPPING.get(
        mood_name,
        {"display": "Uncertain", "clinical": "uncertain"}
    )

    # Map clinical mood to user-facing description
    mood_descriptions = {
        "energized_positive": "Feeling energized and positive",
        "calm_content": "Feeling calm and content",
        "neutral_balanced": "Feeling balanced and neutral",
        "anxious_overwhelmed": "Feeling anxious or overwhelmed",
        "sad_withdrawn": "Feeling sad or withdrawn",
        "frustrated_irritable": "Feeling frustrated or irritable",
        "uncertain": "Not sure about current mood",
    }

    clinical_mood = mood_mapping["clinical"]
    description = mood_descriptions.get(
        clinical_mood,
        "Current emotional state recorded"
    )

    return MoodStatusResponse(
        mood=mood_mapping["display"],
        clinical_mood=clinical_mood,
        confidence=mood_entry.get("confidence", 0.5),
        source=mood_entry.get("source", "conversation"),
        description=description
    )


@app.post("/mood/set")
async def set_mood(request: MoodRequest):
    """
    Manually set user's mood
    
    Args:
        user_id: User identifier
        mood: Mood string (happy, sad, anxious, calm, etc.)
        
    Returns:
        Success message
    """
    mood = request.mood.lower()

    if mood not in MOOD_MAPPING:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mood. Valid moods are: {', '.join(MOOD_MAPPING.keys())}"
        )

    db.set_mood(
        request.user_id,
        MOOD_MAPPING[mood]["clinical"],
        source="manual",
        confidence=0.8
    )

    return {
        "status": "success",
        "mood": MOOD_MAPPING[mood]["clinical"],
        "message": f"Mood set to {MOOD_MAPPING[mood]['display']}"
    }


@app.get("/stats")
async def get_user_stats(user_id: str):
    """Get user statistics"""
    stats = db.get_user_stats(user_id)
    
    if not stats:
        return {"status": "no_data", "user_id": user_id}
    
    return stats


@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "name": "KAIROS Chatbot API",
        "version": "1.0.0",
        "description": "Mental health chatbot with emotion detection and mood tracking",
        "endpoints": {
            "health": "GET /health",
            "chat": "POST /chat",
            "history": "GET /chat/history?user_id=",
            "sentiment_trend": "GET /chat/sentiment?user_id=",
            "clear_chat": "POST /chat/clear?user_id=",
            "current_mood": "GET /mood/current?user_id=",
            "set_mood": "POST /mood/set",
            "stats": "GET /stats?user_id=",
        },
        "port": 8001,
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )
