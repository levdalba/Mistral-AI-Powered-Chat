# 🚀 Deployment Guide

Complete guide for deploying the Mistral AI Chat Application to production.

## 📋 Pre-Deployment Checklist

- [ ] Mistral AI API key obtained from [console.mistral.ai](https://console.mistral.ai/)
- [ ] GitHub repository with latest code
- [ ] Environment variables documented
- [ ] Testing completed locally

## 🌐 Frontend Deployment

### Option 1: Vercel (Recommended)

**Why Vercel?**
- ✅ Zero-config Next.js deployment
- ✅ Automatic HTTPS and CDN
- ✅ Preview deployments for pull requests
- ✅ Built-in analytics

**Steps:**
1. **Connect Repository**
   ```bash
   # Visit vercel.com and connect your GitHub account
   # Import your repository: Mistral-AI-Powered-Chat
   ```

2. **Configure Build Settings**
   ```bash
   Framework Preset: Next.js
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

3. **Environment Variables**
   ```bash
   # In Vercel Dashboard > Settings > Environment Variables
   NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.railway.app
   ```

4. **Deploy**
   ```bash
   # Automatic deployment on every git push to main branch
   # Manual deployment: vercel --prod
   ```

**Live URL:** `https://your-app-name.vercel.app`

### Option 2: Netlify

**Steps:**
1. **Build Locally**
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy**
   ```bash
   # Drag and drop .next/out folder to netlify.com
   # Or connect GitHub repository
   ```

3. **Environment Variables**
   ```bash
   # In Netlify Dashboard > Site settings > Environment variables
   NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.railway.app
   ```

### Option 3: GitHub Pages

**Steps:**
1. **Configure Next.js for Static Export**
   ```javascript
   // next.config.js
   /** @type {import('next').NextConfig} */
   const nextConfig = {
       output: 'export',
       trailingSlash: true,
       images: {
           unoptimized: true
       }
   }
   module.exports = nextConfig
   ```

2. **Build and Deploy**
   ```bash
   cd frontend
   npm run build
   
   # Copy out/ folder to gh-pages branch
   # Enable GitHub Pages in repository settings
   ```

## 🔧 Backend Deployment

### Option 1: Railway (Recommended)

**Why Railway?**
- ✅ Simple Python deployment
- ✅ Automatic scaling
- ✅ Built-in monitoring
- ✅ Environment variable management

**Steps:**
1. **Connect Repository**
   ```bash
   # Visit railway.app and connect GitHub
   # Select your repository: Mistral-AI-Powered-Chat
   ```

2. **Configure Service**
   ```bash
   Root Directory: backend
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

3. **Environment Variables**
   ```bash
   # In Railway Dashboard > Variables
   MISTRAL_API_KEY=your_mistral_api_key_here
   PORT=8000
   ```

4. **Deploy**
   ```bash
   # Automatic deployment on git push
   # Manual deployment through Railway dashboard
   ```

**Live URL:** `https://your-service-name.railway.app`

### Option 2: Render

**Steps:**
1. **Create Web Service**
   ```bash
   # Visit render.com and connect GitHub
   # Create new Web Service
   ```

2. **Configuration**
   ```bash
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

3. **Environment Variables**
   ```bash
   MISTRAL_API_KEY=your_mistral_api_key_here
   ```

### Option 3: Heroku

**Steps:**
1. **Install Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Login
   heroku login
   ```

2. **Create App**
   ```bash
   cd backend
   heroku create your-app-name
   ```

3. **Configure**
   ```bash
   # Create Procfile
   echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile
   
   # Set environment variables
   heroku config:set MISTRAL_API_KEY=your_mistral_api_key_here
   ```

4. **Deploy**
   ```bash
   git subtree push --prefix backend heroku main
   ```

## 🐳 Docker Deployment

### Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MISTRAL_API_KEY=${MISTRAL_API_KEY}
    
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
    depends_on:
      - backend
```

## 🔧 Environment Configuration

### Production Environment Variables

**Backend (.env)**
```bash
MISTRAL_API_KEY=your_mistral_api_key_here
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Frontend (.env.local)**
```bash
NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain.com
NEXT_PUBLIC_ENVIRONMENT=production
```

## 📊 Monitoring & Analytics

### Health Checks

```bash
# Backend health check
curl https://your-backend-url.com/health

# Expected response:
# {"status": "healthy", "timestamp": "2025-01-09T..."}
```

### Performance Monitoring

**Backend Monitoring:**
```python
# Add to main.py for production monitoring
import logging
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    return response
```

### Error Tracking

Consider integrating:
- **Sentry** for error tracking
- **LogRocket** for frontend monitoring
- **DataDog** for comprehensive monitoring

## 🚨 Troubleshooting

### Common Issues

**1. CORS Errors**
```bash
# Ensure backend CORS is configured for your frontend domain
# In backend/app/main.py, update origins:
origins = [
    "https://your-frontend-domain.vercel.app",
    "http://localhost:3000",
    "http://localhost:3001"
]
```

**2. Environment Variables Not Loading**
```bash
# Check environment variable names match exactly
# Restart services after environment changes
# Use deployment platform's environment variable interface
```

**3. Build Failures**
```bash
# Frontend build issues
cd frontend && npm run build
# Check for TypeScript errors and fix them

# Backend deployment issues  
cd backend && pip install -r requirements.txt
# Check Python version compatibility
```

**4. API Connection Issues**
```bash
# Test API connectivity
curl -X POST https://your-backend-url.com/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "model": "mistral-large-latest"}'
```

## 📈 Performance Optimization

### Frontend Optimization

```bash
# Enable compression in next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
    compress: true,
    poweredByHeader: false,
    generateEtags: false,
}
```

### Backend Optimization

```python
# Add caching headers in main.py
from fastapi.responses import JSONResponse

@app.get("/api/health")
async def health_check():
    return JSONResponse(
        content={"status": "healthy"},
        headers={"Cache-Control": "no-cache"}
    )
```

## 🔐 Security Considerations

### Production Security Checklist

- [ ] HTTPS enabled on both frontend and backend
- [ ] Environment variables secured (never commit API keys)
- [ ] CORS configured for specific domains only
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] Error messages don't expose sensitive information

### Security Headers

```python
# Add security headers in backend
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["your-domain.com", "*.your-domain.com"]
)
```

## 🎯 Go-Live Checklist

- [ ] ✅ Backend deployed and health check passing
- [ ] ✅ Frontend deployed and accessible
- [ ] ✅ Environment variables configured
- [ ] ✅ CORS working between frontend and backend
- [ ] ✅ Chat functionality tested end-to-end
- [ ] ✅ Error handling working properly
- [ ] ✅ Rate limiting tested
- [ ] ✅ Performance monitoring enabled
- [ ] ✅ Custom domain configured (optional)
- [ ] ✅ SSL certificate active

## 📞 Support

If you encounter deployment issues:

1. Check the deployment platform's logs
2. Test locally with production environment variables
3. Use the integration test script: `./test_integration.sh`
4. Verify all environment variables are set correctly
5. Check network connectivity between frontend and backend

**Happy Deploying! 🚀**
