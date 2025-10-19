"""
Synthesizer agent for creating final polished startup ideas.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.logger import get_logger

logger = get_logger(__name__)


class Synthesizer:
    """Synthesizer agent for creating final polished startup ideas."""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.initialized = False
    
    async def initialize(self):
        """Initialize the synthesizer agent."""
        try:
            # Load prompt templates
            await self._load_prompts()
            self.initialized = True
            logger.info("Synthesizer agent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Synthesizer: {e}")
            raise
    
    async def _load_prompts(self):
        """Load prompt templates."""
        # In a real implementation, this would load from files
        self.system_prompt = """
        You are a Synthesizer specializing in creating final, polished startup ideas.
        Your role is to take refined ideas and create comprehensive, market-ready concepts
        that are well-structured, compelling, and ready for presentation to stakeholders.
        You should synthesize all the analysis, feedback, and refinements into a cohesive,
        professional startup concept.
        """
        
        self.user_template = """
        Synthesize this refined startup idea into a final, polished concept:
        
        Refined Idea: {refined_idea}
        
        Market Analysis: {market_analysis}
        
        Please create a comprehensive, market-ready startup concept that synthesizes
        all the analysis and refinements into a cohesive, compelling presentation.
        """
    
    async def synthesize_idea(
        self,
        refined_idea: Dict[str, Any],
        market_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize a refined idea into a final, polished concept.
        
        Args:
            refined_idea: Refined idea to synthesize
            market_analysis: Market analysis results
            
        Returns:
            Final synthesized idea
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Synthesizing idea: {refined_idea.get('title', 'Unknown')}")
            
            # Prepare prompt
            prompt = self.user_template.format(
                refined_idea=json.dumps(refined_idea, indent=2),
                market_analysis=json.dumps(market_analysis, indent=2)
            )
            
            # Define output schema
            schema = {
                "type": "object",
                "properties": {
                    "final_concept": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "tagline": {"type": "string"},
                            "executive_summary": {"type": "string"},
                            "problem_statement": {"type": "string"},
                            "solution_description": {"type": "string"},
                            "target_market": {"type": "string"},
                            "target_customers": {"type": "string"},
                            "business_model": {"type": "string"},
                            "value_proposition": {"type": "string"},
                            "key_features": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "differentiators": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "technology_stack": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "go_to_market_strategy": {"type": "string"},
                            "revenue_model": {"type": "string"},
                            "implementation_timeline": {"type": "string"},
                            "success_metrics": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["title", "executive_summary", "problem_statement", "solution_description", "target_market", "business_model"]
                    },
                    "market_positioning": {
                        "type": "object",
                        "properties": {
                            "market_opportunity": {"type": "string"},
                            "competitive_advantage": {"type": "string"},
                            "market_entry_strategy": {"type": "string"},
                            "scaling_plan": {"type": "string"}
                        }
                    },
                    "implementation_roadmap": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "phase": {"type": "string"},
                                "duration": {"type": "string"},
                                "key_milestones": {"type": "array", "items": {"type": "string"}},
                                "deliverables": {"type": "array", "items": {"type": "string"}},
                                "success_criteria": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    },
                    "risk_assessment": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "risk": {"type": "string"},
                                "description": {"type": "string"},
                                "probability": {"type": "string"},
                                "impact": {"type": "string"},
                                "mitigation": {"type": "string"}
                            }
                        }
                    },
                    "investment_requirements": {
                        "type": "object",
                        "properties": {
                            "funding_needed": {"type": "string"},
                            "funding_use": {"type": "string"},
                            "funding_timeline": {"type": "string"},
                            "expected_returns": {"type": "string"}
                        }
                    },
                    "final_scores": {
                        "type": "object",
                        "properties": {
                            "overall_score": {"type": "number", "minimum": 0, "maximum": 10},
                            "feasibility_score": {"type": "number", "minimum": 0, "maximum": 10},
                            "innovation_score": {"type": "number", "minimum": 0, "maximum": 10},
                            "market_potential_score": {"type": "number", "minimum": 0, "maximum": 10},
                            "competitive_advantage_score": {"type": "number", "minimum": 0, "maximum": 10},
                            "implementation_score": {"type": "number", "minimum": 0, "maximum": 10}
                        }
                    },
                    "presentation_ready": {
                        "type": "object",
                        "properties": {
                            "elevator_pitch": {"type": "string"},
                            "key_selling_points": {"type": "array", "items": {"type": "string"}},
                            "demo_script": {"type": "string"},
                            "presentation_outline": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                },
                "required": ["final_concept", "market_positioning", "implementation_roadmap", "final_scores", "presentation_ready"]
            }
            
            # Generate synthesized idea
            result = await self.llm_client.generate_structured(
                prompt=prompt,
                schema=schema,
                system_prompt=self.system_prompt,
                temperature=0.5  # Moderate temperature for synthesis
            )
            
            # Add metadata
            result["synthesis_metadata"] = {
                "refined_idea": refined_idea,
                "market_analysis": market_analysis,
                "synthesized_at": datetime.utcnow().isoformat(),
                "agent": "synthesizer"
            }
            
            logger.info(f"Idea synthesis completed: {result['final_concept'].get('title', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Idea synthesis failed: {e}")
            raise
    
    async def create_presentation(
        self,
        synthesized_idea: Dict[str, Any],
        presentation_type: str = "investor_pitch"
    ) -> Dict[str, Any]:
        """
        Create a presentation for the synthesized idea.
        
        Args:
            synthesized_idea: Synthesized idea to present
            presentation_type: Type of presentation (investor_pitch, team_briefing, etc.)
            
        Returns:
            Presentation content
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Creating {presentation_type} presentation")
            
            # Prepare presentation prompt
            presentation_prompt = f"""
            Create a {presentation_type} presentation for this synthesized startup idea:
            
            Synthesized Idea: {json.dumps(synthesized_idea, indent=2)}
            
            Please create a comprehensive presentation that effectively communicates
            the startup concept to the target audience.
            """
            
            # Define output schema
            schema = {
                "type": "object",
                "properties": {
                    "presentation": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "subtitle": {"type": "string"},
                            "slides": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "slide_number": {"type": "integer"},
                                        "title": {"type": "string"},
                                        "content": {"type": "string"},
                                        "key_points": {"type": "array", "items": {"type": "string"}},
                                        "visual_suggestions": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "presentation_notes": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "delivery_guidelines": {
                        "type": "object",
                        "properties": {
                            "duration": {"type": "string"},
                            "key_messages": {"type": "array", "items": {"type": "string"}},
                            "audience_considerations": {"type": "string"},
                            "q_and_a_preparation": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                },
                "required": ["presentation", "presentation_notes", "delivery_guidelines"]
            }
            
            # Generate presentation
            result = await self.llm_client.generate_structured(
                prompt=presentation_prompt,
                schema=schema,
                system_prompt=self.system_prompt,
                temperature=0.6
            )
            
            # Add metadata
            result["presentation_metadata"] = {
                "synthesized_idea": synthesized_idea,
                "presentation_type": presentation_type,
                "created_at": datetime.utcnow().isoformat(),
                "agent": "synthesizer"
            }
            
            logger.info(f"Presentation created: {presentation_type}")
            return result
            
        except Exception as e:
            logger.error(f"Presentation creation failed: {e}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            "status": "initialized" if self.initialized else "not_initialized",
            "agent_type": "synthesizer",
            "capabilities": [
                "idea_synthesis",
                "presentation_creation",
                "market_positioning",
                "implementation_planning",
                "stakeholder_communication"
            ]
        }
    
    async def close(self):
        """Close the agent."""
        logger.info("Synthesizer agent closed")
