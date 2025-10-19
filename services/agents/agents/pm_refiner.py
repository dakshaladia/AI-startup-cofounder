"""
PM Refiner agent for refining startup ideas based on feedback.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.logger import get_logger

logger = get_logger(__name__)


class PMRefiner:
    """PM Refiner agent for refining startup ideas."""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.initialized = False
    
    async def initialize(self):
        """Initialize the PM refiner agent."""
        try:
            # Load prompt templates
            await self._load_prompts()
            self.initialized = True
            logger.info("PM Refiner agent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PM Refiner: {e}")
            raise
    
    async def _load_prompts(self):
        """Load prompt templates."""
        # In a real implementation, this would load from files
        self.system_prompt = """
        You are a PM Refiner specializing in refining startup ideas and business concepts.
        Your role is to take feedback and critiques to improve ideas, making them more viable,
        market-ready, and implementable. You should focus on practical improvements while
        maintaining the core vision and value proposition.
        """
        
        self.user_template = """
        Refine this startup idea based on the critique and feedback:
        
        Original Idea: {idea}
        
        Critique: {critique}
        
        Constraints: {constraints}
        
        Please provide a refined version that addresses the identified issues while
        maintaining the core concept and improving upon the weaknesses.
        """
    
    async def refine_idea(
        self,
        idea: Dict[str, Any],
        critique: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Refine a startup idea based on critique and constraints.
        
        Args:
            idea: Original idea to refine
            critique: Critique results
            constraints: Refinement constraints
            
        Returns:
            Refined idea
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Refining idea: {idea.get('title', 'Unknown')}")
            
            # Prepare prompt
            prompt = self.user_template.format(
                idea=json.dumps(idea, indent=2),
                critique=json.dumps(critique, indent=2),
                constraints=json.dumps(constraints, indent=2)
            )
            
            # Define output schema
            schema = {
                "type": "object",
                "properties": {
                    "refined_idea": {
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
                            "implementation_timeline": {"type": "string"}
                        },
                        "required": ["title", "problem", "solution", "target_market", "business_model"]
                    },
                    "refinements_made": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "area": {"type": "string"},
                                "original": {"type": "string"},
                                "refined": {"type": "string"},
                                "reasoning": {"type": "string"}
                            }
                        }
                    },
                    "addressed_issues": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "issue": {"type": "string"},
                                "solution": {"type": "string"},
                                "impact": {"type": "string"}
                            }
                        }
                    },
                    "improvement_summary": {
                        "type": "object",
                        "properties": {
                            "key_improvements": {"type": "array", "items": {"type": "string"}},
                            "maintained_aspects": {"type": "array", "items": {"type": "string"}},
                            "new_considerations": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "refined_scores": {
                        "type": "object",
                        "properties": {
                            "feasibility_score": {"type": "number", "minimum": 0, "maximum": 10},
                            "innovation_score": {"type": "number", "minimum": 0, "maximum": 10},
                            "market_potential_score": {"type": "number", "minimum": 0, "maximum": 10},
                            "overall_score": {"type": "number", "minimum": 0, "maximum": 10}
                        }
                    }
                },
                "required": ["refined_idea", "refinements_made", "addressed_issues", "improvement_summary", "refined_scores"]
            }
            
            # Generate refined idea
            result = await self.llm_client.generate_structured(
                prompt=prompt,
                schema=schema,
                system_prompt=self.system_prompt,
                temperature=0.6  # Moderate temperature for refinement
            )
            
            # Add metadata
            result["refinement_metadata"] = {
                "original_idea": idea,
                "critique": critique,
                "constraints": constraints,
                "refined_at": datetime.utcnow().isoformat(),
                "agent": "pm_refiner"
            }
            
            logger.info(f"Idea refinement completed: {result['refined_idea'].get('title', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Idea refinement failed: {e}")
            raise
    
    async def prioritize_features(
        self,
        idea: Dict[str, Any],
        features: list,
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prioritize features for an idea based on constraints and market needs.
        
        Args:
            idea: Idea to prioritize features for
            features: List of features to prioritize
            constraints: Prioritization constraints
            
        Returns:
            Feature prioritization results
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Prioritizing features for idea: {idea.get('title', 'Unknown')}")
            
            # Prepare prioritization prompt
            prioritization_prompt = f"""
            Prioritize these features for the startup idea based on constraints and market needs:
            
            Idea: {json.dumps(idea, indent=2)}
            
            Features: {json.dumps(features, indent=2)}
            
            Constraints: {json.dumps(constraints, indent=2)}
            
            Please provide a prioritized list with reasoning for each feature's priority level.
            """
            
            # Define output schema
            schema = {
                "type": "object",
                "properties": {
                    "prioritized_features": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "feature": {"type": "string"},
                                "priority": {"type": "string"},
                                "reasoning": {"type": "string"},
                                "implementation_effort": {"type": "string"},
                                "market_impact": {"type": "string"},
                                "dependencies": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    },
                    "implementation_phases": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "phase": {"type": "string"},
                                "features": {"type": "array", "items": {"type": "string"}},
                                "timeline": {"type": "string"},
                                "goals": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    },
                    "recommendations": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["prioritized_features", "implementation_phases", "recommendations"]
            }
            
            # Generate prioritization
            result = await self.llm_client.generate_structured(
                prompt=prioritization_prompt,
                schema=schema,
                system_prompt=self.system_prompt,
                temperature=0.5
            )
            
            # Add metadata
            result["prioritization_metadata"] = {
                "idea": idea,
                "features": features,
                "constraints": constraints,
                "prioritized_at": datetime.utcnow().isoformat(),
                "agent": "pm_refiner"
            }
            
            logger.info(f"Feature prioritization completed for idea: {idea.get('title', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Feature prioritization failed: {e}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            "status": "initialized" if self.initialized else "not_initialized",
            "agent_type": "pm_refiner",
            "capabilities": [
                "idea_refinement",
                "feature_prioritization",
                "implementation_planning",
                "constraint_optimization",
                "practical_improvements"
            ]
        }
    
    async def close(self):
        """Close the agent."""
        logger.info("PM Refiner agent closed")
