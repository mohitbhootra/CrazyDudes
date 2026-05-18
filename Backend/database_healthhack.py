"""
Comprehensive MongoDB Database Module - HealthHack Platform
Handles all 8 collections with proper methods for each data type
"""

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import re

load_dotenv()


class HealthHackDB:
    """
    Main database class for HealthHack platform
    Manages all 8 collections: users, moodLogs, diseases, brainRegions, 
    drugs, chatbotResponses, gameSessions, communityPosts
    """
    
    def __init__(self):
        """Initialize MongoDB connection"""
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb+srv://maheshwarimohit701_db_user:h0BMjjS6Prvx8atX@cluster0.wrwxz0m.mongodb.net/?appName=Cluster0")
        self.db_name = os.getenv("MONGODB_DB", "healthhack")
        
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.connected = True
            print("✅ MongoDB connected - HealthHack DB ready")
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            print(f"⚠️ MongoDB connection failed: {e}")
            self.connected = False

    # ═════════════════════════════════════════════════════════════════════
    # 1. USERS COLLECTION
    # ═════════════════════════════════════════════════════════════════════
    
    def create_user(self, user_data: Dict) -> bool:
        """Create new user"""
        if not self.connected:
            return False
        try:
            self.db.users.insert_one({
                "userId": user_data.get("userId"),
                "email": user_data.get("email"),
                "password": user_data.get("password"),  # Should be bcrypt hashed
                "totalXP": 0,
                "preferences": user_data.get("preferences", {}),
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            })
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        if not self.connected:
            return None
        return self.db.users.find_one({"userId": user_id})
    
    def update_user_xp(self, user_id: str, xp_amount: int) -> bool:
        """Update user XP"""
        if not self.connected:
            return False
        result = self.db.users.update_one(
            {"userId": user_id},
            {
                "$inc": {"totalXP": xp_amount},
                "$set": {"updatedAt": datetime.now()}
            }
        )
        return result.modified_count > 0

    # ═════════════════════════════════════════════════════════════════════
    # 2. MOOD LOGS COLLECTION
    # ═════════════════════════════════════════════════════════════════════
    
    def log_mood(self, mood_data: Dict) -> bool:
        """Log user mood entry"""
        if not self.connected:
            return False
        try:
            self.db.moodLogs.insert_one({
                "userId": mood_data.get("userId"),
                "timestamp": datetime.now(),
                "moodScore": mood_data.get("moodScore", 0),  # 1-10
                "stressLevel": mood_data.get("stressLevel", 0),  # 1-10
                "answers": mood_data.get("answers", []),
                "notes": mood_data.get("notes", "")
            })
            return True
        except Exception as e:
            print(f"Error logging mood: {e}")
            return False
    
    def get_mood_history(self, user_id: str, days: int = 30) -> List[Dict]:
        """Get mood history for user"""
        if not self.connected:
            return []
        cutoff = datetime.now() - timedelta(days=days)
        return list(self.db.moodLogs.find(
            {"userId": user_id, "timestamp": {"$gte": cutoff}}
        ).sort("timestamp", -1))
    
    def get_mood_stats(self, user_id: str, days: int = 30) -> Dict:
        """Get mood statistics"""
        if not self.connected:
            return {}
        moods = self.get_mood_history(user_id, days)
        if not moods:
            return {"average": 0, "total": 0}
        
        avg_mood = sum(m.get("moodScore", 0) for m in moods) / len(moods)
        avg_stress = sum(m.get("stressLevel", 0) for m in moods) / len(moods)
        
        return {
            "average_mood": round(avg_mood, 2),
            "average_stress": round(avg_stress, 2),
            "total_entries": len(moods)
        }

    # ═════════════════════════════════════════════════════════════════════
    # 3. DISEASES COLLECTION
    # ═════════════════════════════════════════════════════════════════════
    
    def add_disease(self, disease_data: Dict) -> bool:
        """Add disease to database"""
        if not self.connected:
            return False
        try:
            self.db.diseases.insert_one({
                "name": disease_data.get("name"),
                "symptoms": disease_data.get("symptoms", []),
                "brainRegions": disease_data.get("brainRegions", []),
                "treatments": disease_data.get("treatments", []),
                "description": disease_data.get("description", ""),
                "category": disease_data.get("category", "general"),
                "createdAt": datetime.now()
            })
            return True
        except Exception as e:
            print(f"Error adding disease: {e}")
            return False
    
    def search_diseases(self, query: str, limit: int = 10) -> List[Dict]:
        """Full-text search diseases"""
        if not self.connected:
            return []
        return list(self.db.diseases.find(
            {"$text": {"$search": query}}
        ).limit(limit))
    
    def get_disease_by_category(self, category: str) -> List[Dict]:
        """Get diseases by category"""
        if not self.connected:
            return []
        return list(self.db.diseases.find({"category": category}))

    # ═════════════════════════════════════════════════════════════════════
    # 4. BRAIN REGIONS COLLECTION
    # ═════════════════════════════════════════════════════════════════════
    
    def add_brain_region(self, region_data: Dict) -> bool:
        """Add brain region"""
        if not self.connected:
            return False
        try:
            self.db.brainRegions.insert_one({
                "name": region_data.get("name"),
                "issues": region_data.get("issues", []),
                "facts": region_data.get("facts", []),
                "color": region_data.get("color", "#ffffff"),
                "coordinates3d": region_data.get("coordinates3d", {}),
                "createdAt": datetime.now()
            })
            return True
        except Exception as e:
            print(f"Error adding brain region: {e}")
            return False
    
    def get_brain_region(self, name: str) -> Optional[Dict]:
        """Get brain region by name"""
        if not self.connected:
            return None
        return self.db.brainRegions.find_one({"name": name})
    
    def get_all_brain_regions(self) -> List[Dict]:
        """Get all brain regions"""
        if not self.connected:
            return []
        return list(self.db.brainRegions.find({}))

    # ═════════════════════════════════════════════════════════════════════
    # 5. DRUGS COLLECTION
    # ═════════════════════════════════════════════════════════════════════
    
    def add_drug(self, drug_data: Dict) -> bool:
        """Add drug to database"""
        if not self.connected:
            return False
        try:
            self.db.drugs.insert_one({
                "name": drug_data.get("name"),
                "pros": drug_data.get("pros", []),
                "cons": drug_data.get("cons", []),
                "effects": drug_data.get("effects", []),
                "safeDose": drug_data.get("safeDose", ""),
                "category": drug_data.get("category", "general"),
                "description": drug_data.get("description", ""),
                "createdAt": datetime.now()
            })
            return True
        except Exception as e:
            print(f"Error adding drug: {e}")
            return False
    
    def search_drugs(self, query: str, limit: int = 10) -> List[Dict]:
        """Full-text search drugs"""
        if not self.connected:
            return []
        return list(self.db.drugs.find(
            {"$text": {"$search": query}}
        ).limit(limit))
    
    def get_drug(self, name: str) -> Optional[Dict]:
        """Get drug by name"""
        if not self.connected:
            return None
        return self.db.drugs.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})

    # ═════════════════════════════════════════════════════════════════════
    # 6. CHATBOT RESPONSES COLLECTION
    # ═════════════════════════════════════════════════════════════════════
    
    def add_chatbot_response(self, response_data: Dict) -> bool:
        """Add chatbot Q&A"""
        if not self.connected:
            return False
        try:
            self.db.chatbotResponses.insert_one({
                "question": response_data.get("question"),
                "answer": response_data.get("answer"),
                "category": response_data.get("category", "general"),  # bot1, bot2, bot3, general
                "keywords": response_data.get("keywords", []),
                "confidence": response_data.get("confidence", 0.5),
                "createdAt": datetime.now()
            })
            return True
        except Exception as e:
            print(f"Error adding chatbot response: {e}")
            return False
    
    def search_chatbot_qa(self, query: str, category: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """Search chatbot responses"""
        if not self.connected:
            return []
        search_filter = {"$text": {"$search": query}}
        if category:
            search_filter["category"] = category
        
        return list(self.db.chatbotResponses.find(search_filter).limit(limit))
    
    def get_chatbot_by_category(self, category: str) -> List[Dict]:
        """Get chatbot responses by category (bot1, bot2, bot3)"""
        if not self.connected:
            return []
        return list(self.db.chatbotResponses.find({"category": category}))

    # ═════════════════════════════════════════════════════════════════════
    # 7. GAME SESSIONS COLLECTION
    # ═════════════════════════════════════════════════════════════════════
    
    def log_game_session(self, session_data: Dict) -> bool:
        """Log game session"""
        if not self.connected:
            return False
        try:
            self.db.gameSessions.insert_one({
                "userId": session_data.get("userId"),
                "gameType": session_data.get("gameType"),
                "score": session_data.get("score", 0),
                "xpEarned": session_data.get("xpEarned", 0),
                "timestamp": datetime.now(),
                "duration": session_data.get("duration", 0),  # in seconds
                "metadata": session_data.get("metadata", {})
            })
            # Update user XP
            self.update_user_xp(session_data.get("userId"), session_data.get("xpEarned", 0))
            return True
        except Exception as e:
            print(f"Error logging game session: {e}")
            return False
    
    def get_user_game_stats(self, user_id: str) -> Dict:
        """Get user game statistics"""
        if not self.connected:
            return {}
        sessions = list(self.db.gameSessions.find({"userId": user_id}))
        if not sessions:
            return {"total_sessions": 0, "total_xp": 0}
        
        total_xp = sum(s.get("xpEarned", 0) for s in sessions)
        total_time = sum(s.get("duration", 0) for s in sessions)
        
        return {
            "total_sessions": len(sessions),
            "total_xp": total_xp,
            "total_playtime": total_time,
            "average_score": sum(s.get("score", 0) for s in sessions) / len(sessions)
        }

    # ═════════════════════════════════════════════════════════════════════
    # 8. COMMUNITY POSTS COLLECTION
    # ═════════════════════════════════════════════════════════════════════
    
    def create_community_post(self, post_data: Dict) -> Optional[str]:
        """Create community post, returns post ID"""
        if not self.connected:
            return None
        try:
            result = self.db.communityPosts.insert_one({
                "userId": post_data.get("userId"),
                "title": post_data.get("title"),
                "content": post_data.get("content"),
                "tags": post_data.get("tags", []),
                "upvotes": 0,
                "replies": [],
                "timestamp": datetime.now(),
                "updatedAt": datetime.now()
            })
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating post: {e}")
            return None
    
    def search_community(self, query: str, limit: int = 20) -> List[Dict]:
        """Full-text search community posts"""
        if not self.connected:
            return []
        return list(self.db.communityPosts.find(
            {"$text": {"$search": query}}
        ).sort("timestamp", -1).limit(limit))
    
    def get_recent_posts(self, limit: int = 10) -> List[Dict]:
        """Get recent community posts"""
        if not self.connected:
            return []
        return list(self.db.communityPosts.find({}).sort("timestamp", -1).limit(limit))
    
    def upvote_post(self, post_id: str) -> bool:
        """Upvote a post"""
        if not self.connected:
            return False
        from bson.objectid import ObjectId
        result = self.db.communityPosts.update_one(
            {"_id": ObjectId(post_id)},
            {"$inc": {"upvotes": 1}}
        )
        return result.modified_count > 0
    
    def add_reply(self, post_id: str, reply_data: Dict) -> bool:
        """Add reply to post"""
        if not self.connected:
            return False
        from bson.objectid import ObjectId
        reply = {
            "userId": reply_data.get("userId"),
            "content": reply_data.get("content"),
            "timestamp": datetime.now()
        }
        result = self.db.communityPosts.update_one(
            {"_id": ObjectId(post_id)},
            {
                "$push": {"replies": reply},
                "$set": {"updatedAt": datetime.now()}
            }
        )
        return result.modified_count > 0

    # ═════════════════════════════════════════════════════════════════════
    # GAMES COLLECTION (Game Library & Metadata)
    # ═════════════════════════════════════════════════════════════════════
    
    def get_all_games(self, limit: int = 50) -> List[Dict]:
        """Get all available games"""
        if not self.connected:
            return []
        try:
            games = list(self.db.games.find({"isActive": True}).limit(limit))
            # Convert ObjectId to string for JSON serialization
            for game in games:
                if "_id" in game:
                    game["_id"] = str(game["_id"])
            return games
        except Exception as e:
            print(f"Error fetching games: {e}")
            return []
    
    def get_game_by_id(self, game_id: str) -> Optional[Dict]:
        """Get game by ID"""
        if not self.connected:
            return None
        try:
            game = self.db.games.find_one({"gameId": game_id})
            if game:
                game["_id"] = str(game["_id"])
            return game
        except Exception as e:
            print(f"Error fetching game: {e}")
            return None
    
    def get_games_by_mood(self, mood: str, limit: int = 10) -> List[Dict]:
        """Get games recommended for a specific mood"""
        if not self.connected:
            return []
        try:
            games = list(self.db.games.find({
                "moodTags": mood,
                "isActive": True
            }).limit(limit))
            for game in games:
                if "_id" in game:
                    game["_id"] = str(game["_id"])
            return games
        except Exception as e:
            print(f"Error fetching games by mood: {e}")
            return []
    
    def get_games_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """Get games by category (therapy, wellness, positive, puzzle, relaxation)"""
        if not self.connected:
            return []
        try:
            games = list(self.db.games.find({
                "category": category,
                "isActive": True
            }).limit(limit))
            for game in games:
                if "_id" in game:
                    game["_id"] = str(game["_id"])
            return games
        except Exception as e:
            print(f"Error fetching games by category: {e}")
            return []
    
    def search_games(self, query: str, limit: int = 10) -> List[Dict]:
        """Full-text search games by name or description"""
        if not self.connected:
            return []
        try:
            games = list(self.db.games.find({
                "$text": {"$search": query},
                "isActive": True
            }).limit(limit))
            for game in games:
                if "_id" in game:
                    game["_id"] = str(game["_id"])
            return games
        except Exception as e:
            print(f"Error searching games: {e}")
            return []
    
    def get_game_stats_summary(self) -> Dict:
        """Get summary statistics about games"""
        if not self.connected:
            return {}
        try:
            total_games = self.db.games.count_documents({"isActive": True})
            categories = self.db.games.distinct("category", {"isActive": True})
            
            category_counts = {}
            for cat in categories:
                category_counts[cat] = self.db.games.count_documents({
                    "category": cat,
                    "isActive": True
                })
            
            return {
                "total_games": total_games,
                "categories": category_counts,
                "difficulties": ["Easy", "Medium", "Hard"]
            }
        except Exception as e:
            print(f"Error getting game stats: {e}")
            return {}

    # ═════════════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═════════════════════════════════════════════════════════════════════
    
    def get_db_status(self) -> Dict:
        """Get database status"""
        if not self.connected:
            return {"status": "disconnected"}
        
        collections = self.db.list_collection_names()
        stats = {
            "status": "connected",
            "collections": collections,
            "collection_count": len(collections)
        }
        
        # Add document counts
        for coll in collections:
            stats[f"{coll}_count"] = self.db[coll].count_documents({})
        
        return stats
    
    def close(self):
        """Close MongoDB connection"""
        if self.connected and hasattr(self, 'client'):
            self.client.close()


# Global instance
db = HealthHackDB()
