#!/bin/bash

# Start Backend Service (Candidate Management + Skill Extraction)
# This is the service with the skill extraction enhancement

echo "🚀 Starting Backend Service..."
echo "📁 Location: /backend"
echo "🔧 Service: Candidate Management + Skill Extraction APIs"
echo ""

cd "$(dirname "$0")/backend"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Kill any existing uvicorn process on port 3001
echo "🔄 Checking for existing processes on port 3001..."
lsof -ti:3001 | xargs kill -9 2>/dev/null || true

# Start the backend service
echo ""
echo "🚀 Starting Backend on http://localhost:3001"
echo "📊 API Docs: http://localhost:3001/docs"
echo "🔍 Health Check: http://localhost:3001/health"
echo ""
echo "New Endpoints:"
echo "  - GET /api/v1/candidates/{id}/skills/categorized"
echo "  - GET /api/v1/candidates/{id}/skills/summary"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 3001
