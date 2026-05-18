"""
Mood Tracker API Entry Point
Run this file to start the Mood Tracker API server
"""

import uvicorn
import sys

if __name__ == "__main__":
    try:
        print("🚀 Starting KAIROS Mood Tracker API...")
        print("📊 Port: 8000")
        print("📝 Docs: http://127.0.0.1:8000/docs")
        print()
        
        uvicorn.run(
            "app:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n✋ Mood Tracker API stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
