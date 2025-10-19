"""
Orchestrator service for managing the multi-agent pipeline.
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.models.idea import IdeaSnapshot, GenerateRequest, IterateRequest, IdeaStatus
from app.models.feedback import Feedback
from app.services.persistence import PersistenceService
from app.services.analytics import AnalyticsService
from app.core.logger import get_logger

logger = get_logger(__name__)


class Orchestrator:
    """Orchestrates the multi-agent pipeline for idea generation and iteration."""
    
    def __init__(self):
        self.persistence = PersistenceService()
        self.analytics = AnalyticsService()
        self.agents = {}  # Will be populated with agent instances
    
    async def generate_ideas(
        self,
        topic: str,
        constraints: Dict[str, Any],
        num_ideas: int = 3
    ) -> List[IdeaSnapshot]:
        """
        Generate ideas using the multi-agent pipeline.
        
        Pipeline:
        1. Market Analyst - analyzes market conditions
        2. Idea Generator - creates initial ideas
        3. Critic - evaluates and critiques ideas
        4. PM/Refiner - refines ideas based on feedback
        5. Synthesizer - creates final polished ideas
        """
        try:
            logger.info(f"Starting idea generation for topic: {topic}")
            
            # Step 1: Market Analysis
            market_analysis = await self._run_market_analyst(topic, constraints)
            logger.info("Market analysis completed")
            
            # Step 2: Idea Generation
            raw_ideas = await self._run_idea_generator(topic, constraints, market_analysis, num_ideas)
            logger.info(f"Generated {len(raw_ideas)} raw ideas")
            
            # Step 3: Critique and Refinement
            refined_ideas = []
            for idea in raw_ideas:
                # Run critic
                critique = await self._run_critic(idea, market_analysis)
                
                # Run PM refiner
                refined_idea = await self._run_pm_refiner(idea, critique, constraints)
                
                # Run synthesizer
                final_idea = await self._run_synthesizer(refined_idea, market_analysis)
                
                # Convert to IdeaSnapshot if needed
                if isinstance(final_idea, dict):
                    final_idea = IdeaSnapshot(
                        id=final_idea.get('id', str(uuid.uuid4())),
                        title=final_idea.get('title', 'Untitled Idea'),
                        description=final_idea.get('description', 'No description'),
                        market_analysis=market_analysis,
                        feasibility_score=final_idea.get('feasibility_score', 0.5),
                        novelty_score=final_idea.get('novelty_score', 0.5),
                        market_signal_score=final_idea.get('market_signal_score', 0.5),
                        overall_score=final_idea.get('overall_score', 0.5),
                        status=IdeaStatus.COMPLETED
                    )
                
                refined_ideas.append(final_idea)
            
            # Step 4: Save ideas
            saved_ideas = []
            for idea in refined_ideas:
                saved_idea = await self.persistence.save_idea_snapshot(idea)
                saved_ideas.append(saved_idea)
            
            # Step 5: Analytics
            await self.analytics.track_idea_generation(topic, len(saved_ideas))
            
            logger.info(f"Idea generation completed: {len(saved_ideas)} ideas created")
            return saved_ideas
            
        except Exception as e:
            logger.error(f"Failed to generate ideas: {e}")
            raise
    
    async def iterate_idea(
        self,
        idea: IdeaSnapshot,
        feedback: str,
        iteration_type: str
    ) -> IdeaSnapshot:
        """
        Iterate on an existing idea based on feedback.
        
        Args:
            idea: Existing idea to iterate
            feedback: Feedback for improvement
            iteration_type: Type of iteration to perform
        """
        try:
            logger.info(f"Iterating idea {idea.id} with type: {iteration_type}")
            
            # Create new version
            new_idea = idea.copy()
            new_idea.id = str(uuid.uuid4())
            new_idea.version = idea.version + 1
            new_idea.status = IdeaStatus.REFINING
            new_idea.updated_at = datetime.utcnow()
            
            # Apply iteration based on type
            if iteration_type == "critique":
                critique = await self._run_critic(idea, None, feedback)
                new_idea.critic_output = critique
                
            elif iteration_type == "refinement":
                refined = await self._run_pm_refiner(idea, feedback, {})
                new_idea.pm_refiner_output = refined
                
            elif iteration_type == "synthesis":
                synthesized = await self._run_synthesizer(idea, None, feedback)
                new_idea.synthesizer_output = synthesized
                
            else:
                # General iteration
                new_idea.description = await self._apply_feedback(idea.description, feedback)
            
            # Update scores
            new_idea = await self._recalculate_scores(new_idea)
            
            # Save iteration
            saved_idea = await self.persistence.save_idea_snapshot(new_idea)
            
            # Track analytics
            await self.analytics.track_idea_iteration(idea.id, iteration_type)
            
            logger.info(f"Idea iteration completed: {saved_idea.id}")
            return saved_idea
            
        except Exception as e:
            logger.error(f"Failed to iterate idea: {e}")
            raise
    
    async def get_ideas(
        self,
        page: int = 1,
        page_size: int = 10,
        topic_filter: Optional[str] = None,
        min_score: Optional[float] = None
    ) -> List[IdeaSnapshot]:
        """Get paginated list of ideas with optional filtering."""
        try:
            return await self.persistence.get_ideas(
                page=page,
                page_size=page_size,
                topic_filter=topic_filter,
                min_score=min_score
            )
        except Exception as e:
            logger.error(f"Failed to get ideas: {e}")
            raise
    
    async def get_idea(self, idea_id: str) -> Optional[IdeaSnapshot]:
        """Get a specific idea by ID."""
        try:
            return await self.persistence.get_idea(idea_id)
        except Exception as e:
            logger.error(f"Failed to get idea {idea_id}: {e}")
            raise
    
    async def delete_idea(self, idea_id: str) -> bool:
        """Delete an idea by ID."""
        try:
            return await self.persistence.delete_idea(idea_id)
        except Exception as e:
            logger.error(f"Failed to delete idea {idea_id}: {e}")
            raise
    
    async def export_idea(self, idea: IdeaSnapshot, format: str) -> str:
        """Export an idea in the specified format."""
        try:
            # This would normally generate actual files
            # For now, return a mock URL
            export_url = f"/exports/{idea.id}.{format}"
            return export_url
        except Exception as e:
            logger.error(f"Failed to export idea: {e}")
            raise
    
    async def submit_feedback(self, feedback: Feedback) -> Feedback:
        """Submit feedback for an idea."""
        try:
            return await self.persistence.save_feedback(feedback)
        except Exception as e:
            logger.error(f"Failed to submit feedback: {e}")
            raise
    
    async def get_feedback_for_idea(
        self,
        idea_id: str,
        page: int = 1,
        page_size: int = 10,
        feedback_type: Optional[str] = None
    ) -> List[Feedback]:
        """Get feedback for a specific idea."""
        try:
            return await self.persistence.get_feedback_for_idea(
                idea_id=idea_id,
                page=page,
                page_size=page_size,
                feedback_type=feedback_type
            )
        except Exception as e:
            logger.error(f"Failed to get feedback for idea {idea_id}: {e}")
            raise
    
    async def get_feedback(self, feedback_id: str) -> Optional[Feedback]:
        """Get a specific feedback item."""
        try:
            return await self.persistence.get_feedback(feedback_id)
        except Exception as e:
            logger.error(f"Failed to get feedback {feedback_id}: {e}")
            raise
    
    async def update_feedback(self, feedback: Feedback) -> bool:
        """Update an existing feedback item."""
        try:
            return await self.persistence.update_feedback(feedback)
        except Exception as e:
            logger.error(f"Failed to update feedback: {e}")
            raise
    
    async def delete_feedback(self, feedback_id: str) -> bool:
        """Delete a feedback item."""
        try:
            return await self.persistence.delete_feedback(feedback_id)
        except Exception as e:
            logger.error(f"Failed to delete feedback {feedback_id}: {e}")
            raise
    
    async def get_feedback_analytics(
        self,
        idea_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get feedback analytics."""
        try:
            return await self.analytics.get_feedback_analytics(idea_id, days)
        except Exception as e:
            logger.error(f"Failed to get feedback analytics: {e}")
            raise
    
    # Private methods for agent execution
    
    async def _run_market_analyst(
        self,
        topic: str,
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run the market analyst agent."""
        # Mock implementation - would normally call actual agent
        return {
            "market_size": "Large",
            "competition_level": "High",
            "growth_potential": "High",
            "key_trends": ["AI adoption", "Remote work", "Sustainability"],
            "target_segments": ["SMBs", "Enterprises", "Consumers"]
        }
    
    async def _run_idea_generator(
        self,
        topic: str,
        constraints: Dict[str, Any],
        market_analysis: Dict[str, Any],
        num_ideas: int
    ) -> List[IdeaSnapshot]:
        """Run the idea generator agent."""
        # Mock implementation - would normally call actual agent
        ideas = []
        for i in range(num_ideas):
            idea = IdeaSnapshot(
                id=str(uuid.uuid4()),
                title=f"Idea {i+1} for {topic}",
                description=f"Detailed description for idea {i+1}",
                market_analysis=market_analysis,
                feasibility_score=0.7,
                novelty_score=0.8,
                market_signal_score=0.6,
                overall_score=0.7,
                status=IdeaStatus.DRAFT
            )
            ideas.append(idea)
        return ideas
    
    async def _run_critic(
        self,
        idea: IdeaSnapshot,
        market_analysis: Optional[Dict[str, Any]] = None,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run the critic agent."""
        # Mock implementation - would normally call actual agent
        return {
            "strengths": ["Clear value proposition", "Good market fit"],
            "weaknesses": ["High competition", "Complex implementation"],
            "suggestions": ["Simplify MVP", "Focus on niche market"],
            "score": 0.6
        }
    
    async def _run_pm_refiner(
        self,
        idea: IdeaSnapshot,
        critique: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run the PM refiner agent."""
        # Mock implementation - would normally call actual agent
        return {
            "refinements": ["Simplified feature set", "Clearer user journey"],
            "priorities": ["Core functionality first", "User feedback loop"],
            "timeline": "3-6 months MVP",
            "resources": ["2 developers", "1 designer"]
        }
    
    async def _run_synthesizer(
        self,
        idea: IdeaSnapshot,
        market_analysis: Optional[Dict[str, Any]] = None,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run the synthesizer agent."""
        # Mock implementation - would normally call actual agent
        return {
            "final_concept": "Polished idea concept",
            "key_features": ["Feature 1", "Feature 2", "Feature 3"],
            "business_model": "SaaS subscription",
            "go_to_market": "Direct sales + partnerships"
        }
    
    async def _apply_feedback(self, content: str, feedback: str) -> str:
        """Apply feedback to content."""
        # Mock implementation - would normally use LLM
        return f"{content}\n\n[Refined based on feedback: {feedback}]"
    
    async def _recalculate_scores(self, idea: IdeaSnapshot) -> IdeaSnapshot:
        """Recalculate scores for an idea."""
        # Mock implementation - would normally use evaluator service
        idea.overall_score = (idea.feasibility_score + idea.novelty_score + idea.market_signal_score) / 3
        return idea
