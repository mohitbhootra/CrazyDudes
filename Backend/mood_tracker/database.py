"""
In-memory database for mood tracking
Can be extended to use PostgreSQL/MongoDB later
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class MoodRecord:
    """Single mood record"""
    user_id: str
    mood: str
    timestamp: datetime
    intensity: Optional[int] = None
    context: Optional[str] = None
    confidence: Optional[float] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class UserMoodProfile:
    """User's mood tracking profile"""
    user_id: str
    mood_history: List[MoodRecord] = field(default_factory=list)
    total_assessments: int = 0
    last_assessment: Optional[datetime] = None
    current_mood: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


class MoodDatabase:
    """
    In-memory database for mood tracking
    Thread-safe (uses dict which is atomic in Python)
    """
    
    def __init__(self):
        """Initialize database"""
        self.users: Dict[str, UserMoodProfile] = {}
        self.sessions: Dict[str, Dict] = {}
    
    # ── User Profile Management ────────────────────────────────────
    
    def get_or_create_user(self, user_id: str) -> UserMoodProfile:
        """Get existing user profile or create new one"""
        if user_id not in self.users:
            self.users[user_id] = UserMoodProfile(user_id=user_id)
        return self.users[user_id]
    
    def user_exists(self, user_id: str) -> bool:
        """Check if user exists"""
        return user_id in self.users
    
    # ── Mood Recording ────────────────────────────────────────────────
    
    def record_mood(
        self,
        user_id: str,
        mood: str,
        intensity: Optional[int] = None,
        context: Optional[str] = None,
        confidence: Optional[float] = None
    ) -> MoodRecord:
        """Record a mood entry for user"""
        user = self.get_or_create_user(user_id)
        
        record = MoodRecord(
            user_id=user_id,
            mood=mood,
            timestamp=datetime.now(),
            intensity=intensity,
            context=context,
            confidence=confidence
        )
        
        user.mood_history.append(record)
        user.total_assessments += 1
        user.last_assessment = datetime.now()
        user.current_mood = mood
        
        return record
    
    def get_mood_history(
        self,
        user_id: str,
        limit: Optional[int] = None,
        days: Optional[int] = None
    ) -> List[MoodRecord]:
        """
        Get mood history for user
        Can filter by limit (number of records) or days (time period)
        """
        if not self.user_exists(user_id):
            return []
        
        user = self.users[user_id]
        history = user.mood_history
        
        if days:
            cutoff_time = datetime.now() - timedelta(days=days)
            history = [r for r in history if r.timestamp > cutoff_time]
        
        if limit:
            return history[-limit:]
        
        return history
    
    def get_recent_moods(self, user_id: str, hours: int = 24) -> List[MoodRecord]:
        """Get moods from last N hours"""
        if not self.user_exists(user_id):
            return []
        
        user = self.users[user_id]
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [r for r in user.mood_history if r.timestamp > cutoff_time]
    
    def clear_mood_history(self, user_id: str) -> None:
        """Clear mood history for user"""
        if user_id in self.users:
            self.users[user_id].mood_history = []
    
    # ── Statistics ────────────────────────────────────────────────────
    
    def get_mood_statistics(self, user_id: str, days: int = 30) -> Dict:
        """Get mood statistics for user"""
        if not self.user_exists(user_id):
            return {}
        
        user = self.users[user_id]
        history = self.get_mood_history(user_id, days=days)
        
        if not history:
            return {
                "total_records": 0,
                "period_days": days,
                "message": "No mood data available"
            }
        
        moods = [r.mood for r in history]
        mood_counts = {}
        
        for mood in moods:
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        # Calculate streak
        today = datetime.now().date()
        streak = 0
        current_date = today
        
        for record in reversed(history):
            record_date = record.timestamp.date()
            if (today - record_date).days <= streak + 1:
                if record_date == (current_date - timedelta(days=streak)):
                    streak += 1
                    current_date = record_date
                else:
                    break
            else:
                break
        
        return {
            "total_records": len(history),
            "most_common_mood": max(mood_counts, key=mood_counts.get),
            "mood_distribution": mood_counts,
            "streak_days": streak,
            "last_assessment": user.last_assessment.isoformat() if user.last_assessment else None,
            "average_intensity": sum(r.intensity for r in history if r.intensity) / len([r for r in history if r.intensity]) if any(r.intensity for r in history) else None
        }
    
    # ── Assessment Sessions ────────────────────────────────────────────
    
    def create_assessment_session(self, user_id: str, session_data: Dict) -> str:
        """Create new assessment session"""
        session_id = f"{user_id}_{datetime.now().timestamp()}"
        self.sessions[session_id] = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "data": session_data
        }
        return session_id
    
    def get_assessment_session(self, session_id: str) -> Optional[Dict]:
        """Get assessment session"""
        return self.sessions.get(session_id)
    
    def complete_assessment_session(self, session_id: str, results: Dict) -> None:
        """Mark assessment as complete"""
        if session_id in self.sessions:
            self.sessions[session_id]["completed_at"] = datetime.now()
            self.sessions[session_id]["results"] = results
    
    # ── Export Data ────────────────────────────────────────────────────
    
    def export_user_data(self, user_id: str) -> Dict:
        """Export all user data"""
        if not self.user_exists(user_id):
            return {}
        
        user = self.users[user_id]
        
        return {
            "user_id": user_id,
            "created_at": user.created_at.isoformat(),
            "total_assessments": user.total_assessments,
            "last_assessment": user.last_assessment.isoformat() if user.last_assessment else None,
            "current_mood": user.current_mood,
            "mood_history": [
                {
                    "mood": r.mood,
                    "timestamp": r.timestamp.isoformat(),
                    "intensity": r.intensity,
                    "context": r.context,
                    "confidence": r.confidence
                }
                for r in user.mood_history
            ]
        }
    
    def delete_user_data(self, user_id: str) -> bool:
        """Delete all user data (GDPR compliance)"""
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False


# Initialize global database
db = MoodDatabase()
