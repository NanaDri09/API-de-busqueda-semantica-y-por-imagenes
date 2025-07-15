#!/usr/bin/env python3
"""
Production-like server runner for the Semantic Search API
This runs the server without auto-reload to avoid file watching issues
"""

import uvicorn
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

if __name__ == "__main__":
    print("🚀 Starting Semantic Search API (Production Mode)")
    print("=" * 50)
    print("📍 Server will run on: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("⚠️  Auto-reload is DISABLED for stability")
    print("=" * 50)
    
    # Run the server without auto-reload
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disabled for stability
        log_level="info",
        access_log=True
    ) 