









The .gitignore file is preventing access to package.json files in both frontend and backend directories. This is unusual as .gitignore typically only affects git operations, but the system appears to be enforcing these rules for file access.

I can proceed using the information I already have from the previous session (I analyzed the backend package.json earlier), or I can read the .gitignore file to understand what's blocking access and potentially work around it.

How would you like me to proceed?







# Comprehensive Production Deployment Architecture

---

## SECTION 1: Current Project Analysis

### **Frontend Analysis**
- **Framework:** React + Vite
- **Build Tool:** Vite
- **Output:** Static files in [dist/](cci:9://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/frontend/dist:0:0-0:0)
- **Docker:** Multi-stage build with nginx
- **Environment:** Uses [.env.production](cci:7://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/frontend/.env.production:0:0-0:0) with `VITE_API_URL`
- **Proxy:** Configured for `/parse-sections` to AI service
- **Status:** Production-ready for static deployment

### **Backend Analysis**
- **Framework:** Node.js + Express + TypeScript
- **Entry Point:** [server.ts](cci:7://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/backend/src/server.ts:0:0-0:0) → [app.ts](cci:7://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/backend/src/app.ts:0:0-0:0)
- **Database:** PostgreSQL (currently on Render)
- **Queue System:** BullMQ with Redis
- **File Storage:** AWS S3 / DigitalOcean Spaces (configurable)
- **AI Integration:** OpenAI GPT-4o-mini
- **Real-time:** Socket.io
- **Authentication:** JWT with bcrypt
- **Status:** Production-ready, needs infrastructure

### **AI Service Analysis**
- **Framework:** Python FastAPI
- **Model:** Microsoft DeBERTa-v3-base (fine-tuned)
- **Model Size:** ~400-500MB (model.safetensors)
- **Model Location:** [ai-service/models/resume-ner-deberta/](cci:9://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/ai-service/models/resume-ner-deberta:0:0-0:0)
- **RAM Requirements:** 2-4GB minimum for model loading
- **CPU Requirements:** 2+ cores for acceptable inference
- **Startup Time:** 30-60 seconds (model loading)
- **Additional AI Providers:** OpenAI, Anthropic, Gemini
- **Status:** Heavy resource requirements, needs dedicated infrastructure

### **Existing Deployment Guide Review**
- **Current Approach:** Vercel (frontend) + Render (backend) + Render (AI service)
- **Issues Identified:**
  - Render free tier sleeps after 15 min inactivity
  - Render free tier has 512MB RAM (insufficient for AI model)
  - Render PostgreSQL free tier deletes after 90 days
  - AI service cold starts are unacceptable for production
  - No persistent Redis for queues

---

## SECTION 2: Recommended Architecture

### **Recommended Infrastructure**

```
┌─────────────────────────────────────────────────────────────────┐
│                         Vercel                                  │
│                    Frontend (React)                             │
│                  lakshya-resume-parser.vercel.app                │
│                    (Static Site Deployment)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS API Calls
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DigitalOcean VPS #1                           │
│                  (8GB RAM, 4 vCPU, $48/mo)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Backend (Node.js + Express)                            │  │
│  │  - PM2 Process Manager                                  │  │
│  │  - Port 3001                                            │  │
│  │  - Nginx Reverse Proxy                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Redis (Docker Container)                               │  │
│  │  - BullMQ Job Queues                                    │  │
│  │  - Caching Layer                                        │  │
│  │  - Port 6379                                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ AI Service Calls
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DigitalOcean VPS #2                           │
│                  (8GB RAM, 4 vCPU, $48/mo)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  AI Service (Python FastAPI)                            │  │
│  │  - DeBERTa-v3 Model (loaded in memory)                  │  │
│  │  - PM2 Process Manager                                  │  │
│  │  - Port 8000                                            │  │
│  │  - Nginx Reverse Proxy                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Database Connection
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              DigitalOcean Managed PostgreSQL                     │
│                  (4GB RAM, 2 vCPU, $15/mo)                       │
│              - Persistent Storage                               │
│              - Automated Backups                                 │
│              - High Availability                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ File Storage
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              DigitalOcean Spaces (S3-compatible)                 │
│                  - Resume Files                                  │
│                  - CDN Enabled                                   │
│                  - $5-10/mo depending on usage                    │
└─────────────────────────────────────────────────────────────────┘
```

### **Architecture Decisions**

**Frontend: Vercel**
- **Why:** Best-in-class for React/Vite static sites
- **Benefits:** 
  - Free tier with unlimited bandwidth
  - Automatic deployments from GitHub
  - Global CDN
  - Zero cold starts
  - Built-in HTTPS
- **Cost:** $0 (free tier)

**Backend: DigitalOcean VPS**
- **Why not Render:**
  - Render free tier sleeps (unacceptable for production)
  - Render paid tier ($25/mo) is more expensive than DO
  - Limited control over infrastructure
  - Cannot run Redis on same instance
- **Why DigitalOcean:**
  - User has paid VPS available
  - No sleep issues
  - Can run backend + Redis on same instance
  - Better performance
  - Full control over environment
  - PM2 for process management
- **Cost:** $48/mo (8GB RAM, 4 vCPU)

**AI Service: DigitalOcean VPS**
- **Why not Render:**
  - DeBERTa model requires 2-4GB RAM minimum
  - Render free tier has 512MB RAM (insufficient)
  - Render paid tier ($25/mo) has 2GB RAM (barely sufficient)
  - Cold starts are unacceptable (30-60s model loading)
  - Sleep issues cause repeated cold starts
- **Why DigitalOcean:**
  - Dedicated 8GB RAM for model
  - Model stays loaded in memory
  - No cold starts
  - Can use PM2 for process management
  - Better inference performance
- **Cost:** $48/mo (8GB RAM, 4 vCPU)

**Database: DigitalOcean Managed PostgreSQL**
- **Why not Render:**
  - Render free tier deletes after 90 days
  - Limited features and performance
- **Why DigitalOcean:**
  - Managed service with automated backups
  - Better performance
  - No 90-day limit
  - Better security
  - Integrated with DigitalOcean ecosystem
- **Cost:** $15/mo (4GB RAM, 2 vCPU)

**File Storage: DigitalOcean Spaces**
- **Why not Local:**
  - Limited disk space
  - No redundancy
  - No CDN
- **Why DigitalOcean:**
  - S3-compatible API
  - Same provider as VPS (lower latency)
  - CDN enabled
  - Cost-effective
  - Integrated with existing infrastructure
- **Cost:** $5-10/mo (depending on usage)

---

## SECTION 3: Infrastructure Setup

### **DigitalOcean Account Setup**

1. **Create DigitalOcean Account** (if not already)
2. **Generate API Token:**
   - Go to Settings → API → Generate New Token
   - Save token securely
3. **Create SSH Key:**
   ```bash
   ssh-keygen -t ed25519 -C "your-email@example.com"
   cat ~/.ssh/id_ed25519.pub
   ```
   - Add to DigitalOcean account

### **VPS #1 Setup (Backend + Redis)**

1. **Create Droplet:**
   - Image: Ubuntu 22.04 LTS
   - Size: 8GB RAM, 4 vCPU ($48/mo)
   - Region: Singapore (closest to users)
   - SSH Key: Add your SSH key
   - Hostname: `lakshya-backend`

2. **Initial Server Setup:**
   ```bash
   # SSH into server
   ssh root@your-server-ip
   
   # Update system
   apt update && apt upgrade -y
   
   # Install essential packages
   apt install -y curl git nginx ufw fail2ban
   
   # Install Node.js 20
   curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
   apt install -y nodejs
   
   # Install PM2
   npm install -g pm2
   
   # Install Docker (for Redis)
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   
   # Configure firewall
   ufw allow 22/tcp
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw enable
   ```

### **VPS #2 Setup (AI Service)**

1. **Create Droplet:**
   - Image: Ubuntu 22.04 LTS
   - Size: 8GB RAM, 4 vCPU ($48/mo)
   - Region: Singapore
   - SSH Key: Add your SSH key
   - Hostname: `lakshya-ai-service`

2. **Initial Server Setup:**
   ```bash
   # SSH into server
   ssh root@your-server-ip
   
   # Update system
   apt update && apt upgrade -y
   
   # Install essential packages
   apt install -y curl git nginx ufw fail2ban python3-pip
   
   # Install Python 3.11
   apt install -y python3.11 python3.11-venv
   
   # Install PM2
   npm install -g pm2
   
   # Configure firewall
   ufw allow 22/tcp
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw enable
   ```

### **DigitalOcean Managed PostgreSQL Setup**

1. **Create Database Cluster:**
   - Go to Databases → Create Database Cluster
   - Engine: PostgreSQL
   - Version: 16
   - Size: 4GB RAM, 2 vCPU ($15/mo)
   - Region: Singapore
   - Database Name: `resume_parser`
   - User: `postgres`

2. **Configure Connection:**
   - Add Trusted Sources (VPS #1 and VPS #2 IPs)
   - Enable SSL
   - Copy connection string

### **DigitalOcean Spaces Setup**

1. **Create Space:**
   - Go to Spaces → Create Space
   - Region: Singapore
   - Name: `lakshya-resume-files`
   - CDN: Enable

2. **Create API Keys:**
   - Go to Settings → API Keys
   - Generate Spaces Access Key
   - Save credentials

---

## SECTION 4: Frontend Deployment

### **Vercel Deployment Steps**

1. **Prepare Frontend Repository:**
   ```bash
   cd frontend
   
   # Update .env.production
   cat > .env.production << EOF
   VITE_API_URL=https://backend.yourdomain.com
   VITE_AI_SERVICE_URL=https://ai-service.yourdomain.com
   EOF
   ```

2. **Create vercel.json:**
   ```json
   {
     "buildCommand": "npm run build",
     "outputDirectory": "dist",
     "framework": "vite"
   }
   ```

3. **Deploy to Vercel:**
   - Go to https://vercel.com
   - Click "Add New Project"
   - Import GitHub repository
   - Configure:
     - Framework Preset: Vite
     - Root Directory: [frontend](cci:9://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/frontend:0:0-0:0)
     - Build Command: `npm run build`
     - Output Directory: [dist](cci:9://file:///Users/anjanyelle/Desktop/untitled%20folder%203/Lakshya-LLM-Resume-Parser/frontend/dist:0:0-0:0)
   - Add Environment Variables:
     - `VITE_API_URL`: `https://backend.yourdomain.com`
     - `VITE_AI_SERVICE_URL`: `https://ai-service.yourdomain.com`
   - Click Deploy

4. **Configure Custom Domain:**
   - Go to Project Settings → Domains
   - Add custom domain: `lakshya.yourdomain.com`
   - Configure DNS records

---

## SECTION 5: Backend Deployment

### **VPS #1 Backend Setup**

1. **Clone Repository:**
   ```bash
   ssh root@backend-server-ip
   cd /var/www
   git clone https://github.com/your-username/Lakshya-LLM-Resume-Parser.git
   cd Lakshya-LLM-Resume-Parser/backend/src
   ```

2. **Install Dependencies:**
   ```bash
   npm install
   npm run build
   ```

3. **Create Production .env:**
   ```bash
   cat > .env << EOF
   PORT=3001
   NODE_ENV=production
   
   # Database (DigitalOcean Managed PostgreSQL)
   DATABASE_URL=postgresql://postgres:password@db-host.do-user-123456-0.db.ondigitalocean.com:25060/resume_parser?sslmode=require
   DB_HOST=db-host.do-user-123456-0.db.ondigitalocean.com
   DB_PORT=25060
   DB_NAME=resume_parser
   DB_USER=postgres
   DB_PASSWORD=your-password
   
   # Redis (local Docker)
   REDIS_URL=redis://localhost:6379
   
   # JWT Secret
   JWT_SECRET=your-super-secret-jwt-key-min-32-chars
   
   # AI Service URL
   AI_SERVICE_URL=https://ai-service.yourdomain.com
   
   # CORS Origins
   CORS_ORIGINS=["https://lakshya.yourdomain.com"]
   
   # OpenAI API
   OPENAI_API_KEY=your-openai-api-key
   
   # DigitalOcean Spaces
   AWS_ACCESS_KEY_ID=your-spaces-access-key
   AWS_SECRET_ACCESS_KEY=your-spaces-secret-key
   AWS_BUCKET_NAME=lakshya-resume-files
   AWS_REGION=sgp1
   AWS_ENDPOINT=https://sgp1.digitaloceanspaces.com
   
   # File Upload
   FILE_UPLOAD_PATH=./uploads
   MAX_FILE_SIZE_MB=10
   EOF
   ```

4. **Start Redis with Docker:**
   ```bash
   docker run -d \
     --name redis \
     -p 6379:6379 \
     -v redis-data:/data \
     redis:7-alpine \
     redis-server --appendonly yes
   ```

5. **Start Backend with PM2:**
   ```bash
   pm2 start dist/server.js --name "backend"
   pm2 save
   pm2 startup
   ```

6. **Configure Nginx:**
   ```bash
   cat > /etc/nginx/sites-available/backend << EOF
   server {
       listen 80;
       server_name backend.yourdomain.com;
       
       location / {
           proxy_pass http://localhost:3001;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   EOF
   
   ln -s /etc/nginx/sites-available/backend /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

7. **Configure SSL with Certbot:**
   ```bash
   apt install -y certbot python3-certbot-nginx
   certbot --nginx -d backend.yourdomain.com
   ```

---

## SECTION 6: AI Service Deployment

### **VPS #2 AI Service Setup**

1. **Clone Repository:**
   ```bash
   ssh root@ai-server-ip
   cd /var/www
   git clone https://github.com/your-username/Lakshya-LLM-Resume-Parser.git
   cd Lakshya-LLM-Resume-Parser/ai-service
   ```

2. **Create Python Virtual Environment:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Create Production .env:**
   ```bash
   cat > .env << EOF
   PORT=8000
   ENVIRONMENT=production
   
   # AI Provider Keys
   OPENAI_API_KEY=your-openai-api-key
   ANTHROPIC_API_KEY=your-anthropic-api-key
   GEMINI_API_KEY=your-gemini-api-key
   
   # CORS Origins
   CORS_ORIGINS=["https://backend.yourdomain.com","https://lakshya.yourdomain.com"]
   
   # Model Configuration
   MODEL_PATH=/var/www/Lakshya-LLM-Resume-Parser/ai-service/models/resume-ner-deberta
   DEVICE=cuda  # or cpu if no GPU
   EOF
   ```

4. **Verify Model Files:**
   ```bash
   ls -lh models/resume-ner-deberta/
   # Should see: model.safetensors, config.json, tokenizer files
   ```

5. **Start AI Service with PM2:**
   ```bash
   pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name "ai-service"
   pm2 save
   pm2 startup
   ```

6. **Configure Nginx:**
   ```bash
   cat > /etc/nginx/sites-available/ai-service << EOF
   server {
       listen 80;
       server_name ai-service.yourdomain.com;
       
       client_max_body_size 10M;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           
           # Increase timeout for AI processing
           proxy_read_timeout 300s;
           proxy_connect_timeout 300s;
       }
   }
   EOF
   
   ln -s /etc/nginx/sites-available/ai-service /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

7. **Configure SSL with Certbot:**
   ```bash
   apt install -y certbot python3-certbot-nginx
   certbot --nginx -d ai-service.yourdomain.com
   ```

---

## SECTION 7: Database Deployment

### **DigitalOcean Managed PostgreSQL Setup**

1. **Database Connection String:**
   ```
   postgresql://postgres:password@db-host.do-user-123456-0.db.ondigitalocean.com:25060/resume_parser?sslmode=require
   ```

2. **Run Database Migrations:**
   ```bash
   # On VPS #1
   cd /var/www/Lakshya-LLM-Resume-Parser/backend/src
   npm run db:init
   ```

3. **Configure Automated Backups:**
   - Go to DigitalOcean Dashboard → Databases
   - Select your cluster
   - Enable automated backups (daily, 7-day retention)

4. **Configure Connection Pooling:**
   - Enable PgBouncer in DigitalOcean dashboard
   - Configure pool size: 20-50 connections

---

## SECTION 8: Storage Deployment

### **DigitalOcean Spaces Setup**

1. **Create Bucket Policy:**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "AWS": "*"
         },
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::lakshya-resume-files/*"
       }
     ]
   }
   ```

2. **Configure CORS:**
   ```json
   {
     "CORSRules": [
       {
         "AllowedOrigins": ["https://lakshya.yourdomain.com"],
         "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
         "AllowedHeaders": ["*"],
         "MaxAgeSeconds": 3000
       }
     ]
   }
   ```

3. **Test Upload:**
   ```bash
   # On VPS #1
   aws s3api put-object \
     --bucket lakshya-resume-files \
     --key test.txt \
     --body "test" \
     --endpoint-url https://sgp1.digitaloceanspaces.com
   ```

---

## SECTION 9: Docker Configuration

### **Backend Dockerfile**

```dockerfile
# backend/Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --production

COPY --from=builder /app/dist ./dist

EXPOSE 3001

CMD ["node", "dist/server.js"]
```

### **AI Service Dockerfile**

```dockerfile
# ai-service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    libleptonica-dev \
    libpng-dev \
    libjpeg-dev \
    libtiff-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Copy models (if not using volume)
COPY models/ ./models/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Docker Compose**

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend/src
      dockerfile: Dockerfile
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=${JWT_SECRET}
      - AI_SERVICE_URL=http://ai-service:8000
    depends_on:
      - redis
    restart: unless-stopped

  ai-service:
    build:
      context: ./ai-service
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MODEL_PATH=/app/models/resume-ner-deberta
    volumes:
      - ./ai-service/models:/app/models
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

volumes:
  redis-data:
```

---

## SECTION 10: CI/CD Configuration

### **GitHub Actions Workflow**

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
          working-directory: ./frontend

  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to DigitalOcean
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.BACKEND_HOST }}
          username: root
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /var/www/Lakshya-LLM-Resume-Parser
            git pull origin main
            cd backend/src
            npm install
            npm run build
            pm2 restart backend

  deploy-ai-service:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy AI Service
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.AI_SERVICE_HOST }}
          username: root
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /var/www/Lakshya-LLM-Resume-Parser
            git pull origin main
            cd ai-service
            source venv/bin/activate
            pip install -r requirements.txt
            pm2 restart ai-service
```

### **GitHub Secrets Required**

- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`
- `BACKEND_HOST` (VPS #1 IP)
- `AI_SERVICE_HOST` (VPS #2 IP)
- `SSH_PRIVATE_KEY`

---

## SECTION 11: Cost Estimation

### **Monthly Cost Breakdown**

| Service | Specification | Monthly Cost |
|---------|---------------|-------------|
| **Vercel (Frontend)** | Static site, unlimited bandwidth | $0 |
| **DigitalOcean VPS #1** | 8GB RAM, 4 vCPU (Backend + Redis) | $48 |
| **DigitalOcean VPS #2** | 8GB RAM, 4 vCPU (AI Service) | $48 |
| **DigitalOcean PostgreSQL** | 4GB RAM, 2 vCPU, Managed | $15 |
| **DigitalOcean Spaces** | S3-compatible, CDN enabled | $5-10 |
| **Domain** | Custom domain (optional) | $12/year |
| **SSL Certificates** | Let's Encrypt (free) | $0 |
| **Total** | | **$116-121/month** |

### **Alternative Cost-Optimized Setup**

If budget is a concern, you can consolidate:

| Service | Specification | Monthly Cost |
|---------|---------------|-------------|
| **Vercel (Frontend)** | Static site | $0 |
| **DigitalOcean VPS** | 16GB RAM, 8 vCPU (Backend + AI + Redis) | $96 |
| **DigitalOcean PostgreSQL** | 4GB RAM, 2 vCPU | $15 |
| **DigitalOcean Spaces** | S3-compatible | $5-10 |
| **Total** | | **$116-121/month** |

### **Recommended Droplet Sizes**

**For Production:**
- **Backend VPS:** 8GB RAM, 4 vCPU ($48/mo)
- **AI Service VPS:** 8GB RAM, 4 vCPU ($48/mo)

**For Development/Staging:**
- **Combined VPS:** 16GB RAM, 8 vCPU ($96/mo)

---

## SECTION 12: Security Checklist

### **Network Security**
- [ ] Configure UFW firewall on both VPS
- [ ] Only allow ports 22, 80, 443
- [ ] Disable password authentication for SSH
- [ ] Use SSH keys only
- [ ] Configure fail2ban for SSH protection
- [ ] Enable DDoS protection (DigitalOcean)

### **Application Security**
- [ ] Enable HTTPS with Let's Encrypt
- [ ] Configure CORS properly
- [ ] Use strong JWT secrets (32+ characters)
- [ ] Rotate secrets regularly
- [ ] Enable rate limiting on backend
- [ ] Validate all input data
- [ ] Use parameterized queries
- [ ] Never commit secrets to git

### **Database Security**
- [ ] Enable SSL for database connections
- [ ] Use strong database passwords
- [ ] Restrict database access to VPS IPs only
- [ ] Enable automated backups
- [ ] Regular backup testing
- [ ] Enable query logging

### **File Storage Security**
- [ ] Configure bucket policies
- [ ] Enable CORS for frontend domain only
- [ ] Use signed URLs for private files
- [ ] Enable versioning
- [ ] Configure lifecycle policies

### **Monitoring & Logging**
- [ ] Configure PM2 logging
- [ ] Set up log rotation
- [ ] Monitor disk space
- [ ] Monitor CPU/memory usage
- [ ] Set up alerting (DigitalOcean monitoring)
- [ ] Configure error tracking (Sentry)

### **AI Service Security**
- [ ] Restrict AI service access to backend only
- [ ] Rate limit AI endpoints
- [ ] Monitor API usage
- [ ] Set spending limits on AI providers
- [ ] Validate AI responses

---

## SECTION 13: Step-by-Step Deployment Guide

### **Phase 1: Infrastructure Setup (Day 1)**

1. **Create DigitalOcean Account** (if needed)
2. **Generate API Token** and SSH keys
3. **Create VPS #1** (Backend + Redis)
4. **Create VPS #2** (AI Service)
5. **Create Managed PostgreSQL cluster**
6. **Create DigitalOcean Space**
7. **Configure DNS records** for custom domains

### **Phase 2: Backend Deployment (Day 1-2)**

1. **SSH into VPS #1**
2. **Install Node.js, PM2, Docker, Nginx**
3. **Clone repository**
4. **Install dependencies and build**
5. **Configure .env file**
6. **Start Redis with Docker**
7. **Start backend with PM2**
8. **Configure Nginx reverse proxy**
9. **Enable SSL with Certbot**
10. **Test backend endpoints**

### **Phase 3: AI Service Deployment (Day 2)**

1. **SSH into VPS #2**
2. **Install Python 3.11, PM2, Nginx**
3. **Clone repository**
4. **Create virtual environment**
5. **Install Python dependencies**
6. **Configure .env file**
7. **Verify model files**
8. **Start AI service with PM2**
9. **Configure Nginx reverse proxy**
10. **Enable SSL with Certbot**
11. **Test AI service endpoints**

### **Phase 4: Database Setup (Day 2)**

1. **Configure PostgreSQL connection**
2. **Run database migrations**
3. **Test database connection**
4. **Configure automated backups**
5. **Enable connection pooling**

### **Phase 5: Frontend Deployment (Day 3)**

1. **Update frontend .env.production**
2. **Push to GitHub**
3. **Deploy to Vercel**
4. **Configure custom domain**
5. **Test frontend deployment**

### **Phase 6: CI/CD Setup (Day 3)**

1. **Configure GitHub Actions workflow**
2. **Add GitHub secrets**
3. **Test CI/CD pipeline**
4. **Configure automatic deployments**

### **Phase 7: Monitoring & Testing (Day 4)**

1. **Configure PM2 monitoring**
2. **Set up log rotation**
3. **Configure DigitalOcean monitoring**
4. **Test complete user flow**
5. **Load testing**
6. **Security audit**

### **Phase 8: Go Live (Day 5)**

1. **Final security review**
2. **Backup verification**
3. **DNS final configuration**
4. **Production deployment**
5. **Monitor initial traffic**
6. **Prepare rollback plan**

---

## Final Recommendation

**Production Architecture:**
- **Frontend:** Vercel (free, excellent for React)
- **Backend:** DigitalOcean VPS (8GB RAM, 4 vCPU, $48/mo)
- **AI Service:** DigitalOcean VPS (8GB RAM, 4 vCPU, $48/mo)
- **Database:** DigitalOcean Managed PostgreSQL (4GB RAM, $15/mo)
- **Storage:** DigitalOcean Spaces ($5-10/mo)
- **Total Monthly Cost:** $116-121

**Key Benefits:**
- No sleep issues (unlike Render)
- Sufficient RAM for AI model
- Model stays loaded in memory
- Better performance
- Full control over infrastructure
- Cost-effective for production workload

**Next Steps:**
1. Create DigitalOcean infrastructure
2. Deploy backend to VPS #1
3. Deploy AI service to VPS #2
4. Deploy frontend to Vercel
5. Configure CI/CD pipeline
6. Monitor and optimize

This architecture provides a stable, scalable, and cost-effective production setup for your Lakshya LLM Resume Parser application.