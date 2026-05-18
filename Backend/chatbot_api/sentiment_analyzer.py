"""
Sentiment analysis and emotion detection module
Uses TextBlob for sentiment and rule-based emotion detection
"""

from typing import Dict, Tuple, List
import re
from enum import Enum


class Emotion(str, Enum):
    """Supported emotions"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    ANXIOUS = "anxious"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    CALM = "calm"
    FRUSTRATED = "frustrated"
    HOPEFUL = "hopeful"
    DEPRESSED = "depressed"


class SentimentAnalyzer:
    """
    Sentiment and emotion analyzer for mental health conversations
    Uses TextBlob for polarity and custom rules for emotion detection
    """

    # Emotion keywords for rule-based detection
    EMOTION_KEYWORDS = {
        Emotion.HAPPY: [
            "happy", "great", "wonderful", "excellent", "good", "awesome",
            "fantastic", "delighted", "joy", "love", "brilliant", "perfect",
            "thrilled", "laugh", "smile", "laughing", "smiling", "grateful"
        ],
        Emotion.SAD: [
            "sad", "depressed", "unhappy", "down", "blue", "lonely", "miserable",
            "heartbroken", "crying", "tears", "grief", "sorrow", "hurt",
            "disappointed", "worthless", "hopeless", "meaningless"
        ],
        Emotion.ANGRY: [
            "angry", "furious", "rage", "mad", "irritated", "frustrated",
            "annoyed", "bitter", "resentful", "hate", "despise", "damn",
            "pissed", "livid", "aggressive", "hostile"
        ],
        Emotion.ANXIOUS: [
            "anxious", "worried", "nervous", "scared", "afraid", "panic",
            "stressed", "overwhelmed", "tension", "uneasy", "dread",
            "apprehensive", "tense", "shaky", "trembling", "paranoid"
        ],
        Emotion.CALM: [
            "calm", "peaceful", "relaxed", "serene", "tranquil", "zen",
            "meditative", "breathe", "breathing", "centered", "balanced",
            "grounded", "steady", "composed", "content"
        ],
        Emotion.EXCITED: [
            "excited", "enthusiastic", "energized", "pumped", "thrilled",
            "stoked", "amped", "eager", "looking forward", "can't wait",
            "amazing", "incredible", "awesome", "fantastic"
        ],
        Emotion.FRUSTRATED: [
            "frustrated", "irritated", "annoyed", "exasperated", "fed up",
            "stuck", "helpless", "struggling", "difficult", "hard",
            "stuck in a loop", "nowhere", "unable"
        ],
        Emotion.HOPEFUL: [
            "hope", "hopeful", "possible", "can", "will", "believe",
            "confident", "optimistic", "opportunity", "chance", "better",
            "improve", "progress", "forward"
        ],
        Emotion.DEPRESSED: [
            "depressed", "depression", "suicidal", "kill myself", "harm",
            "worthless", "burden", "pointless", "numb", "empty",
            "void", "dark", "no point", "give up"
        ]
    }

    # Crisis keywords
    CRISIS_KEYWORDS = [
        "suicide", "kill myself", "hurt myself", "self harm",
        "end my life", "die", "overdose", "hang", "jump",
        "cut myself", "harm myself", "no reason to live",
        "better off dead", "everyone would be better",
        "worthless", "burden to everyone"
    ]

    def __init__(self):
        """Initialize sentiment analyzer"""
        self.emotions = list(Emotion)

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment using TextBlob-style approach
        Returns: {polarity_score: 0-1, emotion_scores: {emotion: score}}
        """
        text_lower = text.lower()

        # Calculate polarity based on positive/negative words
        positive_words = [
            "good", "great", "excellent", "wonderful", "perfect", "amazing",
            "awesome", "fantastic", "love", "happy", "glad", "better",
            "improve", "progress", "hope", "thank", "appreciate"
        ]
        negative_words = [
            "bad", "terrible", "awful", "horrible", "hate", "sad", "angry",
            "depressed", "anxious", "stress", "worry", "problem", "issue",
            "difficult", "hard", "struggle", "fail", "worse", "down"
        ]

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        total = positive_count + negative_count

        if total == 0:
            polarity_score = 0.5  # Neutral
        else:
            polarity_score = positive_count / (positive_count + negative_count)
            polarity_score = max(0.0, min(1.0, polarity_score))

        # Calculate emotion scores
        emotion_scores = self._calculate_emotion_scores(text_lower)

        return {
            "polarity_score": round(polarity_score, 3),
            "emotion_scores": emotion_scores
        }

    def _calculate_emotion_scores(self, text_lower: str) -> Dict[str, float]:
        """Calculate scores for each emotion based on keyword matches"""
        emotion_scores = {}
        text_words = text_lower.split()

        for emotion in self.emotions:
            keywords = self.EMOTION_KEYWORDS.get(emotion, [])
            matches = sum(
                1 for word in text_words
                if any(keyword in word for keyword in keywords)
            )
            # Normalize score 0-1
            score = min(1.0, matches / max(1, len(keywords) / 2))
            emotion_scores[emotion.value] = round(score, 3)

        return emotion_scores

    def detect_emotion(self, text: str) -> Tuple[str, float]:
        """
        Detect primary emotion from text
        Returns: (emotion_name, confidence_score)
        """
        emotion_scores = self._calculate_emotion_scores(text.lower())

        if not emotion_scores or max(emotion_scores.values()) == 0:
            return Emotion.NEUTRAL.value, 0.5

        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        confidence = emotion_scores[primary_emotion]

        return primary_emotion, confidence

    def detect_crisis(self, text: str) -> bool:
        """
        Detect if user is in crisis
        Returns: True if crisis indicators found
        """
        text_lower = text.lower()
        crisis_score = sum(
            1 for keyword in self.CRISIS_KEYWORDS
            if keyword in text_lower
        )
        return crisis_score >= 1

    def get_polarity(self, text: str) -> Tuple[str, float]:
        """
        Get sentiment polarity
        Returns: (polarity_type, score)
        """
        sentiment_data = self.analyze_sentiment(text)
        polarity_score = sentiment_data["polarity_score"]

        if polarity_score >= 0.6:
            return "positive", polarity_score
        elif polarity_score <= 0.4:
            return "negative", 1.0 - polarity_score
        else:
            return "neutral", 0.5

    def get_intensity(self, emotion_scores: Dict[str, float]) -> str:
        """
        Determine intensity based on emotion scores
        Returns: "low", "medium", or "high"
        """
        max_score = max(emotion_scores.values()) if emotion_scores else 0

        if max_score >= 0.7:
            return "high"
        elif max_score >= 0.4:
            return "medium"
        else:
            return "low"

    def get_mental_health_response(
        self, emotion: str, polarity: str, text: str
    ) -> Tuple[str, str]:
        """
        Generate appropriate mental health response based on emotion
        Returns: (response, technique_used)
        """
        text_lower = text.lower()

        # Detect if user is in crisis
        if self.detect_crisis(text):
            return (
                "I hear that you're going through a very difficult time. "
                "Please reach out to crisis support: National Suicide Prevention Lifeline 1-800-273-8255 "
                "or Crisis Text Line (text HOME to 741741). Your life matters, and help is available.",
                "crisis_intervention"
            )

        # Respond based on emotion
        if emotion == "depressed":
            return (
                "I understand you're feeling down. Let's focus on small positive steps. "
                "Even tiny actions like taking a short walk or talking to someone can help. "
                "What's one small thing that usually makes you feel a bit better?",
                "behavioral_activation"
            )

        elif emotion == "anxious":
            return (
                "Anxiety can be overwhelming. Let's try a grounding technique: "
                "Name 5 things you see, 4 things you can touch, 3 things you hear, 2 things you smell, and 1 thing you taste. "
                "This can help bring you back to the present moment.",
                "grounding_technique"
            )

        elif emotion == "angry":
            return (
                "I notice you're feeling frustrated. That's valid. "
                "Sometimes stepping away for a moment can help. "
                "Would it help to talk about what triggered this, or would you prefer a break?",
                "emotion_validation"
            )

        elif emotion == "sad":
            return (
                "It sounds like you're dealing with sadness. That's a human emotion, and it's okay to feel it. "
                "Is there someone you can talk to, or would you like to explore what might help right now?",
                "emotional_support"
            )

        elif emotion in ["happy", "excited", "hopeful"]:
            return (
                "That's wonderful! I'm glad you're feeling positive. "
                "Remember this moment - these positive feelings are real and important. "
                "What's contributing to your good mood?",
                "positive_reinforcement"
            )

        elif emotion == "calm":
            return (
                "It's great that you're feeling calm. Hold onto this state. "
                "You might want to remember what helps you feel this way for future moments when you need it.",
                "mindfulness"
            )

        else:
            return (
                "Thank you for sharing. I'm here to listen and support you. "
                "How are you feeling right now, and what's on your mind?",
                "active_listening"
            )


# Create global analyzer instance
analyzer = SentimentAnalyzer()
