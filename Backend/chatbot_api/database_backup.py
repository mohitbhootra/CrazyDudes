"""
In-memory database for storing user conversations and mood data
Can be extended to use PostgreSQL/MongoDB later
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import json


@dataclass
class UserSession:
    """Represents a user's session and conversation history"""
    user_id: str
    conversation_history: List[Dict] = field(default_factory=list)
    mood_history: List[Dict] = field(default_factory=list)
    current_mood: Optional[str] = None
    last_message_time: Optional[datetime] = None
    session_created: datetime = field(default_factory=datetime.now)
    total_messages: int = 0


class InMemoryDatabase:
    """
    MongoDB database for chat conversations and mood tracking
    Persistent storage with MongoDB + fallback to in-memory
    """

    def __init__(self):
        """Initialize MongoDB connection"""
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("MONGODB_DB", "healthhack_chatbot")
        
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.users_collection = self.db["users"]
            self.conversations_collection = self.db["conversations"]
            self.moods_collection = self.db["moods"]
            self.connected = True
            print("✅ MongoDB connected successfully")
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            print(f"⚠️ MongoDB connection failed: {e}")
            print("⚠️ Using fallback in-memory storage")
            self.connected = False
            # Fallback to in-memory
            self.users: Dict[str, UserSession] = {}
        
        self.sessions_timeout_minutes = 30  # Session timeout

    # ── User Session Management ────────────────────────────────────
    
    def get_or_create_user(self, user_id: str) -> UserSession:
        """Get existing user session or create new one"""
        if self.connected:
            user_doc = self.users_collection.find_one({"user_id": user_id})
            if user_doc:
                # Reconstruct UserSession from MongoDB document
                session = UserSession(
                    user_id=user_id,
                    conversation_history=user_doc.get("conversation_history", []),
                    mood_history=user_doc.get("mood_history", []),
                    current_mood=user_doc.get("current_mood"),
                    last_message_time=user_doc.get("last_message_time"),
                    session_created=user_doc.get("session_created", datetime.now()),
                    total_messages=user_doc.get("total_messages", 0)
                )
                return session
            else:
                session = UserSession(user_id=user_id)
                self.users_collection.insert_one({
                    "user_id": user_id,
                    "conversation_history": [],
                    "mood_history": [],
                    "current_mood": None,
                    "last_message_time": None,
                    "session_created": datetime.now(),
                    "total_messages": 0
                })
                return session
        else:
            if user_id not in self.users:
                self.users[user_id] = UserSession(user_id=user_id)
            return self.users[user_id]

    def user_exists(self, user_id: str) -> bool:
        """Check if user exists"""
        if self.connected:
            return self.users_collection.find_one({"user_id": user_id}) is not None
        else:
            return user_id in self.users
        self,
        user_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """Add message to conversation history"""
        user = self.get_or_create_user(user_id)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        user.conversation_history.append(message)
        user.last_message_time = datetime.now()
        user.total_messages += 1

    def get_conversation_history(
        self,
        user_id: str,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Get conversation history for user"""
        if not self.user_exists(user_id):
            return []

        user = self.users[user_id]
        history = user.conversation_history

        if limit:
            return history[-limit:]
        return history

    def clear_conversation(self, user_id: str) -> None:
        """Clear conversation history for user"""
        if user_id in self.users:
            self.users[user_id].conversation_history = []

    def get_recent_messages(self, user_id: str, minutes: int = 60) -> List[Dict]:
        """Get messages from last N minutes"""
        if not self.user_exists(user_id):
            return []

        user = self.users[user_id]
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        recent = [
            msg for msg in user.conversation_history
            if datetime.fromisoformat(msg["timestamp"]) > cutoff_time
        ]
        
        return recent

    # ── Mood Tracking ──────────────────────────────────────────────
    
    def set_mood(
        self,
        user_id: str,
        mood: str,
        source: str = "conversation",
        confidence: float = 0.5,
        metadata: Optional[Dict] = None
    ) -> None:
        """Record mood entry"""
        user = self.get_or_create_user(user_id)
        
        mood_entry = {
            "mood": mood,
            "source": source,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        user.mood_history.append(mood_entry)
        user.current_mood = mood

    def get_current_mood(self, user_id: str) -> Optional[Dict]:
        """Get user's current mood"""
        if not self.user_exists(user_id):
            return None

        user = self.users[user_id]
        
        if not user.mood_history:
            return None

        latest_mood = user.mood_history[-1]
        return latest_mood

    def get_mood_history(self, user_id: str, days: int = 7) -> List[Dict]:
        """Get mood history for last N days"""
        if not self.user_exists(user_id):
            return []

        user = self.users[user_id]
        cutoff_time = datetime.now() - timedelta(days=days)
        
        history = [
            mood for mood in user.mood_history
            if datetime.fromisoformat(mood["timestamp"]) > cutoff_time
        ]
        
        return history

    def get_mood_stats(self, user_id: str) -> Dict:
        """Get mood statistics"""
        if not self.user_exists(user_id):
            return {}

        user = self.users[user_id]
        mood_history = user.mood_history

        if not mood_history:
            return {
                "total_entries": 0,
                "most_common_mood": None,
                "mood_trend": "no_data"
            }

        # Count moods
        mood_counts = defaultdict(int)
        for entry in mood_history:
            mood_counts[entry["mood"]] += 1

        most_common = max(mood_counts, key=mood_counts.get)
        total = len(mood_history)

        # Determine trend
        if total >= 2:
            recent = mood_history[-5:]
            older = mood_history[:-5]
            
            # Simple polarity analysis
            positive_moods = ["happy", "calm", "excited", "hopeful", "energized"]
            recent_positive = sum(
                1 for m in recent if m["mood"] in positive_moods
            )
            older_positive = sum(
                1 for m in older if m["mood"] in positive_moods
            ) / max(1, len(older))

            if recent_positive > older_positive:
                trend = "improving"
            elif recent_positive < older_positive:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "total_entries": total,
            "most_common_mood": most_common,
            "mood_counts": dict(mood_counts),
            "mood_trend": trend,
            "last_mood": mood_history[-1] if mood_history else None
        }

    # ── Sentiment Analysis Over Time ────────────────────────────────
    
    def add_sentiment_record(
        self,
        user_id: str,
        sentiment_data: Dict
    ) -> None:
        """Record sentiment analysis for tracking trends"""
        user = self.get_or_create_user(user_id)
        
        sentiment_record = {
            "timestamp": datetime.now().isoformat(),
            **sentiment_data
        }
        
        # Store in mood history metadata
        if user.mood_history:
            user.mood_history[-1]["sentiment"] = sentiment_record

    def get_sentiment_trend(self, user_id: str, days: int = 7) -> Dict:
        """Get sentiment trend over time"""
        if not self.user_exists(user_id):
            return {}

        user = self.users[user_id]
        cutoff_time = datetime.now() - timedelta(days=days)
        
        relevant_moods = [
            mood for mood in user.mood_history
            if datetime.fromisoformat(mood["timestamp"]) > cutoff_time
        ]

        if not relevant_moods:
            return {
                "trend": "insufficient_data",
                "average_polarity": 0.5,
                "recent_average": 0.5,
                "dominant_emotion": "neutral",
                "records": 0
            }

        # Extract polarity scores from sentiment data (if available)
        polarities = []
        emotions = defaultdict(int)

        for mood in relevant_moods:
            if "sentiment" in mood:
                sentiment = mood["sentiment"]
                # Approximate polarity from mood
                mood_name = mood.get("mood", "neutral")
                if mood_name in ["happy", "excited", "hopeful", "energized"]:
                    polarities.append(0.8)
                elif mood_name in ["sad", "depressed", "anxious"]:
                    polarities.append(0.2)
                else:
                    polarities.append(0.5)

                # Track emotions
                if "emotion_scores" in sentiment:
                    for emotion, score in sentiment["emotion_scores"].items():
                        if score > 0.3:
                            emotions[emotion] += 1

        if not polarities:
            # Fallback if no sentiment data
            polarities = [0.5] * len(relevant_moods)

        avg_polarity = sum(polarities) / len(polarities) if polarities else 0.5
        recent_avg = sum(polarities[-3:]) / len(polarities[-3:]) if len(polarities) >= 3 else avg_polarity

        dominant_emotion = (
            max(emotions, key=emotions.get)
            if emotions
            else "neutral"
        )

        return {
            "trend": "improving" if recent_avg > avg_polarity else ("declining" if recent_avg < avg_polarity else "stable"),
            "average_polarity": round(avg_polarity, 3),
            "recent_average": round(recent_avg, 3),
            "dominant_emotion": dominant_emotion,
            "records": len(relevant_moods)
        }

    # ── Statistics ──────────────────────────────────────────────────
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get user statistics"""
        if not self.user_exists(user_id):
            return {}

        user = self.users[user_id]

        return {
            "user_id": user_id,
            "total_messages": user.total_messages,
            "conversation_count": len(user.conversation_history),
            "mood_entries": len(user.mood_history),
            "session_started": user.session_created.isoformat(),
            "last_active": user.last_message_time.isoformat() if user.last_message_time else None,
            "current_mood": user.current_mood
        }

    def cleanup_old_sessions(self) -> None:
        """Remove sessions older than timeout"""
        cutoff = datetime.now() - timedelta(minutes=self.sessions_timeout_minutes)
        to_remove = [
            user_id for user_id, user in self.users.items()
            if user.session_created < cutoff and user.last_message_time is None
        ]
        for user_id in to_remove:
            del self.users[user_id]


# Global database instance
db = InMemoryDatabase()
