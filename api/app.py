from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Startup Co-Founder API",
    description="Backend API for AI-powered startup idea generation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://ai-startup-cofounder-1upj-8f537ml1e-daksha-ladias-projects.vercel.app",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class GenerateRequest(BaseModel):
    topic: str
    constraints: Dict[str, Any] = {}
    num_ideas: int = 3
    model_settings: Optional[Dict[str, str]] = None

class IterateRequest(BaseModel):
    idea_id: str
    feedback: str
    iteration_type: str
    focus_areas: List[str] = []
    constraints: Dict[str, Any] = {}
    model_settings: Optional[Dict[str, str]] = None

class IdeaResponse(BaseModel):
    id: str
    title: str
    description: str
    overall_score: float
    feasibility_score: float
    novelty_score: float
    market_signal_score: float
    market_analysis: Dict[str, Any]
    critic_output: Dict[str, Any]
    pm_refiner_output: Dict[str, Any]
    synthesizer_output: Dict[str, Any]

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "AI Startup Co-Founder API", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# API endpoints
@app.post("/api/v1/ideas/generate", response_model=List[IdeaResponse])
async def generate_ideas(request: GenerateRequest):
    """
    Generate startup ideas based on topic and constraints
    """
    try:
        logger.info(f"Generating ideas for topic: {request.topic}")
        print(f"DEBUG: Received request for topic: {request.topic}")
        
        # Mock response for now - replace with actual orchestrator logic
        mock_ideas = [
            {
                "id": "idea_1",
                "title": f"AI-powered {request.topic} solution",
                "description": f"An innovative AI solution for {request.topic} that leverages machine learning to solve complex problems.",
                "overall_score": 0.85,
                "feasibility_score": 0.78,
                "novelty_score": 0.92,
                "market_signal_score": 0.81,
                "market_analysis": {
                    "market_size": "$2.5B",
                    "growth_rate": "15%",
                    "competition": "Medium",
                    "current_players": ["Company A", "Company B"]
                },
                "critic_output": {
                    "strengths": ["Strong market demand", "Scalable technology"],
                    "weaknesses": ["High development cost", "Regulatory challenges"],
                    "recommendations": ["Focus on MVP", "Secure funding early"]
                },
                "pm_refiner_output": {
                    "target_users": "Tech-savvy professionals",
                    "key_features": ["AI automation", "Real-time analytics"],
                    "business_model": "SaaS subscription"
                },
                "synthesizer_output": {
                    "final_concept": f"Revolutionary AI platform for {request.topic}",
                    "implementation_plan": "6-month development cycle",
                    "success_metrics": ["User adoption", "Revenue growth"]
                }
            }
        ]
        
        return mock_ideas
        
    except Exception as e:
        logger.error(f"Error generating ideas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ideas/iterate", response_model=IdeaResponse)
async def iterate_idea(request: IterateRequest):
    """
    Iterate on an existing idea based on feedback
    """
    try:
        logger.info(f"Iterating idea {request.idea_id} with feedback: {request.feedback}")
        
        # Mock response for now - replace with actual orchestrator logic
        mock_idea = {
            "id": request.idea_id,
            "title": f"Improved AI-powered solution",
            "description": f"Enhanced version incorporating feedback: {request.feedback}",
            "overall_score": 0.91,
            "feasibility_score": 0.85,
            "novelty_score": 0.95,
            "market_signal_score": 0.88,
            "market_analysis": {
                "market_size": "$3.2B",
                "growth_rate": "18%",
                "competition": "Low",
                "current_players": ["Company A", "Company B", "Company C"]
            },
            "critic_output": {
                "strengths": ["Improved market positioning", "Better user experience"],
                "weaknesses": ["Increased complexity"],
                "recommendations": ["Focus on core features", "User testing"]
            },
            "pm_refiner_output": {
                "target_users": "Expanded user base",
                "key_features": ["Enhanced AI", "Better UX", "Mobile support"],
                "business_model": "Freemium SaaS"
            },
            "synthesizer_output": {
                "final_concept": f"Next-generation AI platform incorporating user feedback",
                "implementation_plan": "8-month development cycle",
                "success_metrics": ["User satisfaction", "Market penetration"]
            }
        }
        
        return mock_idea
        
    except Exception as e:
        logger.error(f"Error iterating idea: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/ideas/{idea_id}", response_model=IdeaResponse)
async def get_idea(idea_id: str):
    """
    Get a specific idea by ID
    """
    try:
        logger.info(f"Fetching idea: {idea_id}")
        
        # Mock response - replace with actual database query
        mock_idea = {
            "id": idea_id,
            "title": "Sample AI Startup Idea",
            "description": "A comprehensive AI solution for modern businesses",
            "overall_score": 0.87,
            "feasibility_score": 0.82,
            "novelty_score": 0.90,
            "market_signal_score": 0.85,
            "market_analysis": {
                "market_size": "$2.8B",
                "growth_rate": "16%",
                "competition": "Medium",
                "current_players": ["Company A", "Company B"]
            },
            "critic_output": {
                "strengths": ["Strong market demand", "Scalable technology"],
                "weaknesses": ["High development cost"],
                "recommendations": ["Focus on MVP"]
            },
            "pm_refiner_output": {
                "target_users": "Tech professionals",
                "key_features": ["AI automation", "Analytics"],
                "business_model": "SaaS"
            },
            "synthesizer_output": {
                "final_concept": "AI-powered business solution",
                "implementation_plan": "6-month cycle",
                "success_metrics": ["User adoption", "Revenue"]
            }
        }
        
        return mock_idea
        
    except Exception as e:
        logger.error(f"Error fetching idea: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
