"""
API endpoints for feedback collection and management.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

from app.services.orchestrator import Orchestrator
from app.models.feedback import Feedback, FeedbackRequest, FeedbackResponse
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class SubmitFeedbackRequest(BaseModel):
    """Request model for submitting feedback."""
    idea_id: str = Field(..., description="ID of the idea being feedback on")
    feedback_type: str = Field(..., description="Type of feedback (critique, suggestion, rating)")
    content: str = Field(..., description="Feedback content")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1-5")
    categories: List[str] = Field(default_factory=list, description="Feedback categories")
    user_id: Optional[str] = Field(None, description="User ID (if authenticated)")


class GetFeedbackResponse(BaseModel):
    """Response model for getting feedback."""
    feedback: List[Feedback]
    total: int
    page: int
    page_size: int


@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(
    request: SubmitFeedbackRequest,
    orchestrator: Orchestrator = Depends(lambda: Orchestrator())
):
    """
    Submit feedback for an idea.
    
    This endpoint allows users to provide feedback on generated ideas,
    which can be used for iterative improvement.
    """
    try:
        logger.info(f"Submitting feedback for idea: {request.idea_id}")
        
        # Create feedback object
        feedback = Feedback(
            id=str(uuid.uuid4()),
            idea_id=request.idea_id,
            feedback_type=request.feedback_type,
            content=request.content,
            rating=request.rating,
            categories=request.categories,
            user_id=request.user_id,
            created_at=datetime.utcnow()
        )
        
        # Save feedback
        saved_feedback = await orchestrator.submit_feedback(feedback)
        
        logger.info(f"Feedback submitted with ID: {saved_feedback.id}")
        
        return FeedbackResponse(
            feedback=saved_feedback,
            message="Feedback submitted successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")


@router.get("/idea/{idea_id}", response_model=GetFeedbackResponse)
async def get_feedback_for_idea(
    idea_id: str,
    page: int = 1,
    page_size: int = 10,
    feedback_type: Optional[str] = None,
    orchestrator: Orchestrator = Depends(lambda: Orchestrator())
):
    """
    Get all feedback for a specific idea.
    
    Args:
        idea_id: ID of the idea
        page: Page number (1-based)
        page_size: Number of feedback items per page
        feedback_type: Filter by feedback type
    """
    try:
        logger.info(f"Fetching feedback for idea: {idea_id}")
        
        feedback_list = await orchestrator.get_feedback_for_idea(
            idea_id=idea_id,
            page=page,
            page_size=page_size,
            feedback_type=feedback_type
        )
        
        # Mock total count (would normally come from database)
        total = len(feedback_list) + (page - 1) * page_size
        
        return GetFeedbackResponse(
            feedback=feedback_list,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Failed to get feedback for idea {idea_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get feedback: {str(e)}")


@router.get("/{feedback_id}")
async def get_feedback(
    feedback_id: str,
    orchestrator: Orchestrator = Depends(lambda: Orchestrator())
):
    """
    Get a specific feedback item by ID.
    
    Args:
        feedback_id: Unique identifier for the feedback
    """
    try:
        logger.info(f"Fetching feedback: {feedback_id}")
        
        feedback = await orchestrator.get_feedback(feedback_id)
        
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        return feedback
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get feedback {feedback_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get feedback: {str(e)}")


@router.put("/{feedback_id}")
async def update_feedback(
    feedback_id: str,
    request: SubmitFeedbackRequest,
    orchestrator: Orchestrator = Depends(lambda: Orchestrator())
):
    """
    Update an existing feedback item.
    
    Args:
        feedback_id: Unique identifier for the feedback
        request: Updated feedback data
    """
    try:
        logger.info(f"Updating feedback: {feedback_id}")
        
        # Create updated feedback object
        updated_feedback = Feedback(
            id=feedback_id,
            idea_id=request.idea_id,
            feedback_type=request.feedback_type,
            content=request.content,
            rating=request.rating,
            categories=request.categories,
            user_id=request.user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        success = await orchestrator.update_feedback(updated_feedback)
        
        if not success:
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        return {"message": "Feedback updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update feedback {feedback_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update feedback: {str(e)}")


@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: str,
    orchestrator: Orchestrator = Depends(lambda: Orchestrator())
):
    """
    Delete a feedback item.
    
    Args:
        feedback_id: Unique identifier for the feedback
    """
    try:
        logger.info(f"Deleting feedback: {feedback_id}")
        
        success = await orchestrator.delete_feedback(feedback_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        return {"message": "Feedback deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete feedback {feedback_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete feedback: {str(e)}")


@router.get("/analytics/summary")
async def get_feedback_analytics(
    idea_id: Optional[str] = None,
    days: int = 30,
    orchestrator: Orchestrator = Depends(lambda: Orchestrator())
):
    """
    Get feedback analytics and summary.
    
    Args:
        idea_id: Optional idea ID to filter by
        days: Number of days to look back
    """
    try:
        logger.info(f"Fetching feedback analytics for {days} days")
        
        analytics = await orchestrator.get_feedback_analytics(
            idea_id=idea_id,
            days=days
        )
        
        return analytics
        
    except Exception as e:
        logger.error(f"Failed to get feedback analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")
