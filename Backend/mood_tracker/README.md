# KAIROS Mood Tracker API

A comprehensive mood tracking and analytics API built with FastAPI featuring ML-powered mood classification, trend analysis, and personalized recommendations.

## Features

- 🧠 **ML-Powered Mood Classification**: Ensemble Random Forest + Gradient Boosting models
- 📊 **Mood Analytics**: Track mood trends, statistics, and patterns
- 📈 **Sentiment Trends**: Analyze mood direction over time (improving/declining/stable)
- 🎯 **Personalized Recommendations**: AI-generated suggestions based on mood and trends
- 🔒 **GDPR Compliance**: Data export and deletion endpoints
- 🚀 **REST API**: Clean, well-documented endpoints with Swagger UI

## Quick Start

### Prerequisites

- Python 3.10+
- pip (Python package manager)

### Installation

1. **Navigate to the mood tracker API directory**:
   ```bash
   cd Backend/mood_tracker
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**:
   ```bash
   python run.py
   ```

   Or with uvicorn directly:
   ```bash
   uvicorn app:app --host 127.0.0.1 --port 8000 --reload
   ```

### Server is Running ✅

Once started, the API will be available at:
- **API**: http://127.0.0.1:8000
- **Docs (Swagger UI)**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## API Endpoints

### Health Check
```
GET /health
```
Check if the API is running and models are loaded.

**Response**:
```json
{
  "status": "ok",
  "timestamp": "2026-05-17T12:00:00",
  "version": "1.0.0",
  "ml_models_loaded": true
}
```

### Quick Mood Check-in
```
POST /mood/checkin
Content-Type: application/json

{
  "user_id": "user123",
  "emotion": "anxious",
  "notes": "Optional context"
}
```

**Response**:
```json
{
  "user_id": "user123",
  "recorded_mood": "anxious_overwhelmed",
  "timestamp": "2026-05-17T12:00:00",
  "message": "Mood 'anxious' recorded successfully"
}
```

### Log Mood with Intensity
```
POST /mood/log
Content-Type: application/json

{
  "user_id": "user123",
  "mood": "anxious_overwhelmed",
  "intensity": 7,
  "context": "Work stress"
}
```

### Get Mood History
```
GET /mood/history?user_id=user123&days=30&limit=100
```

**Response**:
```json
{
  "user_id": "user123",
  "records": [
    {
      "timestamp": "2026-05-17T12:00:00",
      "mood": "anxious_overwhelmed",
      "intensity": 7,
      "context": "Work stress",
      "confidence": 0.85
    }
  ],
  "total_records": 15,
  "date_range": {
    "start": "2026-05-01T09:00:00",
    "end": "2026-05-17T12:00:00"
  }
}
```

### Get Current Mood
```
GET /mood/current?user_id=user123
```

### Get Mood Statistics
```
GET /mood/stats?user_id=user123&days=30
```

**Response**:
```json
{
  "user_id": "user123",
  "total_assessments": 15,
  "average_mood": "anxious_overwhelmed",
  "most_common_mood": "anxious_overwhelmed",
  "mood_variety": 0.65,
  "last_assessment": "2026-05-17T12:00:00",
  "streak_days": 3,
  "weekly_average_intensity": 6.2
}
```

### Get Mood Trends
```
GET /mood/trends?user_id=user123&period=weekly
```

Periods: `daily`, `weekly`, `monthly`

**Response**:
```json
{
  "user_id": "user123",
  "time_period": "weekly",
  "trend_direction": "improving",
  "average_mood": "anxious_overwhelmed",
  "dominant_emotion": "anxious_overwhelmed",
  "emotion_distribution": {
    "anxious_overwhelmed": 7,
    "calm_content": 3,
    "neutral_balanced": 2
  },
  "recommendations": [
    "Great progress! Keep using your coping strategies",
    "Your anxiety is easing, maintain this momentum"
  ]
}
```

### Start Assessment
```
POST /assessment/start?user_id=user123
```

Returns assessment session with questions and options.

### Submit Assessment
```
POST /assessment/submit?user_id=user123&session_id=<session_id>
Content-Type: application/json

{
  "emotions": ["anxious", "worried"],
  "energy": 2,
  "overall_rating": 3
}
```

### Test Mood Classification
```
POST /test/classify?text=I%20feel%20really%20anxious%20today
```

**Response**:
```json
{
  "input_text": "I feel really anxious today",
  "predicted_mood": "anxious_overwhelmed",
  "confidence": 0.92,
  "all_scores": {
    "energized_positive": 0.05,
    "calm_content": 0.03,
    "neutral_balanced": 0.05,
    "anxious_overwhelmed": 0.92,
    "sad_withdrawn": 0.02,
    "frustrated_irritable": 0.10
  }
}
```

### Export User Data (GDPR)
```
GET /user/export?user_id=user123
```

Returns all user's mood data in JSON format.

### Delete User Data (GDPR)
```
DELETE /user/delete?user_id=user123
```

## Mood Categories

The API classifies moods into 6 categories:

| Category | Clinical Context |
|----------|------------------|
| `energized_positive` | Positive, energetic state |
| `calm_content` | Peaceful, satisfied state |
| `neutral_balanced` | Neutral, stable state |
| `anxious_overwhelmed` | Anxious, worried state |
| `sad_withdrawn` | Depressed, withdrawn state |
| `frustrated_irritable` | Angry, frustrated state |

## Machine Learning Models

The API uses an ensemble approach:

- **Random Forest Classifier**: 100 trees, max depth 10
- **Gradient Boosting Classifier**: 100 boosters, max depth 5
- **Voting Classifier**: Soft voting for final predictions

Models are trained on synthetic data demonstrating mood-related keywords and can be retrained with real data.

## Database

Currently uses **in-memory storage** (Python dictionary). For production, migrate to:
- PostgreSQL
- MongoDB
- Firebase Firestore

## Environment Variables

Create a `.env` file (optional):
```
MOOD_TRACKER_PORT=8000
MOOD_TRACKER_HOST=127.0.0.1
```

## CORS Configuration

The API allows requests from:
- http://localhost:4173 (KAIROS Frontend)
- http://localhost:5173 (Alternative port)
- http://localhost:3000 (Dev server)
- http://127.0.0.1:4173

Add more origins as needed in `app.py`.

## Integration with Frontend

The frontend (`KAIROS/src/utils/api.ts`) connects to:
```typescript
const MOOD_TRACKER_API_URL = 'http://localhost:8000';
```

## Testing

Test endpoints using:

1. **Swagger UI**: http://127.0.0.1:8000/docs
2. **cURL**:
   ```bash
   curl -X POST http://127.0.0.1:8000/mood/checkin \
     -H "Content-Type: application/json" \
     -d '{"user_id":"test","emotion":"happy"}'
   ```
3. **Python**:
   ```python
   import requests
   response = requests.post(
       'http://127.0.0.1:8000/mood/checkin',
       json={'user_id': 'test', 'emotion': 'happy'}
   )
   print(response.json())
   ```

## Production Deployment

Before deploying:

1. ✅ Replace in-memory database with PostgreSQL/MongoDB
2. ✅ Setup proper authentication (JWT/OAuth)
3. ✅ Configure environment variables
4. ✅ Setup Redis for caching (optional)
5. ✅ Setup monitoring and logging
6. ✅ Run with production ASGI server (Gunicorn, etc.)

```bash
pip install gunicorn
gunicorn app:app --workers 4 --bind 0.0.0.0:8000
```

## Architecture

```
┌─────────────────────────────────────┐
│     KAIROS Frontend (React)          │
│        Port: 4173                    │
└────────────────┬────────────────────┘
                 │
                 ▼
         ┌────────────────┐
         │  This API      │
         │  Port: 8000    │
         │                │
         │ ┌────────────┐ │
         │ │ ML Models  │ │
         │ │ Random     │ │
         │ │ Forest +   │ │
         │ │ Gradient   │ │
         │ │ Boosting   │ │
         │ └────────────┘ │
         │                │
         │ ┌────────────┐ │
         │ │ In-Memory  │ │
         │ │ Database   │ │
         │ └────────────┘ │
         └────────────────┘
```

## License

MIT License - Part of KAIROS Project
