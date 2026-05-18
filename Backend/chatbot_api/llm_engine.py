"""
LLM Engine for enhanced AI responses
Supports Groq and Google Gemini with fallback to rule-based responses
"""

import os
from typing import Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "500"))
LLM_FALLBACK_ENABLED = os.getenv("LLM_FALLBACK_ENABLED", "true").lower() == "true"
GROQ_MODEL = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")

# Initialize LLM clients
groq_client = None
gemini_client = None

if GROQ_API_KEY and GROQ_API_KEY != "gsk_YOUR_GROQ_API_KEY_HERE":
    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq LLM initialized")
    except Exception as e:
        print(f"⚠️ Failed to initialize Groq: {e}")

if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_client = genai.GenerativeModel(GEMINI_MODEL)
        print("✅ Google Gemini initialized")
    except Exception as e:
        print(f"⚠️ Failed to initialize Gemini: {e}")


class LLMEngine:
    """
    LLM-powered response generation with fallback support
    """

    @staticmethod
    def generate_response(
        user_message: str,
        emotion: str,
        polarity: str,
        system_context: Optional[str] = None
    ) -> Tuple[str, bool, Optional[str]]:
        """
        Generate AI response using LLM
        
        Args:
            user_message: User's message
            emotion: Detected emotion
            polarity: Message polarity (positive/negative/neutral)
            system_context: Additional context for the response
            
        Returns:
            (response_text, success, error_message)
        """
        
        # Build system prompt
        system_prompt = f"""You are KAIROS, a compassionate and empathetic mental health support chatbot. 
Your role is to:
- Provide emotional support and validation
- Suggest evidence-based coping strategies
- Encourage professional help when needed
- Maintain confidentiality and non-judgment
- Be warm, understanding, and genuinely caring

User's detected emotion: {emotion}
Message sentiment: {polarity}
{f'Additional context: {system_context}' if system_context else ''}

Respond with warmth and empathy. Keep responses concise (2-3 sentences). 
If the user shows signs of crisis, provide crisis resources."""

        # Try Groq first if available
        if groq_client and LLM_PROVIDER == "groq":
            try:
                return LLMEngine._query_groq(user_message, system_prompt)
            except Exception as e:
                error_msg = f"Groq error: {str(e)}"
                if not LLM_FALLBACK_ENABLED:
                    return "", False, error_msg

        # Try Gemini if available
        if gemini_client and LLM_PROVIDER == "gemini":
            try:
                return LLMEngine._query_gemini(user_message, system_prompt)
            except Exception as e:
                error_msg = f"Gemini error: {str(e)}"
                if not LLM_FALLBACK_ENABLED:
                    return "", False, error_msg

        # Return success (fallback will be handled by caller)
        return "", True, None

    @staticmethod
    def _query_groq(user_message: str, system_prompt: str) -> Tuple[str, bool, Optional[str]]:
        """Query Groq LLM"""
        try:
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                max_tokens=LLM_MAX_TOKENS,
                temperature=LLM_TEMPERATURE,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            
            if response.choices and response.choices[0].message:
                return response.choices[0].message.content, True, None
            return "", False, "No response from Groq"
        except Exception as e:
            return "", False, str(e)

    @staticmethod
    def _query_gemini(user_message: str, system_prompt: str) -> Tuple[str, bool, Optional[str]]:
        """Query Google Gemini LLM"""
        try:
            full_prompt = f"{system_prompt}\n\nUser: {user_message}"
            response = gemini_client.generate_content(full_prompt)
            
            if response and response.text:
                return response.text, True, None
            return "", False, "No response from Gemini"
        except Exception as e:
            return "", False, str(e)

    @staticmethod
    def is_llm_available() -> bool:
        """Check if any LLM provider is available"""
        return groq_client is not None or gemini_client is not None

    @staticmethod
    def get_provider_status() -> dict:
        """Get status of LLM providers"""
        return {
            "groq_available": groq_client is not None,
            "gemini_available": gemini_client is not None,
            "active_provider": LLM_PROVIDER if (groq_client is not None or gemini_client is not None) else None,
            "fallback_enabled": LLM_FALLBACK_ENABLED
        }


# Initialize LLM engine
llm_engine = LLMEngine()
