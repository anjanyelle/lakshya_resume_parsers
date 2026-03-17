#!/bin/bash

# Deploy with Auto Table Creation

"""
Deployment script that ensures tables are created automatically
"""

echo "🚀 DEPLOYING WITH AUTO TABLE CREATION"
echo "============================================"

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "❌ Backend directory not found!"
    exit 1
fi

cd backend

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run with auto table creation
echo "🔧 Starting with automatic table creation..."

# Option 1: Using docker-compose
if command -v docker-compose &> /dev/null; then
    echo "🐳 Using Docker Compose with auto table creation..."
    docker-compose -f docker-compose.auto-tables.yml up --build
else
    # Option 2: Direct Python
    echo "🐍 Starting directly with auto table creation..."
    python -c "
import logging
from app.startup_hooks import ensure_complete_resume_tables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info('🚀 Auto-creating complete resume tables...')
    ensure_complete_resume_tables()
    logger.info('✅ Complete resume tables ensured!')
    logger.info('🎉 Starting application...')
except Exception as e:
    logger.error(f'❌ Error creating tables: {e}')
    raise

# Start the application
echo "🌐 Starting application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo ""
echo "🎉 DEPLOYMENT COMPLETED!"
echo "✅ Tables created automatically"
echo "✅ Application started"
echo "✅ Enhanced resume parser ready"
echo ""
echo "🌐 Application running at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "🎯 Next Steps:"
echo "   1. Upload a resume to test complete JSON parsing"
echo "   2. Check pgAdmin to see new tables populated"
echo "   3. Verify ML-enhanced accuracy improvements"
