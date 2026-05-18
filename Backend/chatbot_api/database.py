"""
MongoDB database for storing user conversations and mood data
Persistent storage with MongoDB + fallback to in-memory
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import os
from dotenv import load_dotenv

load_dotenv()


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


class MongoDatabase:
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

    # ── Conversation History ────────────────────────────────────────
    
    def add_message(
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
            "timestamp": datetime.now(),
            "metadata": metadata or {}
        }
        
        if self.connected:
            # Insert message
            self.conversations_collection.insert_one({
                "user_id": user_id,
                **message
            })
            
            # Update user totals
            self.users_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {"last_message_time": datetime.now()},
                    "$inc": {"total_messages": 1}
                }
            )
        else:
            user.conversation_history.append({
                "role": role,
                "content": content,
                "timestamp": message["timestamp"].isoformat(),
                "metadata": metadata or {}
            })
            user.last_message_time = datetime.now()
            user.total_messages += 1

    def get_conversation_history(
        self,
        user_id: str,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Get conversation history for user"""
        if self.connected:
            query = {"user_id": user_id}
            cursor = self.conversations_collection.find(query).sort("timestamp", -1)
            if limit:
                cursor = cursor.limit(limit)
            
            messages = []
            for doc in cursor:
                messages.append({
                    "role": doc["role"],
                    "content": doc["content"],
                    "timestamp": doc["timestamp"].isoformat() if isinstance(doc["timestamp"], datetime) else doc["timestamp"],
                    "metadata": doc.get("metadata", {})
                })
            return list(reversed(messages))
        else:
            if not self.user_exists(user_id):
                return []

            user = self.users[user_id]
            history = user.conversation_history

            if limit:
                return history[-limit:]
            return history

    def clear_conversation(self, user_id: str) -> None:
        """Clear conversation history for user"""
        if self.connected:
            self.conversations_collection.delete_many({"user_id": user_id})
        else:
            if user_id in self.users:
                self.users[user_id].conversation_history = []

    def get_recent_messages(self, user_id: str, minutes: int = 60) -> List[Dict]:
        """Get messages from last N minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        if self.connected:
            messages = list(self.conversations_collection.find({
                "user_id": user_id,
                "timestamp": {"$gte": cutoff_time}
            }))
            
            return [
                {
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": msg["timestamp"].isoformat() if isinstance(msg["timestamp"], datetime) else msg["timestamp"],
                    "metadata": msg.get("metadata", {})
                }
                for msg in messages
            ]
        else:
            if not self.user_exists(user_id):
                return []

            user = self.users[user_id]
            
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
            "timestamp": datetime.now(),
            "metadata": metadata or {}
        }
        
        if self.connected:
            self.moods_collection.insert_one({
                "user_id": user_id,
                **mood_entry
            })
            
            self.users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"current_mood": mood}}
            )
        else:
            user.mood_history.append({
                "mood": mood,
                "source": source,
                "confidence": confidence,
                "timestamp": mood_entry["timestamp"].isoformat(),
                "metadata": metadata or {}
            })
            user.current_mood = mood

    def get_current_mood(self, user_id: str) -> Optional[Dict]:
        """Get user's current mood"""
        if self.connected:
            mood_doc = self.moods_collection.find_one(
                {"user_id": user_id},
                sort=[("timestamp", -1)]
            )
            if mood_doc:
                return {
                    "mood": mood_doc["mood"],
                    "source": mood_doc["source"],
                    "confidence": mood_doc["confidence"],
                    "timestamp": mood_doc["timestamp"].isoformat() if isinstance(mood_doc["timestamp"], datetime) else mood_doc["timestamp"],
                    "metadata": mood_doc.get("metadata", {})
                }
            return None
        else:
            if not self.user_exists(user_id):
                return None

            user = self.users[user_id]
            
            if not user.mood_history:
                return None

            latest_mood = user.mood_history[-1]
            return latest_mood

    def get_mood_history(self, user_id: str, days: int = 7) -> List[Dict]:
        """Get mood history for last N days"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        if self.connected:
            moods = list(self.moods_collection.find({
                "user_id": user_id,
                "timestamp": {"$gte": cutoff_time}
            }).sort("timestamp", -1))
            
            return [
                {
                    "mood": m["mood"],
                    "source": m["source"],
                    "confidence": m["confidence"],
                    "timestamp": m["timestamp"].isoformat() if isinstance(m["timestamp"], datetime) else m["timestamp"],
                    "metadata": m.get("metadata", {})
                }
                for m in moods
            ]
        else:
            if not self.user_exists(user_id):
                return []

            user = self.users[user_id]
            
            history = [
                mood for mood in user.mood_history
                if datetime.fromisoformat(mood["timestamp"]) > cutoff_time
            ]
            
            return history

    def get_mood_stats(self, user_id: str) -> Dict:
        """Get mood statistics"""
        if not self.user_exists(user_id):
            return {}

        mood_history = self.get_mood_history(user_id, days=7)

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
            "last_mood": mood_history[0] if mood_history else None
        }

    # ── Sentiment Analysis Over Time ────────────────────────────────
    
    def add_sentiment_record(
        self,
        user_id: str,
        sentiment_data: Dict
    ) -> None:
        """Record sentiment analysis for tracking trends"""
        if self.connected:
            self.db["sentiment_records"].insert_one({
                "user_id": user_id,
                "timestamp": datetime.now(),
                **sentiment_data
            })
        else:
            # For in-memory, just keep in mood history metadata
            pass

    def get_sentiment_trend(self, user_id: str, days: int = 7) -> Dict:
        """Get sentiment trend over time"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        if self.connected:
            records = list(self.db["sentiment_records"].find({
                "user_id": user_id,
                "timestamp": {"$gte": cutoff_time}
            }))
        else:
            records = []

        if not records:
            return {
                "trend": "insufficient_data",
                "average_polarity": 0.5,
                "recent_average": 0.5,
                "dominant_emotion": "neutral",
                "records": 0
            }

        # Extract polarity scores
        polarities = [r.get("polarity", 0.5) for r in records]
        emotions = defaultdict(int)

        for record in records:
            if "emotion_scores" in record:
                for emotion, score in record["emotion_scores"].items():
                    if score > 0.3:
                        emotions[emotion] += 1

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
            "records": len(records)
        }

    # ── Statistics ──────────────────────────────────────────────────
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get user statistics"""
        if not self.user_exists(user_id):
            return {}

        if self.connected:
            user_doc = self.users_collection.find_one({"user_id": user_id})
            if not user_doc:
                return {}
            
            msg_count = self.conversations_collection.count_documents({"user_id": user_id})
            mood_count = self.moods_collection.count_documents({"user_id": user_id})
            
            return {
                "user_id": user_id,
                "total_messages": msg_count,
                "conversation_count": msg_count,
                "mood_entries": mood_count,
                "session_started": user_doc.get("session_created", datetime.now()).isoformat() if isinstance(user_doc.get("session_created"), datetime) else str(user_doc.get("session_created")),
                "last_active": user_doc.get("last_message_time", datetime.now()).isoformat() if isinstance(user_doc.get("last_message_time"), datetime) else str(user_doc.get("last_message_time")),
                "current_mood": user_doc.get("current_mood")
            }
        else:
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
        
        if self.connected:
            self.users_collection.delete_many({
                "session_created": {"$lt": cutoff},
                "last_message_time": None
            })
        else:
            to_remove = [
                user_id for user_id, user in self.users.items()
                if user.session_created < cutoff and user.last_message_time is None
            ]
            for user_id in to_remove:
                del self.users[user_id]

    def close(self):
        """Close MongoDB connection"""
        if self.connected and hasattr(self, 'client'):
            self.client.close()


# Global database instance
db = MongoDatabase()
