"""
Market Analyst agent for analyzing market conditions and trends.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.logger import get_logger

logger = get_logger(__name__)


class MarketAnalyst:
    """Market Analyst agent for market analysis."""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.initialized = False
    
    async def initialize(self):
        """Initialize the market analyst agent."""
        try:
            # Load prompt templates
            await self._load_prompts()
            self.initialized = True
            logger.info("Market Analyst agent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Market Analyst: {e}")
            raise
    
    async def _load_prompts(self):
        """Load prompt templates."""
        # In a real implementation, this would load from files
        self.system_prompt = """
        You are a Market Analyst specializing in startup ecosystems and technology trends.
        Your role is to analyze market conditions, identify opportunities, and assess market potential.
        You should provide data-driven insights and market intelligence.
        """
        
        self.user_template = """
        Analyze the market for: {topic}
        
        Constraints: {constraints}
        
        Please provide a comprehensive market analysis including:
        1. Market size and growth potential
        2. Key trends and opportunities
        3. Competitive landscape
        4. Target customer segments
        5. Market barriers and challenges
        6. Regulatory environment
        7. Technology adoption trends
        8. Investment climate
        """
    
    async def analyze_market(
        self,
        topic: str,
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze market conditions for a given topic.
        
        Args:
            topic: Market topic to analyze
            constraints: Analysis constraints
            
        Returns:
            Market analysis results
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Analyzing market for topic: {topic}")
            
            # Prepare prompt
            prompt = self.user_template.format(
                topic=topic,
                constraints=json.dumps(constraints, indent=2)
            )
            
            # Define output schema
            schema = {
                "type": "object",
                "properties": {
                    "market_size": {
                        "type": "object",
                        "properties": {
                            "current_size": {"type": "string"},
                            "growth_rate": {"type": "string"},
                            "projected_size": {"type": "string"}
                        }
                    },
                    "key_trends": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "opportunities": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "competitive_landscape": {
                        "type": "object",
                        "properties": {
                            "major_players": {"type": "array", "items": {"type": "string"}},
                            "competition_level": {"type": "string"},
                            "market_share_distribution": {"type": "string"}
                        }
                    },
                    "target_segments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "segment": {"type": "string"},
                                "size": {"type": "string"},
                                "characteristics": {"type": "string"}
                            }
                        }
                    },
                    "barriers": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "regulatory_environment": {
                        "type": "object",
                        "properties": {
                            "key_regulations": {"type": "array", "items": {"type": "string"}},
                            "compliance_requirements": {"type": "string"},
                            "regulatory_trends": {"type": "string"}
                        }
                    },
                    "technology_adoption": {
                        "type": "object",
                        "properties": {
                            "adoption_rate": {"type": "string"},
                            "key_technologies": {"type": "array", "items": {"type": "string"}},
                            "adoption_barriers": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "investment_climate": {
                        "type": "object",
                        "properties": {
                            "funding_availability": {"type": "string"},
                            "investor_interest": {"type": "string"},
                            "valuation_trends": {"type": "string"},
                            "funding_stages": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "market_score": {
                        "type": "object",
                        "properties": {
                            "overall_score": {"type": "number", "minimum": 0, "maximum": 10},
                            "opportunity_score": {"type": "number", "minimum": 0, "maximum": 10},
                            "competition_score": {"type": "number", "minimum": 0, "maximum": 10},
                            "barrier_score": {"type": "number", "minimum": 0, "maximum": 10}
                        }
                    }
                },
                "required": ["market_size", "key_trends", "opportunities", "competitive_landscape", "target_segments", "market_score"]
            }
            
            # Generate analysis
            result = await self.llm_client.generate_structured(
                prompt=prompt,
                schema=schema,
                system_prompt=self.system_prompt,
                temperature=0.3  # Lower temperature for more consistent analysis
            )
            
            # Add metadata
            result["analysis_metadata"] = {
                "topic": topic,
                "constraints": constraints,
                "analyzed_at": datetime.utcnow().isoformat(),
                "agent": "market_analyst"
            }
            
            logger.info(f"Market analysis completed for topic: {topic}")
            return result
            
        except Exception as e:
            logger.error(f"Market analysis failed for topic {topic}: {e}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            "status": "initialized" if self.initialized else "not_initialized",
            "agent_type": "market_analyst",
            "capabilities": [
                "market_size_analysis",
                "trend_identification",
                "competitive_analysis",
                "opportunity_assessment"
            ]
        }
    
    async def close(self):
        """Close the agent."""
        logger.info("Market Analyst agent closed")
