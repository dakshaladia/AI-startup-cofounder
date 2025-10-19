"""
Idea Generator agent for creating startup ideas.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.logger import get_logger

logger = get_logger(__name__)


class IdeaGenerator:
    """Idea Generator agent for creating startup ideas."""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.initialized = False
    
    async def initialize(self):
        """Initialize the idea generator agent."""
        try:
            # Load prompt templates
            await self._load_prompts()
            self.initialized = True
            logger.info("Idea Generator agent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Idea Generator: {e}")
            raise
    
    async def _load_prompts(self):
        """Load prompt templates."""
        # In a real implementation, this would load from files
        self.system_prompt = """
        You are an Idea Generator specializing in creating innovative startup ideas.
        Your role is to generate creative, feasible, and market-relevant startup concepts.
        You should consider market opportunities, technology trends, and user needs.
        Focus on ideas that are innovative, scalable, and have clear value propositions.
        """
        
        self.user_template = """
        Generate {num_ideas} startup ideas for: {topic}
        
        Market Analysis: {market_analysis}
        Constraints: {constraints}
        
        For each idea, provide:
        1. A compelling title and tagline
        2. Clear problem statement
        3. Solution description
        4. Target market and customers
        5. Business model
        6. Key features and differentiators
        7. Technology requirements
        8. Go-to-market strategy
        9. Revenue potential
        10. Implementation timeline
        """
    
    async def generate_ideas(
        self,
        topic: str,
        constraints: Dict[str, Any],
        market_analysis: Dict[str, Any],
        num_ideas: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate startup ideas for a given topic.
        
        Args:
            topic: Topic for idea generation
            constraints: Generation constraints
            market_analysis: Market analysis results
            num_ideas: Number of ideas to generate
            
        Returns:
            List of generated ideas
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Generating {num_ideas} ideas for topic: {topic}")
            
            # Prepare prompt
            prompt = self.user_template.format(
                num_ideas=num_ideas,
                topic=topic,
                market_analysis=json.dumps(market_analysis, indent=2),
                constraints=json.dumps(constraints, indent=2)
            )
            
            # Define output schema
            schema = {
                "type": "object",
                "properties": {
                    "ideas": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "tagline": {"type": "string"},
                                "problem": {"type": "string"},
                                "solution": {"type": "string"},
                                "target_market": {"type": "string"},
                                "target_customers": {"type": "string"},
                                "business_model": {"type": "string"},
                                "key_features": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "differentiators": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "technology_requirements": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "go_to_market": {"type": "string"},
                                "revenue_potential": {"type": "string"},
                                "implementation_timeline": {"type": "string"},
                                "feasibility_score": {"type": "number", "minimum": 0, "maximum": 10},
                                "innovation_score": {"type": "number", "minimum": 0, "maximum": 10},
                                "market_potential_score": {"type": "number", "minimum": 0, "maximum": 10}
                            },
                            "required": ["title", "problem", "solution", "target_market", "business_model"]
                        }
                    }
                },
                "required": ["ideas"]
            }
            
            # Generate ideas
            result = await self.llm_client.generate_structured(
                prompt=prompt,
                schema=schema,
                system_prompt=self.system_prompt,
                temperature=0.8  # Higher temperature for more creative ideas
            )
            
            # Add metadata to each idea
            for idea in result["ideas"]:
                idea["generation_metadata"] = {
                    "topic": topic,
                    "constraints": constraints,
                    "generated_at": datetime.utcnow().isoformat(),
                    "agent": "idea_generator"
                }
            
            logger.info(f"Generated {len(result['ideas'])} ideas for topic: {topic}")
            return result["ideas"]
            
        except Exception as e:
            logger.error(f"Idea generation failed for topic {topic}: {e}")
            raise
    
    async def refine_idea(
        self,
        idea: Dict[str, Any],
        feedback: str,
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Refine an existing idea based on feedback.
        
        Args:
            idea: Original idea to refine
            feedback: Feedback for refinement
            constraints: Refinement constraints
            
        Returns:
            Refined idea
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Refining idea: {idea.get('title', 'Unknown')}")
            
            # Prepare refinement prompt
            refinement_prompt = f"""
            Refine this startup idea based on the feedback provided:
            
            Original Idea: {json.dumps(idea, indent=2)}
            
            Feedback: {feedback}
            
            Constraints: {json.dumps(constraints, indent=2)}
            
            Please provide a refined version of the idea that addresses the feedback
            while maintaining the core concept and improving upon the identified issues.
            """
            
            # Define output schema (same as idea generation)
            schema = {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "tagline": {"type": "string"},
                    "problem": {"type": "string"},
                    "solution": {"type": "string"},
                    "target_market": {"type": "string"},
                    "target_customers": {"type": "string"},
                    "business_model": {"type": "string"},
                    "key_features": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "differentiators": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "technology_requirements": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "go_to_market": {"type": "string"},
                    "revenue_potential": {"type": "string"},
                    "implementation_timeline": {"type": "string"},
                    "feasibility_score": {"type": "number", "minimum": 0, "maximum": 10},
                    "innovation_score": {"type": "number", "minimum": 0, "maximum": 10},
                    "market_potential_score": {"type": "number", "minimum": 0, "maximum": 10},
                    "refinement_notes": {"type": "string"}
                },
                "required": ["title", "problem", "solution", "target_market", "business_model"]
            }
            
            # Generate refined idea
            refined_idea = await self.llm_client.generate_structured(
                prompt=refinement_prompt,
                schema=schema,
                system_prompt=self.system_prompt,
                temperature=0.6  # Moderate temperature for refinement
            )
            
            # Add refinement metadata
            refined_idea["refinement_metadata"] = {
                "original_idea": idea,
                "feedback": feedback,
                "constraints": constraints,
                "refined_at": datetime.utcnow().isoformat(),
                "agent": "idea_generator"
            }
            
            logger.info(f"Idea refinement completed: {refined_idea.get('title', 'Unknown')}")
            return refined_idea
            
        except Exception as e:
            logger.error(f"Idea refinement failed: {e}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            "status": "initialized" if self.initialized else "not_initialized",
            "agent_type": "idea_generator",
            "capabilities": [
                "idea_generation",
                "idea_refinement",
                "creative_problem_solving",
                "market_opportunity_identification"
            ]
        }
    
    async def close(self):
        """Close the agent."""
        logger.info("Idea Generator agent closed")
