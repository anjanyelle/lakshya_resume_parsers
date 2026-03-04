#!/bin/bash

echo "Starting application initialization..."

# Wait for database to be available (if needed)
echo "Running database migrations..."
alembic upgrade head

# Create admin user if not exists
echo "Creating admin user..."
python create_admin_user.py

# Start the application
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
