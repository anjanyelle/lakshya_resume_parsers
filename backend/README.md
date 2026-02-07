# Resume Parser Backend

Production-ready FastAPI backend for uploading and parsing resumes.

## Features

- FastAPI with versioned API routes and CORS
- SQLAlchemy models with Alembic migrations
- PostgreSQL support
- File upload storage for resumes
- JWT utilities and password hashing
- Health endpoint and structured error handling

## Requirements

- Python 3.11+
- PostgreSQL 13+
- Poetry

## Setup

1. Install dependencies:
   ```bash
   cd backend
   poetry install
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   ```

   Or export variables directly:
   ```bash
   export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/resume_parser
   export SECRET_KEY=change_me
   export STORAGE_DIR=./storage
   ```

3. Create database and run migrations:
   ```bash
   poetry run alembic upgrade head
   ```

4. Start the server:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

## Configuration

Environment variables available in `.env.example`:

- `APP_NAME` - App title
- `ENVIRONMENT` - Environment name (development/staging/production)
- `API_V1_STR` - API base path
- `LOG_LEVEL` - Logging level
- `DATABASE_URL` - SQLAlchemy database URL
- `DB_POOL_SIZE` - Connection pool size
- `DB_MAX_OVERFLOW` - Max overflow connections
- `DB_POOL_TIMEOUT` - Pool timeout in seconds
- `SECRET_KEY` - JWT signing key
- `ALGORITHM` - JWT algorithm
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token TTL in minutes
- `STORAGE_DIR` - Storage directory for uploads
- `UPLOAD_MAX_SIZE_MB` - Max upload size in MB
- `ALLOWED_UPLOAD_EXTENSIONS` - Comma-separated list of extensions
- `CORS_ORIGINS` - Comma-separated list of allowed origins

## API

- `GET /api/v1/health` - Health check
- `POST /api/v1/upload` - Upload a resume file

## Notes

- Uploaded files are stored in `STORAGE_DIR` (default `./storage`).
- Update `DATABASE_URL` in `.env` to your Postgres instance.
- `CORS_ORIGINS` accepts a comma-separated list like `http://localhost:3000`.