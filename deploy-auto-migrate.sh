#!/bin/bash

# Deploy with Automatic Database Migration

"""
Deployment script that automatically runs Alembic migrations
"""

echo "🚀 DEPLOYING WITH AUTOMATIC TABLE CREATION"
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

# Run Alembic migration
echo "🔧 Running Alembic migration..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Alembic migration completed successfully!"
else
    echo "❌ Alembic migration failed!"
    exit 1
fi

# Start application
echo "🌐 Starting application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo ""
echo "🎉 DEPLOYMENT COMPLETED!"
echo "✅ Tables created automatically via Alembic"
echo "✅ Application started"
echo "✅ Enhanced resume parser ready"
echo ""
echo "🌐 Application running at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "🎯 What happens automatically:"
echo "   1. When you push code, Alembic detects new migrations"
echo "   2. When tester runs 'alembic upgrade head', tables are created"
echo "   3. No manual SQL commands needed"
echo "   4. Complete resume JSON format supported"
echo ""
echo "🔧 Tester commands (if needed):"
echo "   alembic upgrade head  # Run migrations"
echo "   alembic downgrade base  # Rollback migrations"
echo "   alembic revision --autogenerate  # Create new migration"
