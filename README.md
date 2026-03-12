Resume Parser Fine-Tuning Project

This repository includes a resume parsing system and a small synthetic dataset
generator for fine-tuning or evaluation.

## Database setup (required)

The API and parsing pipeline use **PostgreSQL**. You need a running Postgres instance and must run migrations before starting the backend.

- **PostgreSQL** – required (candidates, parsing jobs, skills, etc.).
- **Redis** – optional; only for Celery workers (async parsing). For local dev with `PARSING_MODE=deterministic` or `text_only`, the app can run without Redis.

### Option A: Postgres + Redis with Docker

From project root:

```bash
docker compose up -d postgres redis
```

Set in `backend/.env` (match user/password if you set `POSTGRES_USER` / `POSTGRES_PASSWORD` in root `.env` for Docker):

```env
DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/resume_parser"
```

### Option B: Local PostgreSQL

1. Install PostgreSQL (e.g. Postgres.app or `brew install postgresql@14`).
2. Create DB: `createdb resume_parser`
3. In `backend/.env`:

```env
DATABASE_URL="postgresql+psycopg2://USER:PASSWORD@localhost:5432/resume_parser"
```

### Migrations and seed (from backend directory)

```bash
cd backend
poetry install
poetry run alembic upgrade head
poetry run python scripts/init_db.py
```

Then start the API: `poetry run uvicorn app.main:app --reload`

### Deployed on Render – 503 or "Database schema not ready"

**Root cause:** The APIs return 503 or 400 when the database is **missing tables** (`candidates`, `parsing_jobs`, `audit_logs`, etc.). This often happens if:

- The database was created empty and Alembic reports "Migrations completed" but the schema was never applied (e.g. DB already marked at `head` from another app), or
- Migrations failed silently or ran against a different `DATABASE_URL`.

**What we do automatically:**

- Startup runs `alembic upgrade head` then `Base.metadata.create_all(..., checkfirst=True)` so missing tables are created if possible.
- Register/login/upload catch missing-table errors and either return a clear 503 or, for register, still return success and only skip audit logging.

**Permanent fix (recommended):**

1. In Render Dashboard, create a **new PostgreSQL** instance (or use one that has never had this app’s migrations run).
2. Set the backend service’s **DATABASE_URL** to that new database.
3. Redeploy. On first start, `alembic upgrade head` will run from scratch and create all tables.

After that, register, login, and upload should work without 503.

---

Quick Start
- Generate dataset files:
  - python scripts/prepare_dataset.py

Outputs
- data/train.jsonl
- data/val.jsonl

Each JSONL line has:
{
  "input": "<raw resume text>",
  "output": "<stringified JSON with structured fields>"
}

Notes
- The dataset generator includes 5 diverse examples.
- Intended for local experimentation and prompt/finetune iteration.






anjanyelle@Hello backend % poetry run uvicorn app.main:app --reload



poetry run uvicorn app.main:app --reload


poetry --version


poetry install
poetry run uvicorn app.main:app --reload


Fast mode added: PARSING_MODE=deterministic
Now you have 3 modes:

text_only = extract text only
deterministic = fast parse without any LLM but still saves to DB
full = everything including LLM
In deterministic, the workflow is:

extract_text → clean_text → detect_sections → extract_contact_info → parse_work_experience → parse_education → parse_certifications → extract_skills → taxonomy_mapping → calculate_confidence → save_to_database

So you should get:





APP_NAME="Resume Parser API"
ENVIRONMENT=development
API_V1_STR=/api/v1
LOG_LEVEL=INFO

DATABASE_URL="postgresql+psycopg2://postgres:Anjan%24123@localhost:5432/resume_parser"
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

SECRET_KEY=change_me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

STORAGE_DIR=./storage
UPLOAD_MAX_SIZE_MB=20
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
ALLOWED_UPLOAD_EXTENSIONS=["pdf","doc","docx","txt","rtf","png","jpg","jpeg"]

CLAMAV_ENABLED=false
CLAMAV_PATH=clamscan
1. Install Prerequisites
bash
# Install Node.js 18+ (if not installed)
# macOS: brew install node
# Ubuntu: sudo apt install nodejs npm
 
# Install Python 3.10+ (if not installed)
# macOS: brew install python@3.10
# Ubuntu: sudo apt install python3.10 python3.10-venv
 
# Install PostgreSQL 14+ (if not installed)
# macOS: brew install postgresql@14 && brew services start postgresql@14
# Ubuntu: sudo apt install postgresql postgresql-contrib
 
# Install Redis 7+ (if not installed)
# macOS: brew install redis && brew services start redis
# Ubuntu: sudo apt install redis-server && sudo systemctl start redis
2. Setup Database
bash
# Create database
psql -U postgres -c "CREATE DATABASE resume_parser;"
 
# Run schema setup
cd /Users/anjanyelle/Desktop/untitled\ folder\ 3/Lakshya-LLM-Resume-Parser
psql -U postgres -d resume_parser -f backend/src/database/setup.sql
 
# Run migrations
psql -U postgres -d resume_parser -f backend/migrations/003_add_labeling_table.sql
3. Setup Backend (Node.js)
bash
cd "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src"
 
# Copy and edit environment file
cp .env.example .env
# Edit .env with your settings:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/resume_parser
# JWT_SECRET=your_secret_key_here
# REDIS_URL=redis://localhost:6379
# AI_SERVICE_URL=http://localhost:8000
 
# Install dependencies
npm install
 
# Start backend (keep this terminal open)
npm run dev
# Backend runs on http://localhost:3001
4. Setup AI Service (Python)
bash
cd "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/ai-service"
 
# Create virtual environment
python3 -m venv venv
source venv/bin/activate
 
# Install dependencies
pip install -r requirements.txt
 
# Download spaCy model
python -m spacy download en_core_web_sm
 
# Copy environment file
cp .env.example .env
 
# Start AI service (keep this terminal open)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# AI service runs on http://localhost:8000
5. Setup Frontend (React)
bash
cd "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/frontend"
 
# Install dependencies
npm install
 
# Start frontend (keep this terminal open)
npm run dev
# Frontend runs on http://localhost:5173
6. Create Admin User
bash
cd "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend"
 
# Create admin account
python create_admin_user.py
# Follow prompts to set email and password
7. Verify Everything Works
Open your browser and go to http://localhost:5173

You should see the login page. Use the admin credentials you created to log in.

Quick Terminal Summary (3 terminals needed)
Terminal 1 (Backend):

bash
cd backend/src
npm run dev
Terminal 2 (AI Service):

bash
cd ai-service
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
Terminal 3 (Frontend):

source venv/bin/activate
 
# Start the AI service
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
 
# Start the AI service
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

bash
cd backend
python create_admin_user.py
Then visit http://localhost:5173 and log in.

If Something Goes Wrong
Error	Fix
psql: command not found	Install PostgreSQL client tools: brew install postgresql
python: command not found	Use python3 instead of python
uvicorn: command not found	Make sure you activated the venv: source ai-service/venv/bin/activate
Frontend shows blank page	Check that backend and AI service are running first
Database connection failed	Verify PostgreSQL is running and DATABASE_URL is correct in .env
The app should now be fully running locally on your machine.
python3 create_admin_simple.py
