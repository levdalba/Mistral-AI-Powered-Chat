# Render Deployment Guide for FastAPI Backend

## 🎯 Deploy to Render (100% Free)

### Step 1: Prepare Your Repository
Your repository is already configured correctly!

### Step 2: Deploy to Render

1. **Go to render.com**
2. **Sign up/Login** with your GitHub account
3. **Click "New +"** → **"Web Service"**
4. **Connect Repository**: Select `levdalba/Mistral-AI-Powered-Chat`
5. **Configure Service**:
   ```
   Name: mistral-chat-backend
   Branch: feature/initial-project-setup
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### Step 3: Environment Variables
In Render dashboard, add these environment variables:
```
MISTRAL_API_KEY=your_mistral_api_key_here
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=["https://your-frontend-url.vercel.app","http://localhost:3000"]
```

### Step 4: Get Your Backend URL
After deployment, you'll get a URL like:
`https://mistral-chat-backend.onrender.com`

### Notes:
- ✅ **Free forever**
- ⚠️ **Sleeps after 15 minutes** of inactivity
- ⚠️ **Cold start delay** (~30 seconds when waking up)
- 💡 **Keep-alive tip**: Use a service like UptimeRobot to ping every 14 minutes

---

## Alternative: Fly.io (Also Free)

1. **Install Fly CLI**: `brew install flyctl`
2. **Login**: `fly auth login`
3. **In backend directory**: `fly launch`
4. **Follow prompts** and deploy

Your backend will be available at: `https://your-app-name.fly.dev`
