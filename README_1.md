# 🚀 Lakshya LLM Resume Parser — Full Setup Guide

A full-stack AI-powered resume parsing system with a **Node.js/TypeScript Backend**, **React Frontend**, **Python FastAPI AI Service**, and **PostgreSQL Database**.

---

## 📁 Project Structure

```
Lakshya-LLM-Resume-Parser/
├── backend/
│   └── src/               ← Node.js + TypeScript REST API (Express)
├── frontend/              ← React + Vite + TypeScript UI
├── ai-service/            ← Python FastAPI + LLM/NLP Parser
├── docker-compose.yml     ← Optional: run everything with Docker
└── README_1.md            ← This file
```

---

## ⚙️ Prerequisites — Install These First

Make sure the following tools are installed on your machine before proceeding:

| Tool | Version | Download |
|------|---------|----------|
| **Node.js** | v18+ | https://nodejs.org |
| **npm** | v9+ | (comes with Node.js) |
| **Python** | 3.11+ | https://www.python.org/downloads |
| **pip** | latest | (comes with Python) |
| **PostgreSQL** | 14+ | https://www.postgresql.org/download |
| **Git** | latest | https://git-scm.com |

> **Windows users:** After installing Python, make sure it is added to your system PATH.  
> To verify: open a terminal and run `python --version` and `node --version`.

---

## 🔽 Step 1 — Clone the Repository

```bash
git clone https://github.com/anjanyelle/Lakshya-LLM-Resume-Parser.git
cd Lakshya-LLM-Resume-Parser
```

---

## 🗄️ Step 2 — Database Setup (PostgreSQL)

You need a running PostgreSQL database before starting the backend.

### Option A: Local PostgreSQL

1. Open **pgAdmin** or the **psql** terminal and run:

```sql
CREATE DATABASE resume_parser;
CREATE USER resume_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE resume_parser TO resume_user;
```

2. Your connection string will be:
```
postgresql://resume_user:your_password@localhost:5432/resume_parser
```

### Option B: Use a Cloud Database (Render / Supabase / Neon)

Copy the `DATABASE_URL` from your cloud provider and paste it in the backend `.env` file (Step 3.3 below).

---

## 🖥️ Step 3 — Backend Setup (`backend/src`)

This is the **Node.js + TypeScript Express API** server.

### 3.1 — Navigate to the backend src folder

```bash
cd backend/src
```

### 3.2 — Install Node.js dependencies

```bash
npm install
```

### 3.3 — Create the `.env` file

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

Then open `.env` and fill in your values:

```env
PORT=3001
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/resume_parser
JWT_SECRET=your_super_secret_key_change_this_in_production
NODE_ENV=development

# OpenAI API Key (required for JD matching / AI features)
OPENAI_API_KEY=your_openai_api_key_here

# URL of the Python AI service (must match AI service port)
AI_SERVICE_URL=http://localhost:8000
```

### 3.4 — Initialize the Database (⚠️ First Time Only)

This command creates all tables and applies migrations:

```bash
npm run db:init
```

> This runs `db:reset` → `db:setup` → `db:migrate` in sequence.

If you want to run steps individually:

```bash
# Drop and recreate all tables
npm run db:reset

# Run initial setup SQL (creates base schema)
npm run db:setup

# Apply all pending migrations
npm run db:migrate
```

### 3.5 — Start the Backend Development Server

```bash
npm run dev
```

✅ Backend runs at: **http://localhost:3001**

> Uses `ts-node-dev` — automatically restarts on file changes.

---

## 🤖 Step 4 — AI Service Setup (`ai-service/`)

This is the **Python FastAPI** service that handles resume parsing using NLP and LLM models.

### 4.1 — Navigate to the ai-service folder

```bash
# From project root
cd ai-service

# OR if you're currently inside backend/src
cd ../../ai-service
```

### 4.2 — Create a Python Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

> ✅ You should see `(venv)` at the start of your terminal prompt after activation.

### 4.3 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ This may take **5–15 minutes** — it installs PyTorch, HuggingFace Transformers, spaCy, and other ML libraries.

### 4.4 — Download the spaCy English Language Model

```bash
python -m spacy download en_core_web_sm
```

### 4.5 — Create the `.env` file

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

Then open `.env` and configure:

```env
# Server Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=false
LOG_LEVEL=INFO

# Model Configuration
MODEL_NAME=dslim/bert-base-NER
MODEL_CACHE_DIR=./models/cache
MAX_RESUME_LENGTH=5000
CONFIDENCE_THRESHOLD=0.80

# Device: use 'cuda' if you have a NVIDIA GPU, otherwise keep 'cpu'
DEVICE=cpu
BATCH_SIZE=16
MAX_SEQUENCE_LENGTH=512

# API Settings
API_PREFIX=/api/v1
RELOAD=false
WORKERS=1
TIMEOUT=30

# LLM API Keys — add at least ONE for best parsing accuracy
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 4.6 — Start the AI Service

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ AI service runs at: **http://localhost:8000**  
📖 Swagger API docs: **http://localhost:8000/docs**

---

## 🌐 Step 5 — Frontend Setup (`frontend/`)

This is the **React + Vite + TypeScript** web application.

### 5.1 — Navigate to the frontend folder

```bash
# From project root
cd frontend

# OR if you're currently inside ai-service
cd ../frontend
```

### 5.2 — Install Node.js dependencies

```bash
npm install
```

### 5.3 — Create the `.env` file

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

Then open `.env` and set:

```env
# URL to your backend API
VITE_API_URL=http://localhost:3001/api

# App display name (optional)
VITE_APP_NAME=ResumeParser AI
```

### 5.4 — Start the Frontend Development Server

```bash
npm run dev
```

✅ Frontend runs at: **http://localhost:5173**

---

## ✅ Quick Reference — All Commands in Order

Open **3 separate terminal windows** and run one service per terminal:

---

### 🟢 Terminal 1 — Backend (Node.js Express API)

```bash
cd backend/src
npm install
npm run db:init        # ← Only needed the FIRST TIME
npm run dev
```

**Runs at:** http://localhost:3001

---

### 🟢 Terminal 2 — AI Service (Python FastAPI)

```bash
cd ai-service

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Start the service
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Runs at:** http://localhost:8000

---

### 🟢 Terminal 3 — Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

**Runs at:** http://localhost:5173

---

## 🔗 Service URLs At a Glance

| Service | URL | Notes |
|---------|-----|-------|
| **Frontend (Web UI)** | http://localhost:5173 | Main application |
| **Backend REST API** | http://localhost:3001/api | Node.js Express |
| **AI Service** | http://localhost:8000 | Python FastAPI |
| **AI Service Docs** | http://localhost:8000/docs | Swagger UI |

---

## 🐳 Optional — Run Everything with Docker

If you have **Docker** and **Docker Compose** installed:

```bash
# From the project root directory
docker-compose up --build
```

For development mode:
```bash
docker-compose -f docker-compose.dev.yml up --build
```

To stop all containers:
```bash
docker-compose down
```

---

## 🛠️ All Available Commands

### Backend (`backend/src`)

| Command | Description |
|---------|-------------|
| `npm install` | Install all Node.js dependencies |
| `npm run dev` | Start dev server with hot-reload |
| `npm run build` | Compile TypeScript → JavaScript |
| `npm run start` | Start production server (requires build first) |
| `npm run db:init` | Full DB setup: reset + setup + migrate (first time) |
| `npm run db:reset` | Drop and recreate all database tables |
| `npm run db:setup` | Run initial setup SQL |
| `npm run db:migrate` | Apply all pending migrations |
| `npm run clean` | Delete compiled `dist/` folder |

---

### AI Service (`ai-service/`)

| Command | Description |
|---------|-------------|
| `python -m venv venv` | Create virtual environment |
| `venv\Scripts\activate` | Activate venv (Windows) |
| `source venv/bin/activate` | Activate venv (Mac/Linux) |
| `pip install -r requirements.txt` | Install all Python packages |
| `python -m spacy download en_core_web_sm` | Download spaCy English model |
| `python -m uvicorn main:app --reload` | Start with hot-reload (development) |
| `python -m uvicorn main:app --host 0.0.0.0 --port 8000` | Start (production-like) |

---

### Frontend (`frontend/`)

| Command | Description |
|---------|-------------|
| `npm install` | Install all Node.js dependencies |
| `npm run dev` | Start Vite development server |
| `npm run build` | Build optimized production bundle |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint code checks |

---

## 📋 Environment Variables Reference

### `backend/src/.env`

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | ✅ | `3001` | Backend server port |
| `DATABASE_URL` | ✅ | — | PostgreSQL connection string |
| `JWT_SECRET` | ✅ | — | Secret key for JWT authentication |
| `NODE_ENV` | ✅ | `development` | Environment mode |
| `OPENAI_API_KEY` | ⚠️ | — | Required for JD matching features |
| `AI_SERVICE_URL` | ✅ | `http://localhost:8000` | Python AI service URL |

---

### `ai-service/.env`

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | ✅ | `8000` | AI service port |
| `HOST` | ✅ | `0.0.0.0` | Bind host |
| `DEVICE` | ✅ | `cpu` | `cpu` or `cuda` (if you have a GPU) |
| `MODEL_NAME` | ✅ | `dslim/bert-base-NER` | HuggingFace model name |
| `CONFIDENCE_THRESHOLD` | ✅ | `0.80` | NER confidence threshold |
| `GEMINI_API_KEY` | ⚠️ | — | Google Gemini API key |
| `OPENAI_API_KEY` | ⚠️ | — | OpenAI API key |
| `ANTHROPIC_API_KEY` | ⚠️ | — | Anthropic Claude API key |
| `DEEPSEEK_API_KEY` | ⚠️ | — | DeepSeek API key |

> ⚠️ = Recommended — at least one LLM key is needed for full parsing accuracy.

---

### `frontend/.env`

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | ✅ | `http://localhost:3001/api` | Backend API base URL |
| `VITE_APP_NAME` | ❌ | `ResumeParser AI` | App display name |

> ⚠️ Frontend env variables **must** start with `VITE_` to be accessible in the browser.

---

## ❗ Troubleshooting

### ❌ `Cannot connect to database`
- Make sure PostgreSQL is running locally
- Check the `DATABASE_URL` in `backend/src/.env` is correct
- Ensure the database `resume_parser` exists

### ❌ `Module not found` (Python)
- Make sure your virtual environment is **activated** — you should see `(venv)` in the terminal
- Re-run `pip install -r requirements.txt`

### ❌ `Port already in use`
```bash
# Windows — find which process is using port 3001
netstat -ano | findstr :3001
# Then kill it
taskkill /PID <PID_NUMBER> /F
```

### ❌ `VITE_API_URL not defined`
- Ensure the `.env` file exists in the `frontend/` directory
- All Vite env vars must start with `VITE_`

### ❌ PyTorch / Transformers install fails on Windows
- Upgrade pip first: `pip install --upgrade pip`
- Install Microsoft Visual C++ Build Tools from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

### ❌ `ts-node-dev: command not found`
```bash
npm install -g ts-node-dev
# OR it's in node_modules, run via npx:
npx ts-node-dev --respawn server.ts
```

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 19, TypeScript, Vite, TailwindCSS |
| **State / Data** | Zustand, TanStack Query, React Hook Form |
| **UI Components** | Lucide Icons, Recharts, ECharts |
| **Backend** | Node.js, Express 4, TypeScript |
| **Real-time** | Socket.IO |
| **AI Service** | Python 3.11, FastAPI, Uvicorn |
| **NLP / ML** | HuggingFace Transformers, spaCy, DeBERTa, BERT |
| **LLMs** | Google Gemini, OpenAI GPT-4o, Anthropic Claude, DeepSeek |
| **Database** | PostgreSQL 14 |
| **Auth** | JWT (jsonwebtoken + bcryptjs) |
| **Containerization** | Docker, Docker Compose |

---

## 💡 Startup Order (Important)

Always start services in this order:

```
1. ✅ PostgreSQL       → must be running first
2. ✅ backend/src      → run db:init on first setup, then npm run dev
3. ✅ ai-service       → activate venv, then uvicorn
4. ✅ frontend         → npm run dev
```

The frontend talks to the backend, and the backend talks to the AI service — so start the dependencies first.
