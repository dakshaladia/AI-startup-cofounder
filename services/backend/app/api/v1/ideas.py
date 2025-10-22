"""
API endpoints for idea generation and management.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

from app.services.orchestrator import Orchestrator
from app.models.idea import IdeaSnapshot, GenerateRequest, IterateRequest
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class GenerateResponse(BaseModel):
    """Response model for idea generation."""
    ideas: List[IdeaSnapshot]
    generation_id: str
    created_at: datetime


class IterateResponse(BaseModel):
    """Response model for idea iteration."""
    updated_idea: IdeaSnapshot
    iteration_id: str
    created_at: datetime


class GetIdeasResponse(BaseModel):
    """Response model for getting ideas."""
    ideas: List[IdeaSnapshot]
    total: int
    page: int
    page_size: int


@router.post("/generate", response_model=GenerateResponse)
async def generate_ideas(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
    orchestrator: Orchestrator = Depends(lambda: Orchestrator())
):
    """
    Generate new startup ideas based on topic and constraints.
    
    This endpoint triggers the multi-agent pipeline:
    1. Market Analyst - analyzes market conditions
    2. Idea Generator - creates initial ideas
    3. Critic - evaluates and critiques ideas
    4. PM/Refiner - refines ideas based on feedback
    5. Synthesizer - creates final polished ideas
    """
    try:
        logger.info(f"Generating ideas for topic: {request.topic}")
        
        # Generate ideas using orchestrator
        ideas = await orchestrator.generate_ideas(
            topic=request.topic,
            constraints=request.constraints,
            num_ideas=request.num_ideas or 3,
            model_settings=request.model_settings
        )
        
        generation_id = str(uuid.uuid4())
        
        # Log generation completion
        logger.info(f"Generated {len(ideas)} ideas with ID: {generation_id}")
        
        return GenerateResponse(
            ideas=ideas,
            generation_id=generation_id,
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Failed to generate ideas: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate ideas: {str(e)}")


@router.post("/iterate", response_model=IterateResponse)
async def iterate_idea(
    request: IterateRequest,
    background_tasks: BackgroundTasks,
    orchestrator: Orchestrator = Depends(lambda: Orchestrator())
):
    """
    Iterate on an existing idea based on feedback.
    
    This endpoint allows for iterative refinement of ideas:
    1. Takes existing idea and feedback
    2. Runs through critic and refiner agents
    3. Returns improved version
    """
    try:
        logger.info(f"Iterating on idea: {request.idea_id}")
        
        # Get existing idea from persistence
        existing_idea = await orchestrator.persistence.get_idea(request.idea_id)
        
        if not existing_idea:
            raise HTTPException(status_code=404, detail=f"Idea not found: {request.idea_id}")
        
        # Iterate on the idea
        improved_idea = await orchestrator.iterate_idea(
            idea=existing_idea,
            feedback=request.feedback,
            iteration_type=request.iteration_type,
            model_settings=request.model_settings
        )
        
        iteration_id = str(uuid.uuid4())
        
        logger.info(f"Iterated idea with ID: {iteration_id}")
        
        return IterateResponse(
            updated_idea=improved_idea,
            iteration_id=iteration_id,
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Failed to iterate idea: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to iterate idea: {str(e)}")


@router.get("/", response_model=GetIdeasResponse)
async def get_ideas(
    page: int = 1,
    page_size: int = 10,
    topic_filter: Optional[str] = None,
    min_score: Optional[float] = None,
    orchestrator: Orchestrator = Depends(lambda: Orchestrator())
):
    """
    Get paginated list of ideas with optional filtering.
    
    Args:
        page: Page number (1-based)
        page_size: Number of ideas per page
        topic_filter: Filter by topic keyword
        min_score: Minimum feasibility score
    """
    try:
        logger.info(f"Fetching ideas - page: {page}, size: {page_size}")
        
        # Get ideas from orchestrator (would normally query database)
        ideas = await orchestrator.get_ideas(
            page=page,
            page_size=page_size,
            topic_filter=topic_filter,
            min_score=min_score
        )
        
        # Mock total count (would normally come from database)
        total = len(ideas) + (page - 1) * page_size
        
        return GetIdeasResponse(
            ideas=ideas,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Failed to get ideas: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get ideas: {str(e)}")


@router.get("/{idea_id}")
async def get_idea(
    idea_id: str,
    orchestrator: Orchestrator = Depends(lambda: Orchestrator())
):
    """
    Get a specific idea by ID.
    
    Args:
        idea_id: Unique identifier for the idea
    """
    try:
        logger.info(f"Fetching idea: {idea_id}")
        
        idea = await orchestrator.get_idea(idea_id)
        
        if not idea:
            raise HTTPException(status_code=404, detail="Idea not found")
        
        return idea
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get idea {idea_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get idea: {str(e)}")


@router.delete("/{idea_id}")
async def delete_idea(
    idea_id: str,
    orchestrator: Orchestrator = Depends(lambda: Orchestrator())
):
    """
    Delete an idea by ID.
    
    Args:
        idea_id: Unique identifier for the idea
    """
    try:
        logger.info(f"Deleting idea: {idea_id}")
        
        success = await orchestrator.delete_idea(idea_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Idea not found")
        
        return {"message": "Idea deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete idea {idea_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete idea: {str(e)}")


@router.post("/{idea_id}/export")
async def export_idea(
    idea_id: str,
    format: str = "pdf",
    orchestrator: Orchestrator = Depends(lambda: Orchestrator())
):
    """
    Export an idea in various formats (PDF, PowerPoint, etc.).
    
    Args:
        idea_id: Unique identifier for the idea
        format: Export format (pdf, pptx, docx)
    """
    try:
        logger.info(f"Exporting idea {idea_id} as {format}")
        
        # Get the idea
        idea = await orchestrator.get_idea(idea_id)
        if not idea:
            raise HTTPException(status_code=404, detail="Idea not found")
        
        # Export the idea (would normally generate actual file)
        export_url = await orchestrator.export_idea(idea, format)
        
        return {
            "idea_id": idea_id,
            "format": format,
            "export_url": export_url,
            "created_at": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export idea {idea_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export idea: {str(e)}")
