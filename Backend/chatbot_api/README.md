# KAIROS Chatbot API

A mental health chatbot API built with FastAPI that provides emotion detection, sentiment analysis, mood tracking, and crisis detection.

## Features

- 🤖 **AI-Powered Responses**: Contextual, empathetic responses to mental health conversations
- 😊 **Emotion Detection**: Identifies user emotions (happy, sad, angry, anxious, etc.)
- 📊 **Sentiment Analysis**: Analyzes text polarity and emotional intensity
- 😔 **Mood Tracking**: Records and tracks user mood over time
- 🚨 **Crisis Detection**: Identifies concerning messages and provides resources
- 📈 **Analytics**: Tracks sentiment trends and mood patterns
- 🔌 **REST API**: Clean, well-documented API endpoints

## Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Navigate to the chatbot API directory**:
   ```bash
   cd Backend/chatbot_api
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**:

   **On Windows**:
   ```bash
   run.bat
   ```

   **On macOS/Linux**:
   ```bash
   python run.py
   ```

   Or with uvicorn directly:
   ```bash
   uvicorn app:app --host 127.0.0.1 --port 8001 --reload
   ```

### Server is Running ✅

Once started, the API will be available at:
- **API**: http://127.0.0.1:8001
- **Docs (Swagger UI)**: http://127.0.0.1:8001/docs
- **ReDoc**: http://127.0.0.1:8001/redoc

## API Endpoints

### Health Check
```
GET /health
```
Check if the API is running.

### Chat - Send Message
```
POST /chat
Content-Type: application/json

{
  "user_id": "user123",
  "message": "I'm feeling anxious today"
}
```

Response:
```json
{
  "reply": "I understand you're feeling anxious...",
  "follow_up": "How does that feel?",
  "sentiment": {
    "detected_emotion": "anxious",
    "polarity": "negative",
    "polarity_score": 0.3,
    "confidence": 0.85,
    "intensity": "medium",
    "emotion_scores": { "anxious": 0.85, "worried": 0.72, ... }
  },
  "tracked_mood": "anxious_overwhelmed",
  "mood_source": "conversation",
  "technique_used": "grounding_technique",
  "crisis_detected": false,
  "crisis_resources": null
}
```

### Chat - Get History
```
GET /chat/history?user_id=user123&limit=50
```

Get conversation history for a user.

### Chat - Get Sentiment Trend
```
GET /chat/sentiment?user_id=user123&days=7
```

Get sentiment analysis trends over time.

### Chat - Clear History
```
POST /chat/clear?user_id=user123
```

Clear conversation history for a user.

### Mood - Get Current
```
GET /mood/current?user_id=user123
```

Get user's current mood status.

### Mood - Set Manually
```
POST /mood/set
Content-Type: application/json

{
  "user_id": "user123",
  "mood": "happy"
}
```

Manually set user's mood.

### Stats
```
GET /stats?user_id=user123
```

Get user statistics (total messages, mood entries, etc.)

## Supported Moods

- 😊 `happy` → energized_positive
- 😌 `calm` → calm_content
- 😐 `neutral` → neutral_balanced
- 😰 `anxious` → anxious_overwhelmed
- 😢 `sad` → sad_withdrawn
- 😠 `angry` → frustrated_irritable
- 🤔 `uncertain` → uncertain

## Emotion Detection

The API automatically detects the following emotions:

- Happy
- Sad
- Angry
- Anxious
- Neutral
- Excited
- Calm
- Frustrated
- Hopeful
- Depressed

## Crisis Detection

The API monitors for crisis indicators and provides emergency resources when detected:

- National Suicide Prevention Lifeline: 1-800-273-8255
- Crisis Text Line: Text HOME to 741741
- NAMI Helpline: 1-800-950-NAMI

## Architecture

```
chatbot_api/
├── app.py                 # Main FastAPI application
├── models.py             # Pydantic request/response models
├── sentiment_analyzer.py  # Emotion and sentiment analysis
├── database.py           # In-memory data storage
├── run.py                # Startup script
├── run.bat               # Windows startup script
├── requirements.txt      # Python dependencies
└── .env.example          # Environment variables template
```

## Configuration

Edit `.env.example` and save as `.env` to configure:

```
API_HOST=127.0.0.1
API_PORT=8001
FRONTEND_URL=http://localhost:4173
CRISIS_DETECTION_ENABLED=true
SESSION_TIMEOUT_MINUTES=30
```

## Technology Stack

- **Framework**: FastAPI
- **Server**: Uvicorn
- **Validation**: Pydantic
- **Python**: 3.8+

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| API_HOST | 127.0.0.1 | Server host |
| API_PORT | 8001 | Server port |
| API_RELOAD | true | Auto-reload on code changes |
| FRONTEND_URL | http://localhost:4173 | Frontend URL for CORS |
| SESSION_TIMEOUT_MINUTES | 30 | User session timeout |
| CRISIS_DETECTION_ENABLED | true | Enable crisis detection |

## Frontend Integration

The KAIROS frontend is configured to communicate with this API at:
```
http://localhost:8001
```

To change the API URL in the frontend, set the environment variable:
```
VITE_CHATBOT_API_URL=http://localhost:8001
```

## Testing

You can test the API immediately after starting:

### Using cURL

```bash
# Health check
curl http://127.0.0.1:8001/health

# Send a message
curl -X POST http://127.0.0.1:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user1","message":"I am feeling great today!"}'
```

### Using Swagger UI

1. Open http://127.0.0.1:8001/docs
2. Try out any endpoint using the interactive interface
3. All requests are documented with examples

## Performance

- **Response Time**: < 100ms per message
- **Concurrent Users**: Handles hundreds of concurrent users
- **Memory**: In-memory database (upgradeable to PostgreSQL)

## Future Enhancements

- [ ] Integration with advanced NLP models (transformers)
- [ ] PostgreSQL database backend
- [ ] User authentication and authorization
- [ ] Message persistence and backup
- [ ] Real-time WebSocket support
- [ ] Integration with professional mental health resources
- [ ] Machine learning model for mood prediction
- [ ] Multi-language support

## Troubleshooting

### Port 8001 already in use
```bash
# Find process using port 8001
netstat -ano | findstr :8001

# Kill the process
taskkill /PID <PID> /F
```

### ModuleNotFoundError
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### CORS Errors in Frontend
- Ensure the frontend URL is in the CORS allowed origins
- Check that the API is running on port 8001
- Clear browser cache and hard refresh

## Support

For issues or questions:
1. Check the API documentation at http://127.0.0.1:8001/docs
2. Review the response status codes
3. Check logs in the terminal

## License

Part of the KAIROS Mental Health Platform

---

**Status**: ✅ Ready for Development  
**Version**: 1.0.0  
**Port**: 8001
