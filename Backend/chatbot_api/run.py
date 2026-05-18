#!/usr/bin/env python
"""
Startup script for KAIROS Chatbot API
Run this script to start the API server on port 8001
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the API server"""
    
    print("=" * 60)
    print("KAIROS Chatbot API Startup")
    print("=" * 60)
    
    # Get script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    print(f"\nWorking directory: {script_dir}")
    print(f"Python version: {sys.version}")
    
    # Check if requirements are installed
    print("\n📦 Checking dependencies...")
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ All dependencies installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n📥 Installing requirements...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("✅ Dependencies installed")
    
    # Import app
    print("\n🚀 Starting Chatbot API server...")
    print("\nServer Details:")
    print("  • Host: http://127.0.0.1:8001")
    print("  • Docs: http://127.0.0.1:8001/docs")
    print("  • ReDoc: http://127.0.0.1:8001/redoc")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        import uvicorn

        uvicorn.run(
            "app:app",
            host="127.0.0.1",
            port=8001,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n⛔ Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
