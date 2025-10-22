# 🚀 Vercel Deployment Guide

This guide will help you deploy the AI Startup Co-Founder application on Vercel.

## 📋 Prerequisites

- [Vercel account](https://vercel.com) (free tier available)
- [GitHub account](https://github.com) (for repository hosting)
- [Google AI Studio account](https://aistudio.google.com) (for Gemini API key)

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        VERCEL DEPLOYMENT                           │
│                                                                     │
│  Frontend (Next.js) → Vercel Edge Network                          │
│         │                                                           │
│         ▼                                                           │
│  Backend (FastAPI) → Vercel Serverless Functions                   │
│         │                                                           │
│         ▼                                                           │
│  Database → External Service (Neon, Supabase, or PlanetScale)     │
│         │                                                           │
│         ▼                                                           │
│  AI Models → Google Gemini API (External)                         │
└─────────────────────────────────────────────────────────────────────┘
```

## 🚀 Step-by-Step Deployment

### **Step 1: Prepare Your Repository**

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Create Environment Variables File:**
   ```bash
   # Create .env.local for frontend
   echo "NEXT_PUBLIC_API_URL=https://your-backend-api.vercel.app" > frontend/web/.env.local
   ```

### **Step 2: Deploy Backend API**

#### **Option A: Vercel Serverless Functions**

1. **Create `api/` directory in root:**
   ```bash
   mkdir -p api
   ```

2. **Create `api/ideas.py`:**
   ```python
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware
   import os
   
   app = FastAPI()
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend.vercel.app"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   
   @app.get("/")
   async def root():
       return {"message": "AI Startup Co-Founder API"}
   
   # Add your existing API routes here
   ```

3. **Create `api/requirements.txt`:**
   ```
   fastapi==0.104.1
   uvicorn==0.24.0
   pydantic==2.5.0
   google-generativeai==0.8.3
   ```

#### **Option B: Separate Backend Service (Recommended)**

Deploy backend to a separate Vercel project or use Railway/Render for the backend.

### **Step 3: Deploy Frontend**

1. **Go to [Vercel Dashboard](https://vercel.com/dashboard)**

2. **Click "New Project"**

3. **Import from GitHub:**
   - Select your repository
   - Choose "frontend/web" as root directory

4. **Configure Build Settings:**
   ```
   Framework Preset: Next.js
   Root Directory: frontend/web
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

5. **Set Environment Variables:**
   ```
   NEXT_PUBLIC_API_URL = https://your-backend-api.vercel.app
   GEMINI_API_KEY = your_gemini_api_key_here
   ```

6. **Deploy!**

### **Step 4: Configure Database**

#### **Option A: Neon (Recommended)**
1. Go to [Neon Console](https://console.neon.tech)
2. Create new project
3. Get connection string
4. Add to backend environment variables:
   ```
   DATABASE_URL = postgresql://user:password@host/database
   ```

#### **Option B: Supabase**
1. Go to [Supabase Dashboard](https://supabase.com)
2. Create new project
3. Get connection string
4. Add to backend environment variables

#### **Option C: PlanetScale**
1. Go to [PlanetScale Dashboard](https://planetscale.com)
2. Create new database
3. Get connection string
4. Add to backend environment variables

### **Step 5: Set Up Database Schema**

Create the following tables in your database:

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Ideas table
CREATE TABLE ideas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    topic VARCHAR(200),
    overall_score DECIMAL(3,2),
    feasibility_score DECIMAL(3,2),
    novelty_score DECIMAL(3,2),
    market_signal_score DECIMAL(3,2),
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    version INTEGER DEFAULT 1
);

-- Agent outputs table
CREATE TABLE agent_outputs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_id UUID REFERENCES ideas(id),
    agent_type VARCHAR(50) NOT NULL,
    output JSONB,
    model_used VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    filename VARCHAR(255),
    content TEXT,
    embeddings VECTOR(1536),
    processed_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_ideas_user_id ON ideas(user_id);
CREATE INDEX idx_ideas_topic ON ideas(topic);
CREATE INDEX idx_ideas_score ON ideas(overall_score);
CREATE INDEX idx_agent_outputs_idea_id ON agent_outputs(idea_id);
```

### **Step 6: Update Backend for Production**

1. **Update `services/backend/app/core/config.py`:**
   ```python
   class Settings(BaseSettings):
       # Database
       DATABASE_URL: str = Field(..., env="DATABASE_URL")
       
       # CORS
       CORS_ORIGINS: List[str] = Field(
           default=["https://your-frontend.vercel.app"],
           env="CORS_ORIGINS"
       )
       
       # Gemini API
       GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY")
       
       class Config:
           env_file = ".env"
   ```

2. **Update persistence service to use real database:**
   ```python
   import asyncpg
   
   class PersistenceService:
       async def _init_database(self):
           self.db_client = await asyncpg.connect(settings.DATABASE_URL)
   ```

### **Step 7: Environment Variables**

Set these in your Vercel project settings:

#### **Frontend Environment Variables:**
```
NEXT_PUBLIC_API_URL = https://your-backend-api.vercel.app
```

#### **Backend Environment Variables:**
```
DATABASE_URL = postgresql://user:password@host/database
GEMINI_API_KEY = your_gemini_api_key_here
CORS_ORIGINS = ["https://your-frontend.vercel.app"]
LLM_PROVIDER = gemini
LLM_MODEL = gemini-2.0-flash-lite
```

### **Step 8: Custom Domain (Optional)**

1. **In Vercel Dashboard:**
   - Go to your project
   - Click "Domains"
   - Add your custom domain
   - Configure DNS records

2. **Update CORS settings:**
   ```
   CORS_ORIGINS = ["https://yourdomain.com"]
   ```

## 🔧 Production Optimizations

### **1. Performance Optimizations**

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverComponentsExternalPackages: ['@google/generativeai']
  },
  images: {
    domains: ['your-domain.com']
  },
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization' }
        ]
      }
    ]
  }
}

module.exports = nextConfig
```

### **2. Database Connection Pooling**

```python
# services/backend/app/core/database.py
import asyncpg
from typing import Optional

class DatabasePool:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def create_pool(self, database_url: str):
        self.pool = await asyncpg.create_pool(
            database_url,
            min_size=1,
            max_size=10,
            command_timeout=60
        )
    
    async def close_pool(self):
        if self.pool:
            await self.pool.close()
```

### **3. Error Handling**

```python
# services/backend/app/core/error_handlers.py
from fastapi import HTTPException
import logging

async def handle_database_error(e: Exception):
    logging.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Database connection failed")

async def handle_llm_error(e: Exception):
    logging.error(f"LLM error: {e}")
    raise HTTPException(status_code=500, detail="AI service temporarily unavailable")
```

## 📊 Monitoring & Analytics

### **1. Vercel Analytics**
- Built-in performance monitoring
- Real-time metrics
- Error tracking

### **2. Custom Monitoring**
```python
# Add to your backend
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start_time
        
        # Log to your monitoring service
        logging.info(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper
```

## 🚨 Troubleshooting

### **Common Issues:**

1. **CORS Errors:**
   ```
   Solution: Update CORS_ORIGINS in backend environment variables
   ```

2. **Database Connection Errors:**
   ```
   Solution: Check DATABASE_URL format and credentials
   ```

3. **API Timeout:**
   ```
   Solution: Increase Vercel function timeout in vercel.json
   ```

4. **Build Failures:**
   ```
   Solution: Check Node.js version compatibility
   ```

### **Debug Commands:**

```bash
# Check Vercel deployment logs
vercel logs

# Check function performance
vercel inspect

# Test API endpoints
curl https://your-backend-api.vercel.app/api/health
```

## 🎯 Final Checklist

- [ ] Repository pushed to GitHub
- [ ] Backend deployed to Vercel
- [ ] Frontend deployed to Vercel
- [ ] Database configured and schema created
- [ ] Environment variables set
- [ ] CORS configured correctly
- [ ] Custom domain configured (optional)
- [ ] Monitoring set up
- [ ] Error handling implemented
- [ ] Performance optimizations applied

## 🚀 Go Live!

Once everything is configured:

1. **Test your deployment:**
   - Visit your Vercel URL
   - Generate some ideas
   - Check database for stored data

2. **Monitor performance:**
   - Check Vercel Analytics
   - Monitor database performance
   - Watch for errors

3. **Scale as needed:**
   - Upgrade Vercel plan if needed
   - Optimize database queries
   - Add caching layers

Your AI Startup Co-Founder is now live on Vercel! 🎉
