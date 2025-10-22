# 🚀 Simple Vercel Deployment (No vercel.json needed!)

This guide shows you how to deploy your AI Startup Co-Founder app on Vercel using the **automatic detection** - no configuration files required!

## 📋 Prerequisites

- [Vercel account](https://vercel.com) (free tier available)
- [GitHub account](https://github.com) 
- [Google AI Studio account](https://aistudio.google.com) (for Gemini API key)

## 🚀 Step-by-Step Deployment

### **Step 1: Push to GitHub**

```bash
git add .
git commit -m "Ready for Vercel deployment"
git push origin main
```

### **Step 2: Deploy Frontend (Next.js)**

1. **Go to [Vercel Dashboard](https://vercel.com/dashboard)**
2. **Click "New Project"**
3. **Import from GitHub:**
   - Select your repository
   - **IMPORTANT**: Set root directory to `frontend/web`
4. **Vercel will auto-detect Next.js!** ✨
5. **Add Environment Variable:**
   ```
   NEXT_PUBLIC_API_URL = http://localhost:8000
   ```
6. **Click "Deploy"**

### **Step 3: Deploy Backend (FastAPI)**

#### **Option A: Vercel Serverless Functions**

1. **Create new Vercel project**
2. **Set root directory to `api`**
3. **Vercel will auto-detect Python!** ✨
4. **Add Environment Variables:**
   ```
   GEMINI_API_KEY = your_gemini_api_key_here
   ```
5. **Click "Deploy"**

#### **Option B: Keep Backend Local (Easiest)**

For development, you can keep the backend running locally and just deploy the frontend:

1. **Run backend locally:**
   ```bash
   cd services/backend
   docker-compose up -d
   ```

2. **Update frontend environment variable:**
   ```
   NEXT_PUBLIC_API_URL = http://localhost:8000
   ```

### **Step 4: Update CORS (If using local backend)**

If you're running backend locally, update the CORS settings:

```python
# In services/backend/app/core/config.py
CORS_ORIGINS: List[str] = Field(
    default=["http://localhost:3000", "https://your-frontend.vercel.app"],
    env="CORS_ORIGINS"
)
```

## 🎯 That's It!

Vercel's automatic detection handles everything:

- **Next.js**: Auto-detected from `package.json`
- **Python**: Auto-detected from `requirements.txt`
- **Build commands**: Auto-generated
- **Output directories**: Auto-configured

## 🔧 Environment Variables

### **Frontend (Next.js)**
```
NEXT_PUBLIC_API_URL = https://your-backend.vercel.app
```

### **Backend (FastAPI)**
```
GEMINI_API_KEY = your_gemini_api_key_here
CORS_ORIGINS = ["https://your-frontend.vercel.app"]
```

## 🚨 Troubleshooting

### **Common Issues:**

1. **Build Fails:**
   - Check Node.js version (use 18.x)
   - Ensure all dependencies are in `package.json`

2. **API Not Working:**
   - Check CORS settings
   - Verify environment variables
   - Check Vercel function logs

3. **Frontend Can't Connect to Backend:**
   - Update `NEXT_PUBLIC_API_URL`
   - Check backend deployment URL

## 🎉 Benefits of This Approach

- ✅ **No configuration files needed**
- ✅ **Automatic detection**
- ✅ **Zero setup complexity**
- ✅ **Easy to understand**
- ✅ **Quick deployment**

## 🚀 Go Live!

1. **Deploy frontend to Vercel**
2. **Deploy backend to Vercel** (or keep local)
3. **Update environment variables**
4. **Test your app!**

Your AI Startup Co-Founder is now live! 🎉
