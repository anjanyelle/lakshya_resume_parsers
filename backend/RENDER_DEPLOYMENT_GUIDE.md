# FASTAPI BACKEND DEPLOYMENT GUIDE
## Complete Production Deployment on Render.com

This guide provides step-by-step instructions for deploying your FastAPI resume parser backend to Render with ML models, file uploads, and database integration.

---

## 📋 TABLE OF CONTENTS

1. [Project Structure Analysis](#project-structure)
2. [Required Files](#required-files)
3. [Render Configuration](#render-configuration)
4. [Environment Setup](#environment-setup)
5. [ML Model Loading](#ml-model-loading)
6. [Database Configuration](#database-configuration)
7. [File Upload Support](#file-upload-support)
8. [CORS Configuration](#cors-configuration)
9. [Testing & Monitoring](#testing-monitoring)
10. [Troubleshooting](#troubleshooting)

---

## 🏗️ PROJECT STRUCTURE ANALYSIS

Your FastAPI backend follows production best practices:

```
backend/
├── app/
│   ├── api/v1/          # API routes and endpoints
│   ├── core/             # Configuration, database, security
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic request/response schemas
│   ├── services/         # Business logic and parsing engine
│   ├── utils/            # Utilities (validation, audit, etc.)
│   └── workers/          # Background job processing
├── alembic/              # Database migrations
├── observability/         # Monitoring and metrics
├── scripts/              # Utility scripts
├── storage/              # File storage directory
├── pyproject.toml         # Poetry dependencies
├── Dockerfile.render       # Production Docker configuration
├── render.yaml           # Render service definition
└── start.sh              # Production startup script
```

**✅ Production-Ready Features:**
- FastAPI with async support
- SQLAlchemy ORM with Alembic migrations
- Comprehensive error handling
- File upload with validation
- ML model integration framework
- Observability (Sentry, Prometheus)
- Background job processing
- Security middleware

---

## 📁 REQUIRED FILES

### 1. Core Configuration Files

#### `render.yaml` ✅ ALREADY EXISTS
```yaml
services:
  - type: web
    name: resume-parser-api
    env: docker
    plan: starter
    dockerfilePath: ./Dockerfile.render
    dockerContext: .
    healthCheckPath: /health
    autoDeploy: true
    envVars:
      # All environment variables configured
```

#### `Dockerfile.render` ✅ ALREADY EXISTS
```dockerfile
FROM python:3.11-slim
# Production optimizations included
# Health checks, security, ML dependencies
```

#### `pyproject.toml` ✅ ALREADY EXISTS
```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.115.0"
# All dependencies properly configured
```

### 2. Essential Files Status

| File | Status | Purpose |
|------|---------|---------|
| `render.yaml` | ✅ Complete | Render service configuration |
| `Dockerfile.render` | ✅ Complete | Production Docker image |
| `start.sh` | ✅ Complete | Production startup script |
| `.dockerignore` | ✅ Complete | Docker build optimization |
| `requirements.txt` | ✅ Complete | Fallback dependencies |
| `alembic.ini` | ✅ Complete | Database migrations |

---

## ⚙️ RENDER CONFIGURATION

### Step 1: Create Web Service

1. **Navigate to Render Dashboard**
   - Go to https://render.com
   - Click **"New → Web Service"**

2. **Connect Repository**
   - **Repository**: `anjanyelle/Lakshya-LLM-Resume-Parser`
   - **Branch**: `main`
   - **Root Directory**: `backend`

3. **Configure Service**
   ```
   Name: Lakshya-LLM-Resume-Parser
   Environment: Docker
   Region: Singapore (Southeast Asia)
   Dockerfile Path: Dockerfile.render
   Health Check Path: /health
   Instance Type: Free (to start)
   ```

4. **Advanced Settings**
   ```
   Auto-Deploy: Enabled
   Health Check Path: /health
   HTTP Header: X-Request-ID
   ```

### Step 2: Add Database

1. **Create PostgreSQL Database**
   ```
   Name: resume-parser-db
   Database Name: resume_parser
   User: postgres
   Plan: Free (256MB)
   Region: Same as web service
   ```

2. **Connect to Web Service**
   - Go to web service settings
   - Add environment variable:
   ```
   DATABASE_URL: [Auto-populated from database]
   ```

### Step 3: Add Redis (Optional but Recommended)

1. **Create Redis Instance**
   ```
   Name: resume-parser-redis
   Plan: Free (25MB)
   Region: Same as web service
   ```

2. **Connect to Web Service**
   ```
   REDIS_URL: [Auto-populated from Redis]
   ```

---

## 🌍 ENVIRONMENT SETUP

### Core Environment Variables

#### Database Configuration
```bash
DATABASE_URL=postgresql+psycopg2://postgres:password@host:5432/resume_parser
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800
```

#### Application Settings
```bash
APP_NAME="Resume Parser API"
ENVIRONMENT=production
API_V1_STR=/api/v1
LOG_LEVEL=INFO
SECRET_KEY=[Generate secure key]
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

#### File Upload & Storage
```bash
STORAGE_DIR=./storage
UPLOAD_MAX_SIZE_MB=20
ALLOWED_UPLOAD_EXTENSIONS=["pdf","doc","docx","txt","rtf","png","jpg","jpeg"]
```

#### ML & OCR Settings
```bash
OCR_MIN_TEXT_CHARS=100
OCR_MAX_PAGES=15
PDF_MAX_PAGES=50
TESSERACT_CMD=/usr/bin/tesseract
```

#### CORS Configuration
```bash
CORS_ORIGINS=["https://your-frontend-domain.vercel.app"]
```

### Render-Specific Variables
```bash
# Render provides these automatically
PORT=10000
# Web service URL
# Database connection strings
# Redis connection strings
```

---

## 🤖 ML MODEL LOADING

### Current ML Integration

Your application includes ML model loading in the parsing pipeline:

```python
# From your services/parser/ directory
try:
    import spacy
    from spacy.matcher import PhraseMatcher
except Exception:
    spacy = None
    PhraseMatcher = None
```

### Production Model Loading Strategy

#### 1. Model Pre-loading
```python
# In app/main.py or startup event
@app.on_event("startup")
async def startup_event():
    # Load ML models once at startup
    logger.info("Loading ML models...")
    # Add your model loading logic here
    logger.info("ML models loaded successfully")
```

#### 2. Model Caching
```python
# Cache models in memory for performance
MODEL_CACHE = {}

def get_model(model_name: str):
    if model_name not in MODEL_CACHE:
        MODEL_CACHE[model_name] = load_model(model_name)
    return MODEL_CACHE[model_name]
```

#### 3. Model Storage
```python
# Store models in /app/models/ directory
# Mount as volume in Docker for persistence
```

### Render ML Model Deployment

1. **Include Models in Docker**
   ```dockerfile
   # In Dockerfile.render
   COPY ./models/ ./app/models/
   # Download spaCy models
   RUN python -m spacy download en_core_web_sm
   ```

2. **Environment Variables for Models**
   ```bash
   MODEL_PATH=/app/models
   SPACY_MODEL=en_core_web_sm
   ```

---

## 🗄️ DATABASE CONFIGURATION

### PostgreSQL Setup

#### 1. Migration Strategy
```python
# Run migrations on startup
# In start.sh or startup event
alembic upgrade head
```

#### 2. Connection Pooling
```python
# Already configured in config.py
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
```

#### 3. Database Health Check
```python
@app.get("/health")
async def health_check():
    # Check database connection
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
    finally:
        db.close()
```

### Render Database Integration

1. **Automatic Connection**
   - Render automatically provides `DATABASE_URL`
   - Format: `postgresql://username:password@host:port/database`

2. **Migration Execution**
   ```bash
   # Via start.sh
   alembic upgrade head
   ```

3. **Backup Strategy**
   - Render handles automatic backups
   - Configure retention in database settings

---

## 📁 FILE UPLOAD SUPPORT

### Current Implementation Analysis

Your file upload system is production-ready:

```python
# From upload.py
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
```

### File Upload Features

#### 1. Validation
```python
# Magic byte validation
from app.utils.file_validation import validate_magic

# Size limits
UPLOAD_MAX_SIZE_MB=20

# Extension validation
ALLOWED_UPLOAD_EXTENSIONS=["pdf","doc","docx","txt","rtf","png","jpg","jpeg"]
```

#### 2. Storage Options
```python
# Local storage
STORAGE_DIR=./storage

# S3 storage (optional)
S3_ENDPOINT_URL
S3_ACCESS_KEY_ID
S3_SECRET_ACCESS_KEY
S3_BUCKET
```

#### 3. Security Scanning
```python
# Virus scanning
CLAMAV_ENABLED=true
CLAMAV_PATH=/usr/bin/clamscan
```

### Render File Upload Configuration

1. **Persistent Storage**
   ```yaml
   # In render.yaml
   disk:
     name: upload-storage
     sizeGB: 10
     mountPath: /app/storage
   ```

2. **Temporary Storage**
   ```dockerfile
   # Create storage directory
   RUN mkdir -p /app/storage/uploads
   ```

---

## 🌐 CORS CONFIGURATION

### Current CORS Setup

```python
# In app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Production CORS Configuration

#### 1. Environment-Specific Origins
```bash
# Development
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Production (Vercel Frontend)
CORS_ORIGINS=["https://your-app.vercel.app"]

# Multiple domains
CORS_ORIGINS=["https://app.vercel.app","https://www.app.vercel.app"]
```

#### 2. Security Headers
```python
# Additional security headers
@app.middleware("https_redirect")
async def https_redirect(request, call_next):
    if not request.url.scheme.startswith("https"):
        return RedirectResponse(url=request.url.replace("http://", "https://"))
    return await call_next(request)
```

---

## 🧪 TESTING & MONITORING

### Health Endpoints

Your application includes comprehensive health checks:

```python
@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/health/live")
async def live_check():
    return {"status": "ok"}

@app.get("/health/ready")
async def ready_check():
    checks = {"database": "ok", "storage": "ok"}
    return {"status": "ok", "checks": checks}
```

### Monitoring Integration

#### 1. Prometheus Metrics
```python
# Already implemented
from prometheus_client import generate_latest

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

#### 2. Sentry Error Tracking
```python
# Already configured
init_sentry()
instrument_db(engine)
```

#### 3. Structured Logging
```python
# Already implemented
import structlog
logger = structlog.get_logger(__name__)
```

### Render Monitoring Setup

1. **Service Health**
   - Render automatically monitors `/health` endpoint
   - Configure health check interval (30 seconds)

2. **Log Aggregation**
   - Render collects application logs
   - View in dashboard

3. **Metrics Dashboard**
   - Prometheus metrics available at `/metrics`
   - Custom dashboards can be created

---

## 🚀 DEPLOYMENT STEPS

### Pre-Deployment Checklist

#### 1. Code Preparation
- [ ] Push latest code to `main` branch
- [ ] Verify `render.yaml` is in backend root
- [ ] Confirm `Dockerfile.render` exists
- [ ] Test local build: `docker build -f Dockerfile.render .`

#### 2. Environment Setup
- [ ] Prepare environment variables
- [ ] Generate secure `SECRET_KEY`
- [ ] Configure CORS origins
- [ ] Set database connection parameters

#### 3. Database Preparation
- [ ] Create PostgreSQL service on Render
- [ ] Note connection string
- [ ] Plan migration strategy

### Step-by-Step Deployment

#### Step 1: Create Web Service
1. Go to Render Dashboard → **New → Web Service**
2. Connect GitHub repository
3. Configure:
   ```
   Name: Lakshya-LLM-Resume-Parser
   Root Directory: backend
   Dockerfile Path: Dockerfile.render
   Health Check Path: /health
   Auto-Deploy: Enabled
   ```

#### Step 2: Add Database
1. Go to **New → PostgreSQL**
2. Configure:
   ```
   Name: resume-parser-db
   Database Name: resume_parser
   Plan: Free
   ```
3. Connect to web service

#### Step 3: Configure Environment
1. Go to web service → **Environment**
2. Add required variables:
   ```bash
   SECRET_KEY=[generate-secure-key]
   CORS_ORIGINS=["https://your-frontend.vercel.app"]
   # Others auto-populated
   ```

#### Step 4: Deploy
1. Push changes to trigger deployment
2. Monitor build logs
3. Verify health endpoint
4. Test API functionality

---

## 🔧 TROUBLESHOOTING

### Common Deployment Issues

#### 1. Build Failures
**Problem**: Docker build fails
```
Solution:
1. Check Dockerfile.render syntax
2. Verify all dependencies in pyproject.toml
3. Test local build: docker build -f Dockerfile.render .
```

#### 2. Database Connection Issues
**Problem**: Can't connect to PostgreSQL
```
Solution:
1. Verify DATABASE_URL format
2. Check database service status
3. Ensure proper SSL settings
4. Test connection manually
```

#### 3. Health Check Failures
**Problem**: Health check returns 503
```
Solution:
1. Verify /health endpoint exists
2. Check application logs
3. Ensure port binding (0.0.0.0:8000)
4. Review startup script errors
```

#### 4. ML Model Loading Issues
**Problem**: Models fail to load
```
Solution:
1. Verify model files in Docker image
2. Check environment variables
3. Add model loading to startup logs
4. Implement graceful fallback
```

#### 5. File Upload Issues
**Problem**: Uploads fail or files not saved
```
Solution:
1. Check storage directory permissions
2. Verify file size limits
3. Test file validation logic
4. Check disk space availability
```

#### 6. CORS Errors
**Problem**: Frontend can't access API
```
Solution:
1. Update CORS_ORIGINS environment variable
2. Verify exact domain match
3. Check for trailing slashes
4. Ensure HTTPS protocol
```

### Debugging Commands

#### 1. Local Testing
```bash
# Test Docker build
docker build -f Dockerfile.render -t resume-parser .

# Test container locally
docker run -p 8000:8000 resume-parser

# Test health endpoint
curl http://localhost:8000/health
```

#### 2. Render Logs
```bash
# View real-time logs
# Via Render dashboard → Logs tab

# Common log locations
/app/logs/
/var/log/render/
```

#### 3. Database Debugging
```bash
# Connect to Render database
psql $DATABASE_URL

# Check migrations
alembic current
alembic history
```

---

## 📊 PERFORMANCE OPTIMIZATION

### FastAPI Production Settings

#### 1. Gunicorn Configuration
```dockerfile
# In Dockerfile.render
CMD ["gunicorn", "app.main:app", 
       "-w", "2",                    # Workers
       "-k", "uvicorn.workers.UvicornWorker",
       "-b", "0.0.0.0:8000",
       "--timeout", "120",            # Request timeout
       "--max-requests", "1000",      # Worker restart limit
       "--max-requests-jitter", "50"] # Jitter for restarts
```

#### 2. Memory Management
```python
# Connection pooling
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Request limits
UPLOAD_MAX_SIZE_MB=20
PDF_MAX_PAGES=50
```

#### 3. Caching Strategy
```python
# Redis caching (if configured)
from app.core.cache import cache

@cache.memoize(ttl=300)
def expensive_ml_operation(data):
    # Cache for 5 minutes
    pass
```

---

## 🔒 SECURITY CHECKLIST

### Production Security Measures

#### 1. Authentication & Authorization
- [ ] JWT tokens implemented
- [ ] Rate limiting configured
- [ ] User authentication enforced
- [ ] API key authentication for services

#### 2. Input Validation
- [ ] File type validation (magic bytes)
- [ ] File size limits enforced
- [ ] SQL injection protection (ORM)
- [ ] XSS prevention

#### 3. Infrastructure Security
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] Virus scanning enabled

#### 4. Data Protection
- [ ] Environment variables secured
- [ ] Database encryption enabled
- [ ] Audit logging implemented
- [ ] GDPR compliance features

---

## 📈 MONITORING & ALERTS

### Key Metrics to Monitor

#### 1. Application Metrics
- Request rate and response times
- Error rates by endpoint
- File upload success/failure rates
- ML model inference times

#### 2. Infrastructure Metrics
- CPU and memory usage
- Database connection pool status
- Disk space usage
- Network latency

#### 3. Business Metrics
- Resume parsing success rate
- Average parsing time
- User registration/activity
- File storage usage

### Alert Configuration

#### 1. Render Alerts
- Service health failures
- Build/deployment failures
- High error rates
- Resource exhaustion

#### 2. Custom Alerts
```python
# Custom health checks
@app.get("/health/detailed")
async def detailed_health():
    return {
        "status": "healthy",
        "checks": {
            "database": await check_database(),
            "storage": await check_storage(),
            "ml_models": await check_ml_models(),
            "redis": await check_redis()
        }
    }
```

---

## 🔄 CONTINUOUS DEPLOYMENT

### CI/CD Pipeline

#### 1. Automated Testing
```yaml
# .github/workflows/deploy.yml
name: Deploy to Render
on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          docker build -f Dockerfile.render .
          pytest tests/
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Render
        run: |
          curl -X POST \
            -H "Authorization: Bearer $RENDER_API_KEY" \
            -H "Content-Type: application/json" \
            -d '{"serviceId": "your-service-id"}' \
            https://api.render.com/v1/services/your-service-id/deploys
```

#### 2. Blue-Green Deployment
```yaml
# Render supports zero-downtime deployments
# Configure in render.yaml
preDeployHook: ./scripts/pre-deploy.sh
postDeployHook: ./scripts/post-deploy.sh
```

---

## 📚 REFERENCE DOCUMENTATION

### Quick Links
- [Render Documentation](https://render.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [Docker Best Practices](https://docs.docker.com)

### Environment Variable Reference
| Variable | Required | Default | Description |
|----------|-----------|---------|-------------|
| `DATABASE_URL` | ✅ | - | PostgreSQL connection string |
| `SECRET_KEY` | ✅ | `change_me` | JWT signing key |
| `CORS_ORIGINS` | ✅ | `[]` | Allowed frontend origins |
| `STORAGE_DIR` | ❌ | `./storage` | File upload directory |
| `UPLOAD_MAX_SIZE_MB` | ❌ | `20` | Max file size in MB |
| `LOG_LEVEL` | ❌ | `INFO` | Logging verbosity |

---

## 🎯 SUCCESS CRITERIA

Your deployment is successful when:

- [ ] Web service responds to `/health` endpoint
- [ ] Database migrations completed successfully
- [ ] File uploads work correctly
- [ ] ML models load without errors
- [ ] API endpoints return expected responses
- [ ] CORS properly configured for frontend
- [ ] Monitoring and logging functional
- [ ] Performance meets requirements (<3s parse time)

---

## 🆘 SUPPORT

### Render Support
- Documentation: https://render.com/docs
- Status Page: https://status.render.com
- Support: support@render.com

### Common Issues
- **Build Failures**: Check Dockerfile and dependencies
- **Database Issues**: Verify connection string and migrations
- **Performance**: Optimize database queries and caching
- **Security**: Review environment variables and CORS settings

---

**This guide covers all aspects of deploying your FastAPI resume parser backend to Render with ML models, file uploads, database integration, and production-ready configuration.**
