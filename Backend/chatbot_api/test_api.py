"""
Test script for KAIROS Chatbot API
Run this to verify all endpoints are working correctly
"""

import requests
import json
from datetime import datetime

# API Configuration
API_URL = "http://127.0.0.1:8001"
USER_ID = "test_user_123"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_test(name, passed, response=None):
    """Print test result"""
    status = f"{Colors.OKGREEN}✅ PASS{Colors.ENDC}" if passed else f"{Colors.FAIL}❌ FAIL{Colors.ENDC}"
    print(f"  {status} | {name}")
    if response and not passed:
        print(f"    Error: {response}")


def test_health():
    """Test health check endpoint"""
    print(f"\n{Colors.BOLD}Testing Health Endpoint{Colors.ENDC}")
    try:
        response = requests.get(f"{API_URL}/health")
        passed = response.status_code == 200
        print_test("GET /health", passed, response.text if not passed else None)
        if passed:
            print(f"    Response: {response.json()}")
        return passed
    except Exception as e:
        print_test("GET /health", False, str(e))
        return False


def test_chat():
    """Test chat endpoint"""
    print(f"\n{Colors.BOLD}Testing Chat Endpoint{Colors.ENDC}")
    
    test_messages = [
        "I'm feeling great today!",
        "I've been anxious lately",
        "Thank you for listening",
        "I'm struggling with my emotions"
    ]
    
    for message in test_messages:
        try:
            payload = {
                "user_id": USER_ID,
                "message": message
            }
            response = requests.post(
                f"{API_URL}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            passed = response.status_code == 200
            print_test(f"POST /chat - '{message[:30]}...'", passed, response.text if not passed else None)
            
            if passed:
                data = response.json()
                print(f"    Emotion: {Colors.OKCYAN}{data.get('sentiment', {}).get('detected_emotion')}{Colors.ENDC}")
                print(f"    Polarity: {Colors.OKCYAN}{data.get('sentiment', {}).get('polarity')}{Colors.ENDC}")
                print(f"    Crisis: {Colors.OKCYAN}{data.get('crisis_detected')}{Colors.ENDC}")
                print(f"    Reply: {Colors.OKCYAN}{data.get('reply')[:60]}...{Colors.ENDC}")
        except Exception as e:
            print_test(f"POST /chat - '{message[:30]}...'", False, str(e))


def test_history():
    """Test chat history endpoint"""
    print(f"\n{Colors.BOLD}Testing Chat History Endpoint{Colors.ENDC}")
    try:
        response = requests.get(
            f"{API_URL}/chat/history",
            params={"user_id": USER_ID, "limit": 10}
        )
        passed = response.status_code == 200
        print_test("GET /chat/history", passed, response.text if not passed else None)
        if passed:
            data = response.json()
            print(f"    Messages: {Colors.OKCYAN}{len(data)}{Colors.ENDC}")
            for i, msg in enumerate(data[-2:]):
                print(f"    [{i+1}] {msg.get('role')}: {msg.get('content')[:50]}...")
    except Exception as e:
        print_test("GET /chat/history", False, str(e))


def test_sentiment():
    """Test sentiment endpoint"""
    print(f"\n{Colors.BOLD}Testing Sentiment Trend Endpoint{Colors.ENDC}")
    try:
        response = requests.get(
            f"{API_URL}/chat/sentiment",
            params={"user_id": USER_ID, "days": 7}
        )
        passed = response.status_code == 200
        print_test("GET /chat/sentiment", passed, response.text if not passed else None)
        if passed:
            data = response.json()
            print(f"    Trend: {Colors.OKCYAN}{data.get('trend')}{Colors.ENDC}")
            print(f"    Avg Polarity: {Colors.OKCYAN}{data.get('average_polarity')}{Colors.ENDC}")
            print(f"    Dominant Emotion: {Colors.OKCYAN}{data.get('dominant_emotion')}{Colors.ENDC}")
            print(f"    Records: {Colors.OKCYAN}{data.get('records')}{Colors.ENDC}")
    except Exception as e:
        print_test("GET /chat/sentiment", False, str(e))


def test_current_mood():
    """Test current mood endpoint"""
    print(f"\n{Colors.BOLD}Testing Current Mood Endpoint{Colors.ENDC}")
    try:
        response = requests.get(
            f"{API_URL}/mood/current",
            params={"user_id": USER_ID}
        )
        passed = response.status_code == 200
        print_test("GET /mood/current", passed, response.text if not passed else None)
        if passed:
            data = response.json()
            print(f"    Mood: {Colors.OKCYAN}{data.get('mood')}{Colors.ENDC}")
            print(f"    Clinical: {Colors.OKCYAN}{data.get('clinical_mood')}{Colors.ENDC}")
            print(f"    Confidence: {Colors.OKCYAN}{data.get('confidence')}{Colors.ENDC}")
            print(f"    Description: {Colors.OKCYAN}{data.get('description')}{Colors.ENDC}")
    except Exception as e:
        print_test("GET /mood/current", False, str(e))


def test_set_mood():
    """Test set mood endpoint"""
    print(f"\n{Colors.BOLD}Testing Set Mood Endpoint{Colors.ENDC}")
    
    moods = ["happy", "calm", "anxious", "sad"]
    
    for mood in moods:
        try:
            payload = {
                "user_id": USER_ID,
                "mood": mood
            }
            response = requests.post(
                f"{API_URL}/mood/set",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            passed = response.status_code == 200
            print_test(f"POST /mood/set - {mood}", passed, response.text if not passed else None)
        except Exception as e:
            print_test(f"POST /mood/set - {mood}", False, str(e))


def test_clear_chat():
    """Test clear chat endpoint"""
    print(f"\n{Colors.BOLD}Testing Clear Chat Endpoint{Colors.ENDC}")
    try:
        response = requests.post(
            f"{API_URL}/chat/clear",
            params={"user_id": USER_ID}
        )
        passed = response.status_code == 200
        print_test("POST /chat/clear", passed, response.text if not passed else None)
    except Exception as e:
        print_test("POST /chat/clear", False, str(e))


def test_stats():
    """Test stats endpoint"""
    print(f"\n{Colors.BOLD}Testing Stats Endpoint{Colors.ENDC}")
    try:
        response = requests.get(
            f"{API_URL}/stats",
            params={"user_id": USER_ID}
        )
        passed = response.status_code == 200
        print_test("GET /stats", passed, response.text if not passed else None)
        if passed:
            data = response.json()
            print(f"    Total Messages: {Colors.OKCYAN}{data.get('total_messages')}{Colors.ENDC}")
            print(f"    Mood Entries: {Colors.OKCYAN}{data.get('mood_entries')}{Colors.ENDC}")
    except Exception as e:
        print_test("GET /stats", False, str(e))


def main():
    """Run all tests"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          KAIROS Chatbot API - Test Suite                   ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Configuration:{Colors.ENDC}")
    print(f"  API URL: {Colors.OKCYAN}{API_URL}{Colors.ENDC}")
    print(f"  Test User: {Colors.OKCYAN}{USER_ID}{Colors.ENDC}")
    print(f"  Timestamp: {Colors.OKCYAN}{datetime.now().isoformat()}{Colors.ENDC}")
    
    # Check if server is running
    print(f"\n{Colors.BOLD}Checking Server Connection...{Colors.ENDC}")
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            print(f"{Colors.OKGREEN}✅ Server is running!{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}❌ Server returned status {response.status_code}{Colors.ENDC}")
            return
    except requests.exceptions.ConnectionError:
        print(f"{Colors.FAIL}❌ Cannot connect to server at {API_URL}{Colors.ENDC}")
        print(f"{Colors.WARNING}   Make sure the API server is running: python run.py{Colors.ENDC}")
        return
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
        return
    
    # Run tests
    test_health()
    test_chat()
    test_history()
    test_sentiment()
    test_current_mood()
    test_set_mood()
    
    # Final stats before clearing
    test_stats()
    
    # Clear chat
    test_clear_chat()
    
    # Final summary
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                   Testing Complete! ✅                      ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Next Steps:{Colors.ENDC}")
    print(f"  1. API Docs: {Colors.OKCYAN}http://127.0.0.1:8001/docs{Colors.ENDC}")
    print(f"  2. Frontend: Connect to {Colors.OKCYAN}http://127.0.0.1:8001{Colors.ENDC}")
    print(f"  3. Keep server running for frontend integration")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Tests cancelled by user{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}Test error: {e}{Colors.ENDC}")
