"""
Machine Learning Models for Mood Classification
Includes Random Forest, Gradient Boosting, and Ensemble Voting Classifier
"""

import numpy as np
import pickle
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import os


class MoodClassifier:
    """
    Ensemble mood classification model combining multiple algorithms
    Uses TF-IDF vectorization for text features
    """

    def __init__(self):
        """Initialize the mood classifier with pre-trained or dummy models"""
        self.moods = [
            "energized_positive", "calm_content", "neutral_balanced",
            "anxious_overwhelmed", "sad_withdrawn", "frustrated_irritable"
        ]
        
        # Initialize TF-IDF Vectorizer
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        
        # Initialize models
        self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        self.gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42, max_depth=5)
        
        # Ensemble voting classifier
        self.ensemble = VotingClassifier(
            estimators=[
                ('rf', self.rf_model),
                ('gb', self.gb_model)
            ],
            voting='soft'
        )
        
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        self.feature_importance = {}
        
    def _generate_synthetic_training_data(self, n_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate synthetic training data for demo purposes
        In production, use real training dataset
        """
        # Sample texts representing different moods
        mood_texts = {
            "energized_positive": [
                "I feel great and energized", "Feeling wonderful and excited",
                "Amazing day, so happy", "Energetic and motivated", "Feeling fantastic"
            ],
            "calm_content": [
                "I feel peaceful and calm", "Content and at ease", "Relaxed and comfortable",
                "Serene and satisfied", "Feeling balanced"
            ],
            "neutral_balanced": [
                "I feel okay today", "Neutral mood", "Nothing special happening",
                "Just going through the day", "Average day"
            ],
            "anxious_overwhelmed": [
                "I feel anxious and worried", "Overwhelmed and stressed",
                "Nervous and afraid", "Panicked and tense", "So much anxiety"
            ],
            "sad_withdrawn": [
                "I feel sad and down", "Depressed and hopeless", "Withdrawn and lonely",
                "Heartbroken and miserable", "Very sad today"
            ],
            "frustrated_irritable": [
                "I feel frustrated and angry", "Irritated and annoyed",
                "Furious and resentful", "Fed up and bitter", "Very frustrated"
            ]
        }
        
        texts = []
        labels = []
        
        for mood, text_samples in mood_texts.items():
            # Repeat samples to create training set
            for _ in range(n_samples // len(mood_texts)):
                texts.append(np.random.choice(text_samples))
                labels.append(mood)
        
        # Vectorize texts
        X = self.vectorizer.fit_transform(texts).toarray()
        y = self.label_encoder.fit_transform(labels)
        
        return X, y
    
    def train(self, texts: Optional[List[str]] = None, labels: Optional[List[str]] = None):
        """
        Train the ensemble model
        If no data provided, trains on synthetic data
        """
        if texts is None or labels is None:
            # Generate synthetic data for demo
            X, y = self._generate_synthetic_training_data(500)
        else:
            X = self.vectorizer.fit_transform(texts).toarray()
            y = self.label_encoder.fit_transform(labels)
        
        # Train ensemble
        self.ensemble.fit(X, y)
        self.is_trained = True
        
        # Store feature importance from Random Forest (after training)
        try:
            feature_names = self.vectorizer.get_feature_names_out()
            if self.rf_model.feature_importances_ is not None:
                self.feature_importance = {
                    feature_names[i]: self.rf_model.feature_importances_[i]
                    for i in range(len(feature_names))
                }
        except Exception as e:
            # If feature importance fails, just continue
            self.feature_importance = {}
    
    def predict(self, text: str) -> Dict[str, float]:
        """
        Predict mood from text
        Returns confidence scores for each mood
        """
        if not self.is_trained:
            self.train()
        
        # Vectorize text
        X = self.vectorizer.transform([text]).toarray()
        
        # Get probabilities from ensemble
        probabilities = self.ensemble.predict_proba(X)[0]
        
        # Map to mood labels
        mood_scores = {
            mood: float(prob)
            for mood, prob in zip(self.moods, probabilities)
        }
        
        return mood_scores
    
    def predict_with_confidence(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        """
        Predict mood with confidence and all scores
        Returns: (predicted_mood, confidence, all_scores)
        """
        scores = self.predict(text)
        predicted_mood = max(scores, key=scores.get)
        confidence = scores[predicted_mood]
        return predicted_mood, confidence, scores


class MoodTrendAnalyzer:
    """
    Analyzes mood trends over time
    Calculates statistics and recommendations
    """
    
    def __init__(self):
        self.mood_to_numeric = {
            "energized_positive": 4,
            "calm_content": 3,
            "neutral_balanced": 2,
            "anxious_overwhelmed": 1,
            "sad_withdrawn": 0,
            "frustrated_irritable": 1
        }
    
    def calculate_trend(self, mood_history: List[Dict]) -> Dict:
        """
        Calculate trend direction and statistics
        """
        if not mood_history:
            return {
                "trend": "no_data",
                "direction": "neutral",
                "average_mood": "neutral_balanced",
                "recommendation": "No mood data available"
            }
        
        # Extract moods
        moods = [record["mood"] for record in mood_history]
        mood_values = [self.mood_to_numeric.get(m, 2) for m in moods]
        
        # Calculate trend
        if len(mood_values) >= 2:
            recent_avg = np.mean(mood_values[-3:] if len(mood_values) >= 3 else mood_values[-2:])
            older_avg = np.mean(mood_values[:-3] if len(mood_values) > 3 else [mood_values[0]])
            
            if recent_avg > older_avg + 0.5:
                trend_direction = "improving"
            elif recent_avg < older_avg - 0.5:
                trend_direction = "declining"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "stable"
        
        # Get most common mood
        most_common_mood = max(set(moods), key=moods.count)
        
        # Generate recommendations
        recommendations = self._get_recommendations(most_common_mood, trend_direction)
        
        return {
            "trend_direction": trend_direction,
            "average_mood": most_common_mood,
            "recent_count": len(mood_values),
            "recommendations": recommendations
        }
    
    def _get_recommendations(self, mood: str, trend: str) -> List[str]:
        """Generate personalized recommendations based on mood and trend"""
        recommendations_map = {
            "energized_positive": {
                "improving": ["Keep up the positive momentum!", "Maintain your current activities"],
                "declining": ["Try to preserve this energy", "Engage in activities you enjoy"],
                "stable": ["Continue your current routine", "Share your positivity with others"]
            },
            "calm_content": {
                "improving": ["You're doing great!", "Maintain this peaceful state"],
                "declining": ["Be gentle with yourself", "Practice mindfulness"],
                "stable": ["You have good balance", "Consider deepening your practice"]
            },
            "neutral_balanced": {
                "improving": ["Things are getting better", "Build on this momentum"],
                "declining": ["Try engaging activities", "Consider talking to someone"],
                "stable": ["Seek ways to boost your mood", "Try new activities"]
            },
            "anxious_overwhelmed": {
                "improving": ["Great progress!", "Keep using your coping strategies"],
                "declining": ["Use grounding techniques", "Reach out for support"],
                "stable": ["Practice breathing exercises", "Consider talking to a therapist"]
            },
            "sad_withdrawn": {
                "improving": ["You're making progress!", "Keep moving forward"],
                "declining": ["Please reach out for support", "Consider professional help"],
                "stable": ["You deserve support", "Connect with loved ones"]
            },
            "frustrated_irritable": {
                "improving": ["Your frustration is easing", "Keep this up"],
                "declining": ["Take breaks when needed", "Practice stress relief"],
                "stable": ["Identify triggers", "Try relaxation techniques"]
            }
        }
        
        return recommendations_map.get(mood, {}).get(trend, ["Take care of yourself"])
    
    def calculate_statistics(self, mood_history: List[Dict]) -> Dict:
        """Calculate mood statistics"""
        if not mood_history:
            return {}
        
        moods = [record["mood"] for record in mood_history]
        
        # Count occurrences
        mood_counts = {}
        for mood in moods:
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        # Calculate variety (entropy-like measure)
        total = len(moods)
        variety = sum(-(count/total) * np.log(count/total) for count in mood_counts.values() if count > 0)
        variety = variety / np.log(len(set(moods))) if len(set(moods)) > 1 else 0
        
        return {
            "total_records": len(moods),
            "most_common": max(mood_counts, key=mood_counts.get),
            "mood_distribution": mood_counts,
            "variety_score": float(variety)
        }


# Initialize global classifier
mood_classifier = MoodClassifier()
trend_analyzer = MoodTrendAnalyzer()
