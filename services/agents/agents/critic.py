"""
Critic agent for evaluating and critiquing startup ideas.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.logger import get_logger

logger = get_logger(__name__)


class Critic:
    """Critic agent for evaluating startup ideas."""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.initialized = False
    
    async def initialize(self):
        """Initialize the critic agent."""
        try:
            # Load prompt templates
            await self._load_prompts()
            self.initialized = True
            logger.info("Critic agent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Critic: {e}")
            raise
    
    async def _load_prompts(self):
        """Load prompt templates."""
        # In a real implementation, this would load from files
        self.system_prompt = """
        You are a Critic specializing in evaluating startup ideas and business concepts.
        Your role is to provide objective, constructive criticism and identify potential issues.
        You should assess feasibility, market viability, competitive positioning, and implementation challenges.
        Be thorough but fair in your evaluation, highlighting both strengths and weaknesses.
        """
        
        self.user_template = """
        Critically evaluate this startup idea:
        
        Idea: {idea}
        
        Market Analysis: {market_analysis}
        
        Please provide a comprehensive critique including:
        1. Strengths and positive aspects
        2. Weaknesses and potential issues
        3. Market viability assessment
        4. Competitive analysis
        5. Implementation challenges
        6. Risk factors
        7. Improvement suggestions
        8. Overall assessment
        """
    
    async def critique_idea(
        self,
        idea: Dict[str, Any],
        market_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Critique a startup idea.
        
        Args:
            idea: Idea to critique
            market_analysis: Market analysis results
            
        Returns:
            Critique results
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Critiquing idea: {idea.get('title', 'Unknown')}")
            
            # Prepare prompt
            prompt = self.user_template.format(
                idea=json.dumps(idea, indent=2),
                market_analysis=json.dumps(market_analysis, indent=2)
            )
            
            # Define output schema
            schema = {
                "type": "object",
                "properties": {
                    "strengths": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "aspect": {"type": "string"},
                                "description": {"type": "string"},
                                "impact": {"type": "string"}
                            }
                        }
                    },
                    "weaknesses": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "issue": {"type": "string"},
                                "description": {"type": "string"},
                                "severity": {"type": "string"},
                                "impact": {"type": "string"}
                            }
                        }
                    },
                    "market_viability": {
                        "type": "object",
                        "properties": {
                            "assessment": {"type": "string"},
                            "market_fit": {"type": "string"},
                            "customer_demand": {"type": "string"},
                            "market_timing": {"type": "string"}
                        }
                    },
                    "competitive_analysis": {
                        "type": "object",
                        "properties": {
                            "competitive_landscape": {"type": "string"},
                            "differentiation": {"type": "string"},
                            "competitive_advantages": {"type": "array", "items": {"type": "string"}},
                            "competitive_threats": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "implementation_challenges": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "challenge": {"type": "string"},
                                "description": {"type": "string"},
                                "severity": {"type": "string"},
                                "mitigation": {"type": "string"}
                            }
                        }
                    },
                    "risk_factors": {
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
                    "improvement_suggestions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "area": {"type": "string"},
                                "suggestion": {"type": "string"},
                                "priority": {"type": "string"},
                                "expected_impact": {"type": "string"}
                            }
                        }
                    },
                    "overall_assessment": {
                        "type": "object",
                        "properties": {
                            "summary": {"type": "string"},
                            "recommendation": {"type": "string"},
                            "confidence_level": {"type": "string"},
                            "next_steps": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "scores": {
                        "type": "object",
                        "properties": {
                            "overall_score": {"type": "number", "minimum": 0, "maximum": 10},
                            "feasibility_score": {"type": "number", "minimum": 0, "maximum": 10},
                            "market_potential_score": {"type": "number", "minimum": 0, "maximum": 10},
                            "innovation_score": {"type": "number", "minimum": 0, "maximum": 10},
                            "competitive_advantage_score": {"type": "number", "minimum": 0, "maximum": 10},
                            "implementation_score": {"type": "number", "minimum": 0, "maximum": 10}
                        }
                    }
                },
                "required": ["strengths", "weaknesses", "market_viability", "competitive_analysis", "overall_assessment", "scores"]
            }
            
            # Generate critique
            result = await self.llm_client.generate_structured(
                prompt=prompt,
                schema=schema,
                system_prompt=self.system_prompt,
                temperature=0.4  # Lower temperature for more consistent evaluation
            )
            
            # Add metadata
            result["critique_metadata"] = {
                "idea": idea,
                "market_analysis": market_analysis,
                "critiqued_at": datetime.utcnow().isoformat(),
                "agent": "critic"
            }
            
            logger.info(f"Critique completed for idea: {idea.get('title', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Critique failed for idea {idea.get('title', 'Unknown')}: {e}")
            raise
    
    async def compare_ideas(
        self,
        ideas: list,
        criteria: list
    ) -> Dict[str, Any]:
        """
        Compare multiple ideas against specific criteria.
        
        Args:
            ideas: List of ideas to compare
            criteria: Comparison criteria
            
        Returns:
            Comparison results
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Comparing {len(ideas)} ideas")
            
            # Prepare comparison prompt
            comparison_prompt = f"""
            Compare these startup ideas against the specified criteria:
            
            Ideas: {json.dumps(ideas, indent=2)}
            
            Criteria: {json.dumps(criteria, indent=2)}
            
            Please provide a detailed comparison including:
            1. Ranking of ideas
            2. Strengths and weaknesses of each
            3. Comparative analysis
            4. Recommendations
            """
            
            # Define output schema
            schema = {
                "type": "object",
                "properties": {
                    "ranking": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "idea_title": {"type": "string"},
                                "rank": {"type": "integer"},
                                "score": {"type": "number"},
                                "reasoning": {"type": "string"}
                            }
                        }
                    },
                    "comparative_analysis": {
                        "type": "object",
                        "properties": {
                            "best_overall": {"type": "string"},
                            "most_innovative": {"type": "string"},
                            "most_feasible": {"type": "string"},
                            "highest_market_potential": {"type": "string"}
                        }
                    },
                    "recommendations": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["ranking", "comparative_analysis", "recommendations"]
            }
            
            # Generate comparison
            result = await self.llm_client.generate_structured(
                prompt=comparison_prompt,
                schema=schema,
                system_prompt=self.system_prompt,
                temperature=0.3
            )
            
            # Add metadata
            result["comparison_metadata"] = {
                "ideas": ideas,
                "criteria": criteria,
                "compared_at": datetime.utcnow().isoformat(),
                "agent": "critic"
            }
            
            logger.info(f"Comparison completed for {len(ideas)} ideas")
            return result
            
        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            "status": "initialized" if self.initialized else "not_initialized",
            "agent_type": "critic",
            "capabilities": [
                "idea_evaluation",
                "critique_generation",
                "comparative_analysis",
                "risk_assessment",
                "improvement_suggestions"
            ]
        }
    
    async def close(self):
        """Close the agent."""
        logger.info("Critic agent closed")
