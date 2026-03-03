#!/bin/bash

# Production startup script for Render
echo "Starting Resume Parser API..."

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z $DATABASE_HOST 5432; do
  sleep 1
done
echo "Database is ready!"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Create storage directories
echo "Creating storage directories..."
mkdir -p storage/uploads

# Start the application
echo "Starting FastAPI application..."
exec gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --timeout 120 --max-requests 1000 --max-requests-jitter 50
