"""
HealthHack API - FastAPI endpoints for all collections
Provides comprehensive API for all 8 MongoDB collections
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from database_healthhack import db
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="HealthHack API",
    description="Complete API for mental health platform with 8 MongoDB collections",
    version="1.0.0"
)

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:4173,http://127.0.0.1:4173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═════════════════════════════════════════════════════════════════════

class UserCreate(BaseModel):
    userId: str
    email: str
    password: str
    preferences: Optional[Dict] = {}

class MoodLog(BaseModel):
    userId: str
    moodScore: int  # 1-10
    stressLevel: int  # 1-10
    notes: Optional[str] = ""
    answers: Optional[List[str]] = []

class DiseaseCreate(BaseModel):
    name: str
    symptoms: List[str] = []
    brainRegions: List[str] = []
    treatments: List[str] = []
    description: Optional[str] = ""
    category: Optional[str] = "general"

class DrugCreate(BaseModel):
    name: str
    pros: List[str] = []
    cons: List[str] = []
    effects: List[str] = []
    safeDose: Optional[str] = ""
    category: Optional[str] = "general"
    description: Optional[str] = ""

class BrainRegionCreate(BaseModel):
    name: str
    issues: List[str] = []
    facts: List[str] = []
    color: Optional[str] = "#ffffff"
    coordinates3d: Optional[Dict] = {}

class ChatbotResponseCreate(BaseModel):
    question: str
    answer: str
    category: Optional[str] = "general"  # bot1, bot2, bot3
    keywords: List[str] = []
    confidence: Optional[float] = 0.5

class GameSession(BaseModel):
    userId: str
    gameType: str
    score: int = 0
    xpEarned: int = 0
    duration: int = 0  # seconds
    metadata: Optional[Dict] = {}

class CommunityPost(BaseModel):
    userId: str
    title: str
    content: str
    tags: List[str] = []

class CommunityReply(BaseModel):
    userId: str
    content: str

# ═════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check():
    """Check API and database status"""
    status = db.get_db_status()
    return {
        "status": "ok",
        "api": "running",
        "database": status
    }

# ═════════════════════════════════════════════════════════════════════
# 1. USERS ENDPOINTS
# ═════════════════════════════════════════════════════════════════════

@app.post("/api/users")
async def create_user(user: UserCreate):
    """Create new user"""
    success = db.create_user(user.dict())
    if success:
        return {"status": "success", "message": "User created"}
    raise HTTPException(status_code=400, detail="Failed to create user")

@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    """Get user by ID"""
    user = db.get_user(user_id)
    if user:
        user['_id'] = str(user['_id'])
        return user
    raise HTTPException(status_code=404, detail="User not found")

# ═════════════════════════════════════════════════════════════════════
# 2. MOOD LOGS ENDPOINTS
# ═════════════════════════════════════════════════════════════════════

@app.post("/api/mood-logs")
async def log_mood(mood: MoodLog):
    """Log user mood"""
    success = db.log_mood(mood.dict())
    if success:
        return {"status": "success", "message": "Mood logged"}
    raise HTTPException(status_code=400, detail="Failed to log mood")

@app.get("/api/mood-logs/{user_id}")
async def get_mood_history(user_id: str, days: int = Query(30, ge=1)):
    """Get mood history for user"""
    history = db.get_mood_history(user_id, days)
    return {
        "user_id": user_id,
        "count": len(history),
        "data": history
    }

@app.get("/api/mood-stats/{user_id}")
async def get_mood_stats(user_id: str, days: int = Query(30, ge=1)):
    """Get mood statistics"""
    stats = db.get_mood_stats(user_id, days)
    return stats

# ═════════════════════════════════════════════════════════════════════
# 3. DISEASES ENDPOINTS
# ═════════════════════════════════════════════════════════════════════

@app.post("/api/diseases")
async def add_disease(disease: DiseaseCreate):
    """Add disease to database"""
    success = db.add_disease(disease.dict())
    if success:
        return {"status": "success", "message": "Disease added"}
    raise HTTPException(status_code=400, detail="Failed to add disease")

@app.get("/api/diseases/search")
async def search_diseases(q: str = Query(..., min_length=2), limit: int = Query(10, ge=1, le=100)):
    """Full-text search diseases"""
    results = db.search_diseases(q, limit)
    return {
        "query": q,
        "count": len(results),
        "results": results
    }

@app.get("/api/diseases/category/{category}")
async def get_diseases_by_category(category: str):
    """Get diseases by category"""
    diseases = db.get_disease_by_category(category)
    return {
        "category": category,
        "count": len(diseases),
        "diseases": diseases
    }

# ═════════════════════════════════════════════════════════════════════
# 4. BRAIN REGIONS ENDPOINTS
# ═════════════════════════════════════════════════════════════════════

@app.post("/api/brain-regions")
async def add_brain_region(region: BrainRegionCreate):
    """Add brain region"""
    success = db.add_brain_region(region.dict())
    if success:
        return {"status": "success", "message": "Brain region added"}
    raise HTTPException(status_code=400, detail="Failed to add brain region")

@app.get("/api/brain-regions/{name}")
async def get_brain_region(name: str):
    """Get brain region by name"""
    region = db.get_brain_region(name)
    if region:
        return region
    raise HTTPException(status_code=404, detail="Brain region not found")

@app.get("/api/brain-regions")
async def get_all_brain_regions():
    """Get all brain regions (for 3D visualization)"""
    regions = db.get_all_brain_regions()
    return {
        "count": len(regions),
        "regions": regions
    }

# ═════════════════════════════════════════════════════════════════════
# 5. DRUGS ENDPOINTS
# ═════════════════════════════════════════════════════════════════════

@app.post("/api/drugs")
async def add_drug(drug: DrugCreate):
    """Add drug to database"""
    success = db.add_drug(drug.dict())
    if success:
        return {"status": "success", "message": "Drug added"}
    raise HTTPException(status_code=400, detail="Failed to add drug")

@app.get("/api/drugs/search")
async def search_drugs(q: str = Query(..., min_length=2), limit: int = Query(10, ge=1, le=100)):
    """Full-text search drugs"""
    results = db.search_drugs(q, limit)
    return {
        "query": q,
        "count": len(results),
        "results": results
    }

@app.get("/api/drugs/{name}")
async def get_drug(name: str):
    """Get drug by name"""
    drug = db.get_drug(name)
    if drug:
        return drug
    raise HTTPException(status_code=404, detail="Drug not found")

# ═════════════════════════════════════════════════════════════════════
# 6. CHATBOT RESPONSES ENDPOINTS
# ═════════════════════════════════════════════════════════════════════

@app.post("/api/chatbot/responses")
async def add_chatbot_response(response: ChatbotResponseCreate):
    """Add chatbot Q&A"""
    success = db.add_chatbot_response(response.dict())
    if success:
        return {"status": "success", "message": "Chatbot response added"}
    raise HTTPException(status_code=400, detail="Failed to add chatbot response")

@app.get("/api/chatbot/search")
async def search_chatbot(q: str = Query(..., min_length=2), category: Optional[str] = None, limit: int = Query(5)):
    """Search chatbot Q&A"""
    results = db.search_chatbot_qa(q, category, limit)
    return {
        "query": q,
        "category": category,
        "count": len(results),
        "results": results
    }

@app.get("/api/chatbot/category/{category}")
async def get_chatbot_by_category(category: str):
    """Get chatbot responses by category (bot1, bot2, bot3)"""
    responses = db.get_chatbot_by_category(category)
    return {
        "category": category,
        "count": len(responses),
        "responses": responses
    }

# ═════════════════════════════════════════════════════════════════════
# 7. GAME SESSIONS ENDPOINTS
# ═════════════════════════════════════════════════════════════════════

@app.post("/api/games/sessions")
async def log_game_session(session: GameSession):
    """Log game session"""
    success = db.log_game_session(session.dict())
    if success:
        return {"status": "success", "message": "Game session logged", "xp_earned": session.xpEarned}
    raise HTTPException(status_code=400, detail="Failed to log game session")

@app.get("/api/games/stats/{user_id}")
async def get_game_stats(user_id: str):
    """Get user game statistics"""
    stats = db.get_user_game_stats(user_id)
    return {
        "user_id": user_id,
        "stats": stats
    }

# ═════════════════════════════════════════════════════════════════════
# 8. COMMUNITY ENDPOINTS
# ═════════════════════════════════════════════════════════════════════

@app.post("/api/community/posts")
async def create_community_post(post: CommunityPost):
    """Create community post"""
    post_id = db.create_community_post(post.dict())
    if post_id:
        return {"status": "success", "post_id": post_id}
    raise HTTPException(status_code=400, detail="Failed to create post")

@app.get("/api/community/search")
async def search_community(q: str = Query(..., min_length=2), limit: int = Query(20)):
    """Search community posts"""
    results = db.search_community(q, limit)
    return {
        "query": q,
        "count": len(results),
        "results": results
    }

@app.get("/api/community/recent")
async def get_recent_posts(limit: int = Query(10, ge=1, le=100)):
    """Get recent community posts"""
    posts = db.get_recent_posts(limit)
    return {
        "count": len(posts),
        "posts": posts
    }

@app.post("/api/community/posts/{post_id}/upvote")
async def upvote_post(post_id: str):
    """Upvote a post"""
    success = db.upvote_post(post_id)
    if success:
        return {"status": "success", "message": "Post upvoted"}
    raise HTTPException(status_code=400, detail="Failed to upvote post")

@app.post("/api/community/posts/{post_id}/replies")
async def add_reply(post_id: str, reply: CommunityReply):
    """Add reply to post"""
    success = db.add_reply(post_id, reply.dict())
    if success:
        return {"status": "success", "message": "Reply added"}
    raise HTTPException(status_code=400, detail="Failed to add reply")

# ═════════════════════════════════════════════════════════════════════
# API DOCUMENTATION
# ═════════════════════════════════════════════════════════════════════

@app.get("/docs", include_in_schema=False)
async def get_docs():
    """Swagger UI documentation"""
    from fastapi.openapi.utils import get_openapi
    return get_openapi(
        title="HealthHack API",
        version="1.0.0",
        routes=app.routes,
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
