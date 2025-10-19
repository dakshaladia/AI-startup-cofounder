"""
FastAPI main application for AI Startup Co-Founder backend service.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import os
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logger import get_logger
from app.api.v1 import ideas, feedback
from app.services.orchestrator import Orchestrator
from app.services.persistence import PersistenceService
from app.core.queue import QueueManager

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting AI Startup Co-Founder backend service...")
    
    # Initialize services
    app.state.orchestrator = Orchestrator()
    app.state.persistence = PersistenceService()
    app.state.queue = QueueManager()
    
    # Initialize database connections
    await app.state.persistence.initialize()
    await app.state.queue.initialize()
    
    logger.info("Backend service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down backend service...")
    await app.state.persistence.close()
    await app.state.queue.close()
    logger.info("Backend service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="AI Startup Co-Founder API",
    description="Multimodal AI Startup Co-Founder with multi-agent pipeline",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["localhost", "127.0.0.1"]
)

# Include API routers
app.include_router(ideas.router, prefix="/api/v1/ideas", tags=["ideas"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["feedback"])


@app.get("/")
async def root():
    """Root endpoint with basic service information."""
    return {
        "service": "AI Startup Co-Founder API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check database connection
        await app.state.persistence.health_check()
        
        # Check queue connection
        await app.state.queue.health_check()
        
        return {
            "status": "healthy",
            "database": "connected",
            "queue": "connected",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.AUTO_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
