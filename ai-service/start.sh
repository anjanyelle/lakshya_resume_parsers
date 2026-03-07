#!/bin/bash

# AI Service Startup Script
# Starts the Resume Parser AI service with proper environment setup

echo "🚀 Starting Resume Parser AI Service"
echo "====================================="

# Check if we're in the correct directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the ai-service directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if Tesseract is available
echo "🔍 Checking Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract is available: $(tesseract --version | head -1)"
else
    echo "⚠️  Warning: Tesseract OCR not found. PDF OCR functionality will be limited."
    echo "   Install with: brew install tesseract (macOS) or apt-get install tesseract-ocr (Ubuntu)"
fi

# Create test_files directory if it doesn't exist
if [ ! -d "test_files" ]; then
    echo "📁 Creating test_files directory..."
    mkdir -p test_files
fi

# Start the service
echo "🌟 Starting FastAPI service..."
echo "   Service will be available at: http://localhost:8000"
echo "   API docs at: http://localhost:8000/docs"
echo "   Press Ctrl+C to stop the service"
echo ""

# Start with uvicorn
python main.py
