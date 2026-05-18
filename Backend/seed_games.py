#!/usr/bin/env python3
"""
Seed game definitions into MongoDB
Adds all game metadata from frontend to database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database_healthhack import db
from datetime import datetime

GAMES_DATA = [
    {
        "gameId": "cbt-thought-challenger",
        "name": "CBT Thought Challenger",
        "description": "Challenge and reframe negative thoughts using CBT techniques",
        "emoji": "🧠",
        "category": "therapy",
        "difficulty": "Medium",
        "duration": "10-15 min",
        "moodTags": ["anxious", "sad", "frustrated", "stressed", "depressed"],
        "benefits": ["Reframes negative thinking", "Builds cognitive resilience", "Evidence-based CBT"],
        "instructions": "Identify negative thoughts and learn to reframe them using CBT techniques",
        "createdAt": datetime.now(),
        "isActive": True
    },
    {
        "gameId": "mindfulness-breathing",
        "name": "Mindfulness Breathing",
        "description": "Guided breathing exercises for calm and relaxation",
        "emoji": "🌬️",
        "category": "wellness",
        "difficulty": "Easy",
        "duration": "5-10 min",
        "moodTags": ["anxious", "stressed", "overwhelmed", "tired", "neutral"],
        "benefits": ["Reduces anxiety", "Promotes relaxation", "Improves focus"],
        "instructions": "Follow guided breathing patterns to calm your mind and body",
        "createdAt": datetime.now(),
        "isActive": True
    },
    {
        "gameId": "gratitude-quest",
        "name": "Gratitude Quest",
        "description": "An adventure game that cultivates gratitude and positive thinking",
        "emoji": "🌟",
        "category": "positive",
        "difficulty": "Easy",
        "duration": "10-15 min",
        "moodTags": ["sad", "depressed", "neutral", "happy", "lonely"],
        "benefits": ["Boosts positivity", "Cultivates gratitude", "Shifts perspective"],
        "instructions": "Complete quests by identifying things you're grateful for",
        "createdAt": datetime.now(),
        "isActive": True
    },
    {
        "gameId": "emotion-match-puzzle",
        "name": "Emotion Match Puzzle",
        "description": "Match emotions and learn to identify feelings through fun puzzles",
        "emoji": "🧩",
        "category": "puzzle",
        "difficulty": "Easy",
        "duration": "5-10 min",
        "moodTags": ["neutral", "happy", "bored", "tired", "curious"],
        "benefits": ["Emotional intelligence", "Fun distraction", "Pattern recognition"],
        "instructions": "Match emotion cards and learn emotion identification",
        "createdAt": datetime.now(),
        "isActive": True
    },
    {
        "gameId": "virtual-garden",
        "name": "Virtual Garden",
        "description": "Grow a peaceful garden as a metaphor for personal growth",
        "emoji": "🌱",
        "category": "relaxation",
        "difficulty": "Easy",
        "duration": "5-15 min",
        "moodTags": ["stressed", "anxious", "sad", "peaceful", "calm"],
        "benefits": ["Promotes patience", "Visual relaxation", "Growth mindset"],
        "instructions": "Plant seeds, water plants, and watch your garden grow",
        "createdAt": datetime.now(),
        "isActive": True
    },
    {
        "gameId": "anxiety-buster",
        "name": "Anxiety Buster",
        "description": "Quick breathing exercises to calm anxiety",
        "emoji": "🫁",
        "category": "wellness",
        "difficulty": "Easy",
        "duration": "2-3 min",
        "moodTags": ["anxious", "panic", "worried", "nervous"],
        "benefits": ["Quick anxiety relief", "Portable calmness", "Immediate help"],
        "instructions": "Follow quick breathing patterns for instant anxiety relief",
        "createdAt": datetime.now(),
        "isActive": True
    },
    {
        "gameId": "energy-boost",
        "name": "Energy Boost",
        "description": "Quick activities to boost your energy",
        "emoji": "⚡",
        "category": "wellness",
        "difficulty": "Easy",
        "duration": "3-5 min",
        "moodTags": ["tired", "unmotivated", "low-energy", "sluggish"],
        "benefits": ["Instant energy", "Mood lifting", "Quick motivation"],
        "instructions": "Complete quick exercises to boost your energy levels",
        "createdAt": datetime.now(),
        "isActive": True
    },
    {
        "gameId": "sleep-sanctuary",
        "name": "Sleep Sanctuary",
        "description": "Guided relaxation and visualization for better sleep",
        "emoji": "😴",
        "category": "relaxation",
        "difficulty": "Easy",
        "duration": "15-30 min",
        "moodTags": ["tired", "insomnia", "restless", "stressed"],
        "benefits": ["Better sleep", "Deep relaxation", "Stress reduction"],
        "instructions": "Follow guided visualization to prepare for restful sleep",
        "createdAt": datetime.now(),
        "isActive": True
    },
    {
        "gameId": "mood-booster",
        "name": "Mood Booster",
        "description": "Interactive activities to improve your mood",
        "emoji": "😊",
        "category": "positive",
        "difficulty": "Easy",
        "duration": "5-10 min",
        "moodTags": ["sad", "neutral", "bored", "lonely"],
        "benefits": ["Mood improvement", "Positivity boost", "Social connection"],
        "instructions": "Complete mood-boosting activities and challenges",
        "createdAt": datetime.now(),
        "isActive": True
    },
    {
        "gameId": "focus-flow",
        "name": "Focus Flow",
        "description": "Improve concentration and enter flow state",
        "emoji": "🎯",
        "category": "wellness",
        "difficulty": "Medium",
        "duration": "15-30 min",
        "moodTags": ["distracted", "scattered", "unmotivated"],
        "benefits": ["Deep focus", "Productivity", "Flow state"],
        "instructions": "Complete focused exercises to build concentration",
        "createdAt": datetime.now(),
        "isActive": True
    }
]

def seed_games():
    """Seed game data into MongoDB"""
    try:
        # Create games collection if it doesn't exist
        if "games" not in db.db.list_collection_names():
            db.db.create_collection("games")
            print("✓ Created 'games' collection")
        
        # Clear existing games
        result = db.db.games.delete_many({})
        print(f"✓ Cleared {result.deleted_count} existing games")
        
        # Insert new games
        result = db.db.games.insert_many(GAMES_DATA)
        print(f"✓ Inserted {len(result.inserted_ids)} games")
        
        # Create indexes
        db.db.games.create_index([("gameId", 1)], unique=True)
        db.db.games.create_index([("category", 1)])
        db.db.games.create_index([("moodTags", 1)])
        db.db.games.create_index([("name", "text"), ("description", "text")])
        print("✓ Created indexes: gameId, category, moodTags, full-text search")
        
        print()
        print("=" * 70)
        print("✅ GAMES SEEDED SUCCESSFULLY!")
        print("=" * 70)
        print()
        print(f"📊 Total Games Added: {len(GAMES_DATA)}")
        print()
        print("📋 Games Added:")
        for game in GAMES_DATA:
            print(f"   • {game['emoji']} {game['name']} ({game['category']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error seeding games: {e}")
        return False

if __name__ == "__main__":
    seed_games()
