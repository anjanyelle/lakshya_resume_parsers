# 🚀 Deployment Guide - Resume Parser Application

## 📋 **Overview**

This application has **3 components** that need to be deployed:

1. **Frontend (React)** → Deploy to **Vercel**
2. **Backend (Node.js)** → Deploy to **Render**
3. **AI Service (Python FastAPI)** → Deploy to **Render**

---

## 🎯 **Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                         VERCEL                              │
│                    Frontend (React)                         │
│                  https://your-app.vercel.app                │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ API Calls
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                         RENDER                              │
│                  Backend (Node.js/Express)                  │
│              https://backend.onrender.com                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ AI Requests
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                         RENDER                              │
│                AI Service (Python FastAPI)                  │
│              https://ai-service.onrender.com                │
└─────────────────────────────────────────────────────────────┘
```

---

# 📦 **Part 1: Deploy AI Service to Render**

## **Step 1.1: Prepare AI Service**

### Create `render.yaml` in project root:

```yaml
services:
  - type: web
    name: resume-parser-ai-service
    env: python
    region: oregon
    plan: free
    buildCommand: |
      cd ai-service
      pip install -r requirements.txt
    startCommand: |
      cd ai-service
      uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: PORT
        value: 8000
```

### Update `ai-service/requirements.txt`:

Make sure it includes all dependencies:

```txt
fastapi==0.115.6
uvicorn[standard]==0.34.0
python-multipart==0.0.20
pdfplumber==0.11.9
pymupdf==1.27.2.3
python-docx==1.2.0
pytesseract==0.3.13
transformers==4.48.2
torch==2.6.0
scikit-learn==1.6.1
numpy==2.2.3
pandas==2.2.3
python-dateutil==2.9.0
```

## **Step 1.2: Deploy to Render**

1. **Go to**: https://render.com
2. **Sign up/Login** with GitHub
3. **Click**: "New +" → "Web Service"
4. **Connect your GitHub repository**
5. **Configure**:
   - **Name**: `resume-parser-ai-service`
   - **Region**: Oregon (Free)
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Runtime**: Python 3
   - **Build Command**: 
     ```bash
     cd ai-service && pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     cd ai-service && uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: Free

6. **Environment Variables**:
   - Click "Advanced" → "Add Environment Variable"
   - Add: `PYTHON_VERSION` = `3.11.0`

7. **Click**: "Create Web Service"

8. **Wait** for deployment (5-10 minutes)

9. **Copy the URL**: `https://resume-parser-ai-service.onrender.com`

---

# 📦 **Part 2: Deploy Backend to Render**

## **Step 2.1: Prepare Backend**

### Create `backend/render.yaml`:

```yaml
services:
  - type: web
    name: resume-parser-backend
    env: node
    region: oregon
    plan: free
    buildCommand: |
      cd backend/src
      npm install
      npm run build
    startCommand: |
      cd backend/src
      npm start
    envVars:
      - key: NODE_VERSION
        value: 20.11.0
      - key: PORT
        value: 3001
```

### Update `backend/src/package.json`:

Add build and start scripts:

```json
{
  "scripts": {
    "dev": "ts-node-dev --respawn --transpile-only server.ts",
    "build": "tsc",
    "start": "node dist/server.js"
  }
}
```

### Create `backend/src/tsconfig.json` (if not exists):

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "outDir": "./dist",
    "rootDir": "./",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

## **Step 2.2: Set Up Database**

### Option A: Use Render PostgreSQL (Recommended)

1. In Render Dashboard, click "New +" → "PostgreSQL"
2. **Name**: `resume-parser-db`
3. **Database**: `resume_parser`
4. **User**: `postgres`
5. **Region**: Oregon (same as backend)
6. **Plan**: Free
7. Click "Create Database"
8. **Copy** the "Internal Database URL"

### Option B: Use External PostgreSQL (Supabase, Neon, etc.)

Skip this if using Render PostgreSQL.

## **Step 2.3: Deploy Backend to Render**

1. **Go to**: https://render.com
2. **Click**: "New +" → "Web Service"
3. **Connect your GitHub repository**
4. **Configure**:
   - **Name**: `resume-parser-backend`
   - **Region**: Oregon (Free)
   - **Branch**: `main`
   - **Root Directory**: `backend/src`
   - **Runtime**: Node
   - **Build Command**: 
     ```bash
     npm install && npm run build
     ```
   - **Start Command**: 
     ```bash
     npm start
     ```
   - **Plan**: Free

5. **Environment Variables** (Click "Advanced"):

   ```env
   NODE_ENV=production
   PORT=3001
   
   # Database (from Step 2.2)
   DATABASE_URL=postgresql://user:password@host:5432/resume_parser
   DB_HOST=your-db-host.render.com
   DB_PORT=5432
   DB_NAME=resume_parser
   DB_USER=postgres
   DB_PASSWORD=your-password
   
   # AI Service URL (from Part 1)
   AI_SERVICE_URL=https://resume-parser-ai-service.onrender.com
   
   # JWT Secret (generate random string)
   JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
   
   # Redis (optional - for job queue)
   REDIS_URL=redis://localhost:6379
   
   # CORS
   CORS_ORIGIN=https://your-app.vercel.app
   
   # File Upload
   FILE_UPLOAD_PATH=./uploads
   MAX_FILE_SIZE=10485760
   ```

6. **Click**: "Create Web Service"

7. **Wait** for deployment (5-10 minutes)

8. **Copy the URL**: `https://resume-parser-backend.onrender.com`

---

# 📦 **Part 3: Deploy Frontend to Vercel**

## **Step 3.1: Prepare Frontend**

### Update `frontend/.env.production`:

```env
VITE_API_URL=https://resume-parser-backend.onrender.com
VITE_AI_SERVICE_URL=https://resume-parser-ai-service.onrender.com
```

### Create `frontend/vercel.json`:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://resume-parser-backend.onrender.com/api/:path*"
    },
    {
      "source": "/parse-sections",
      "destination": "https://resume-parser-ai-service.onrender.com/parse-sections"
    }
  ]
}
```

## **Step 3.2: Deploy to Vercel**

1. **Go to**: https://vercel.com
2. **Sign up/Login** with GitHub
3. **Click**: "Add New..." → "Project"
4. **Import your GitHub repository**
5. **Configure**:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

6. **Environment Variables**:
   - Click "Environment Variables"
   - Add:
     ```
     VITE_API_URL=https://resume-parser-backend.onrender.com
     VITE_AI_SERVICE_URL=https://resume-parser-ai-service.onrender.com
     ```

7. **Click**: "Deploy"

8. **Wait** for deployment (2-5 minutes)

9. **Your app is live!** 🎉
   - URL: `https://your-app.vercel.app`

---

# 🔧 **Post-Deployment Configuration**

## **Update Backend CORS**

In your backend environment variables on Render, update:

```env
CORS_ORIGIN=https://your-app.vercel.app
```

Then redeploy the backend.

## **Test the Deployment**

1. Visit: `https://your-app.vercel.app`
2. Try uploading a resume
3. Check if parsing works

---

# 🐛 **Troubleshooting**

## **Issue: AI Service Timeout**

**Solution**: Render free tier sleeps after 15 minutes of inactivity. First request takes 30-60 seconds to wake up.

Add this to `ai-service/main.py`:

```python
@app.on_event("startup")
async def startup_event():
    logger.info("AI Service started successfully")
```

## **Issue: Backend Database Connection Failed**

**Solution**: Check DATABASE_URL format:

```
postgresql://user:password@host:port/database
```

## **Issue: Frontend Can't Connect to Backend**

**Solution**: 
1. Check CORS settings in backend
2. Verify VITE_API_URL in Vercel environment variables
3. Check backend logs in Render dashboard

## **Issue: File Upload Fails**

**Solution**: Render free tier has limited disk space. Files are stored temporarily.

Consider using:
- **AWS S3** for file storage
- **Cloudinary** for file uploads

---

# 📊 **Monitoring**

## **Render Dashboard**

- View logs: Render Dashboard → Your Service → Logs
- Check metrics: CPU, Memory usage
- View deployments: Deploy history

## **Vercel Dashboard**

- View deployments: Vercel Dashboard → Your Project
- Check analytics: Usage, Performance
- View logs: Functions → Logs

---

# 💰 **Cost Breakdown**

## **Free Tier Limits**

| Service | Free Tier | Limits |
|---------|-----------|--------|
| **Render (AI Service)** | 750 hours/month | Sleeps after 15 min inactivity |
| **Render (Backend)** | 750 hours/month | Sleeps after 15 min inactivity |
| **Render (PostgreSQL)** | 1 database | 90 days, then deleted |
| **Vercel (Frontend)** | Unlimited | 100 GB bandwidth/month |

## **Upgrade Options**

- **Render Starter**: $7/month per service (no sleep)
- **Render Standard**: $25/month (better performance)
- **Vercel Pro**: $20/month (better analytics)

---

# 🚀 **Quick Deploy Commands**

## **Deploy All at Once**

```bash
# 1. Push to GitHub
git add .
git commit -m "Prepare for deployment"
git push origin main

# 2. Deploy AI Service (Render)
# - Go to render.com
# - Connect repo
# - Set root: ai-service
# - Deploy

# 3. Deploy Backend (Render)
# - Go to render.com
# - Connect repo
# - Set root: backend/src
# - Add environment variables
# - Deploy

# 4. Deploy Frontend (Vercel)
# - Go to vercel.com
# - Connect repo
# - Set root: frontend
# - Add environment variables
# - Deploy
```

---

# ✅ **Deployment Checklist**

- [ ] AI Service deployed to Render
- [ ] AI Service URL copied
- [ ] Backend deployed to Render
- [ ] Database created and connected
- [ ] Backend environment variables set
- [ ] Backend URL copied
- [ ] Frontend environment variables updated
- [ ] Frontend deployed to Vercel
- [ ] CORS configured in backend
- [ ] Test file upload
- [ ] Test resume parsing
- [ ] Monitor logs for errors

---

# 📞 **Support**

If you encounter issues:

1. **Check Render Logs**: Dashboard → Service → Logs
2. **Check Vercel Logs**: Dashboard → Project → Functions
3. **Check Browser Console**: F12 → Console tab
4. **Check Network Tab**: F12 → Network tab

---

**Your application is now deployed and live!** 🎉

- **Frontend**: https://your-app.vercel.app
- **Backend**: https://resume-parser-backend.onrender.com
- **AI Service**: https://resume-parser-ai-service.onrender.com
