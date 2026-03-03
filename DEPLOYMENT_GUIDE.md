# DEPLOYMENT GUIDE
## Resume Parser Application - Render + Vercel

This guide will help you deploy the resume parser application to Render (backend) and Vercel (frontend).

---

## PREREQUISITES

1. **Render Account** - Sign up at https://render.com
2. **Vercel Account** - Sign up at https://vercel.com
3. **GitHub Repository** - Push your code to GitHub
4. **Domain Names** (Optional) - Custom domains for frontend/backend

---

## BACKEND DEPLOYMENT (RENDER)

### Step 1: Prepare Repository
1. Ensure your code is pushed to GitHub
2. The `render.yaml` file should be in the root of the backend directory
3. The `Dockerfile.render` file should be in the backend directory

### Step 2: Create Render Service
1. Go to Render Dashboard → New → Web Service
2. Connect your GitHub repository
3. Select the `backend` directory
4. Configure the service:
   - **Name**: `resume-parser-api`
   - **Environment**: Docker
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Dockerfile Path**: `Dockerfile.render`
   - **Health Check Path**: `/health`

### Step 3: Configure Environment Variables
Render will automatically read from `render.yaml`, but you may need to update:
- `CORS_ORIGINS` - Add your Vercel frontend URL
- `DATABASE_URL` - Will be auto-populated by Render PostgreSQL
- `REDIS_URL` - Will be auto-populated if using Render Redis

### Step 4: Add Database
1. Go to Render Dashboard → New → PostgreSQL
2. **Name**: `resume-parser-db`
3. **Database Name**: `resume_parser`
4. **User**: `postgres`
5. Connect to your web service

### Step 5: Add Redis (Optional)
1. Go to Render Dashboard → New → Redis
2. **Name**: `resume-parser-redis`
3. Connect to your web service

### Step 6: Deploy
1. Push changes to GitHub
2. Render will auto-deploy
3. Monitor deployment logs
4. Test health endpoint: `https://your-app.onrender.com/health`

---

## FRONTEND DEPLOYMENT (VERCEL)

### Step 1: Prepare Repository
1. Ensure `vercel.json` is in the frontend root
2. Ensure `.env.production` is configured with your backend URL
3. Update `VITE_API_URL` in both files

### Step 2: Deploy to Vercel
1. Go to Vercel Dashboard → New Project
2. Import your GitHub repository
3. Select the `frontend` directory
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

### Step 3: Configure Environment Variables
1. In Vercel project settings → Environment Variables
2. Add:
   - `VITE_API_URL`: `https://your-backend-domain.onrender.com`
   - Replace with your actual Render backend URL

### Step 4: Deploy
1. Vercel will automatically deploy
2. You'll get a `.vercel.app` domain
3. Test the frontend loads and connects to backend

---

## POST-DEPLOYMENT CONFIGURATION

### Update CORS Settings
In your Render environment variables, update:
```bash
CORS_ORIGINS=["https://your-frontend-domain.vercel.app"]
```

### Database Migration
1. SSH into your Render service
2. Run database migrations:
```bash
cd /app
alembic upgrade head
```

### Test Integration
1. Upload a test resume through the frontend
2. Check parsing results
3. Monitor logs in both Render and Vercel

---

## TROUBLESHOOTING

### Common Issues

#### Backend Issues
1. **Build Failures**: Check Dockerfile.render and dependencies
2. **Database Connection**: Verify DATABASE_URL format
3. **CORS Errors**: Update CORS_ORIGINS environment variable
4. **Health Check Fails**: Ensure `/health` endpoint is accessible

#### Frontend Issues
1. **Build Failures**: Check package.json and dependencies
2. **API Connection Errors**: Verify VITE_API_URL
3. **CORS Issues**: Backend CORS configuration

#### Integration Issues
1. **Timeout Errors**: Increase timeout in gunicorn command
2. **File Upload Issues**: Check file size limits
3. **OCR Processing**: Ensure Tesseract is properly installed

### Monitoring
- **Render**: Check logs in dashboard
- **Vercel**: Check Functions logs
- **Database**: Monitor connection pool
- **Redis**: Monitor memory usage

---

## SECURITY CONSIDERATIONS

1. **Environment Variables**: Never commit secrets to git
2. **Database**: Use SSL connections
3. **API Keys**: Rotate regularly
4. **CORS**: Restrict to specific domains
5. **File Uploads**: Validate file types and sizes

---

## PERFORMANCE OPTIMIZATION

1. **Backend**: Enable Redis caching
2. **Frontend**: Use Vercel's CDN
3. **Database**: Add proper indexes
4. **Images**: Optimize file sizes
5. **Monitoring**: Set up alerts

---

## CUSTOM DOMAINS (Optional)

### Frontend (Vercel)
1. Go to Vercel project → Domains
2. Add your custom domain
3. Configure DNS records

### Backend (Render)
1. Go to Render service → Custom Domains
2. Add your custom domain
3. Configure DNS records

---

## COST ESTIMATES

### Render (Free Tier)
- Web Service: $0/month (limited hours)
- PostgreSQL: $0/month (256MB)
- Redis: $0/month (25MB)

### Vercel (Hobby)
- Frontend: $0/month (Personal)
- Bandwidth: 100GB/month
- Build Time: Limited

### Paid Plans
- Render Pro: $25/month
- Vercel Pro: $20/month

---

## SUPPORT

- **Render Documentation**: https://render.com/docs
- **Vercel Documentation**: https://vercel.com/docs
- **GitHub Issues**: For application-specific issues

---

## NEXT STEPS

1. Deploy backend to Render
2. Deploy frontend to Vercel
3. Test full integration
4. Set up monitoring
5. Configure custom domains
6. Set up backup strategies

---

**Note**: This deployment uses the current rule-based parsing system. To achieve 85-90% accuracy, implement the spaCy NER fine-tuning pipeline as outlined in the technical gap analysis.
