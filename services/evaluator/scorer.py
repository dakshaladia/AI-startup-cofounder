"""
Composite scoring logic for startup ideas.
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class Scorer:
    """Service for scoring startup ideas using composite metrics."""
    
    def __init__(self):
        self.weights = {
            "market_signal": settings.MARKET_SIGNAL_WEIGHT,
            "feasibility": settings.FEASIBILITY_WEIGHT,
            "novelty": settings.NOVELTY_WEIGHT,
            "critic_severity": settings.CRITIC_SEVERITY_WEIGHT
        }
        self.initialized = False
    
    async def initialize(self):
        """Initialize the scorer."""
        try:
            self.initialized = True
            logger.info("Scorer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize scorer: {e}")
            raise
    
    async def score_idea(
        self,
        idea: Dict[str, Any],
        market_analysis: Optional[Dict[str, Any]] = None,
        critique: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Score a startup idea using composite metrics.
        
        Args:
            idea: Idea to score
            market_analysis: Market analysis results
            critique: Critique results
            
        Returns:
            Scoring results
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Scoring idea: {idea.get('title', 'Unknown')}")
            
            # Calculate individual scores
            market_score = await self._calculate_market_score(idea, market_analysis)
            feasibility_score = await self._calculate_feasibility_score(idea)
            novelty_score = await self._calculate_novelty_score(idea)
            critic_score = await self._calculate_critic_score(critique)
            
            # Calculate weighted overall score
            overall_score = (
                market_score * self.weights["market_signal"] +
                feasibility_score * self.weights["feasibility"] +
                novelty_score * self.weights["novelty"] +
                critic_score * self.weights["critic_severity"]
            )
            
            # Create scoring results
            results = {
                "overall_score": round(overall_score, 2),
                "component_scores": {
                    "market_signal": round(market_score, 2),
                    "feasibility": round(feasibility_score, 2),
                    "novelty": round(novelty_score, 2),
                    "critic_severity": round(critic_score, 2)
                },
                "weights": self.weights,
                "scoring_metadata": {
                    "idea_id": idea.get("id", "unknown"),
                    "scored_at": datetime.utcnow().isoformat(),
                    "scorer": "composite_scorer"
                }
            }
            
            logger.info(f"Idea scored: {overall_score:.2f}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to score idea: {e}")
            raise
    
    async def _calculate_market_score(
        self,
        idea: Dict[str, Any],
        market_analysis: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate market signal score."""
        try:
            if not market_analysis:
                return 0.5  # Default neutral score
            
            # Extract market signals
            market_size = market_analysis.get("market_size", {})
            opportunities = market_analysis.get("opportunities", [])
            trends = market_analysis.get("key_trends", [])
            
            # Calculate score based on market signals
            score = 0.0
            
            # Market size factor
            if market_size.get("growth_rate"):
                growth_rate = market_size["growth_rate"]
                if "high" in growth_rate.lower():
                    score += 0.3
                elif "medium" in growth_rate.lower():
                    score += 0.2
                else:
                    score += 0.1
            
            # Opportunities factor
            if opportunities:
                score += min(len(opportunities) * 0.1, 0.3)
            
            # Trends factor
            if trends:
                score += min(len(trends) * 0.05, 0.2)
            
            # Target market alignment
            target_market = idea.get("target_market", "")
            if target_market and market_analysis.get("target_segments"):
                target_segments = market_analysis["target_segments"]
                if any(segment["segment"].lower() in target_market.lower() 
                      for segment in target_segments):
                    score += 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate market score: {e}")
            return 0.5
    
    async def _calculate_feasibility_score(self, idea: Dict[str, Any]) -> float:
        """Calculate feasibility score."""
        try:
            score = 0.0
            
            # Technology requirements factor
            tech_requirements = idea.get("technology_requirements", [])
            if tech_requirements:
                # Simpler tech stack = higher feasibility
                complexity_score = max(0, 1.0 - len(tech_requirements) * 0.1)
                score += complexity_score * 0.3
            
            # Implementation timeline factor
            timeline = idea.get("implementation_timeline", "")
            if timeline:
                if "3 months" in timeline.lower() or "6 months" in timeline.lower():
                    score += 0.3
                elif "1 year" in timeline.lower():
                    score += 0.2
                else:
                    score += 0.1
            
            # Business model clarity factor
            business_model = idea.get("business_model", "")
            if business_model:
                if len(business_model) > 50:  # Detailed business model
                    score += 0.2
                else:
                    score += 0.1
            
            # Key features factor
            key_features = idea.get("key_features", [])
            if key_features:
                # Moderate number of features = higher feasibility
                feature_count = len(key_features)
                if 3 <= feature_count <= 7:
                    score += 0.2
                elif feature_count < 3:
                    score += 0.1
                else:
                    score += 0.05
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate feasibility score: {e}")
            return 0.5
    
    async def _calculate_novelty_score(self, idea: Dict[str, Any]) -> float:
        """Calculate novelty score."""
        try:
            score = 0.0
            
            # Innovation indicators
            differentiators = idea.get("differentiators", [])
            if differentiators:
                # More unique differentiators = higher novelty
                score += min(len(differentiators) * 0.15, 0.4)
            
            # Technology novelty
            tech_requirements = idea.get("technology_requirements", [])
            novel_tech_keywords = ["ai", "blockchain", "quantum", "ar", "vr", "iot", "ml"]
            novel_tech_count = sum(1 for tech in tech_requirements 
                                 if any(keyword in tech.lower() for keyword in novel_tech_keywords))
            if novel_tech_count > 0:
                score += min(novel_tech_count * 0.1, 0.3)
            
            # Problem uniqueness
            problem = idea.get("problem", "")
            if problem:
                unique_problem_keywords = ["new", "novel", "unique", "innovative", "breakthrough"]
                if any(keyword in problem.lower() for keyword in unique_problem_keywords):
                    score += 0.2
            
            # Solution uniqueness
            solution = idea.get("solution", "")
            if solution:
                unique_solution_keywords = ["revolutionary", "disruptive", "cutting-edge", "pioneering"]
                if any(keyword in solution.lower() for keyword in unique_solution_keywords):
                    score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate novelty score: {e}")
            return 0.5
    
    async def _calculate_critic_score(self, critique: Optional[Dict[str, Any]]) -> float:
        """Calculate critic severity score (inverted - lower severity = higher score)."""
        try:
            if not critique:
                return 0.5  # Default neutral score
            
            # Extract critic scores
            scores = critique.get("scores", {})
            if not scores:
                return 0.5
            
            # Calculate average critic score
            critic_scores = [
                scores.get("overall_score", 0),
                scores.get("feasibility_score", 0),
                scores.get("market_potential_score", 0),
                scores.get("innovation_score", 0),
                scores.get("competitive_advantage_score", 0),
                scores.get("implementation_score", 0)
            ]
            
            # Filter out None values
            valid_scores = [score for score in critic_scores if score is not None]
            
            if valid_scores:
                average_score = sum(valid_scores) / len(valid_scores)
                # Convert to 0-1 scale (assuming critic scores are 0-10)
                return average_score / 10.0
            
            return 0.5
            
        except Exception as e:
            logger.error(f"Failed to calculate critic score: {e}")
            return 0.5
    
    async def compare_ideas(
        self,
        ideas: List[Dict[str, Any]],
        market_analysis: Optional[Dict[str, Any]] = None,
        critiques: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple ideas and rank them.
        
        Args:
            ideas: List of ideas to compare
            market_analysis: Market analysis results
            critiques: List of critique results for each idea
            
        Returns:
            Comparison results with rankings
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Comparing {len(ideas)} ideas")
            
            # Score each idea
            scored_ideas = []
            for i, idea in enumerate(ideas):
                critique = critiques[i] if critiques and i < len(critiques) else None
                score_result = await self.score_idea(idea, market_analysis, critique)
                
                scored_idea = {
                    "idea": idea,
                    "score": score_result["overall_score"],
                    "component_scores": score_result["component_scores"],
                    "ranking": 0  # Will be set after sorting
                }
                scored_ideas.append(scored_idea)
            
            # Sort by overall score
            scored_ideas.sort(key=lambda x: x["score"], reverse=True)
            
            # Assign rankings
            for i, scored_idea in enumerate(scored_ideas):
                scored_idea["ranking"] = i + 1
            
            # Calculate comparison metrics
            comparison_metrics = self._calculate_comparison_metrics(scored_ideas)
            
            results = {
                "ranked_ideas": scored_ideas,
                "comparison_metrics": comparison_metrics,
                "comparison_metadata": {
                    "compared_at": datetime.utcnow().isoformat(),
                    "total_ideas": len(ideas),
                    "scorer": "composite_scorer"
                }
            }
            
            logger.info(f"Comparison completed for {len(ideas)} ideas")
            return results
            
        except Exception as e:
            logger.error(f"Failed to compare ideas: {e}")
            raise
    
    def _calculate_comparison_metrics(self, scored_ideas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comparison metrics."""
        try:
            if not scored_ideas:
                return {}
            
            scores = [idea["score"] for idea in scored_ideas]
            
            metrics = {
                "score_range": {
                    "min": min(scores),
                    "max": max(scores),
                    "range": max(scores) - min(scores)
                },
                "score_distribution": {
                    "mean": np.mean(scores),
                    "median": np.median(scores),
                    "std": np.std(scores)
                },
                "top_performer": {
                    "idea_title": scored_ideas[0]["idea"].get("title", "Unknown"),
                    "score": scored_ideas[0]["score"],
                    "ranking": 1
                },
                "score_gaps": []
            }
            
            # Calculate gaps between consecutive rankings
            for i in range(len(scored_ideas) - 1):
                gap = scored_ideas[i]["score"] - scored_ideas[i + 1]["score"]
                metrics["score_gaps"].append({
                    "from_rank": i + 1,
                    "to_rank": i + 2,
                    "gap": round(gap, 3)
                })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate comparison metrics: {e}")
            return {}
    
    async def get_scoring_weights(self) -> Dict[str, float]:
        """Get current scoring weights."""
        return self.weights.copy()
    
    async def update_scoring_weights(self, new_weights: Dict[str, float]) -> bool:
        """Update scoring weights."""
        try:
            # Validate weights
            total_weight = sum(new_weights.values())
            if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
                raise ValueError(f"Weights must sum to 1.0, got {total_weight}")
            
            # Update weights
            self.weights.update(new_weights)
            
            logger.info(f"Updated scoring weights: {self.weights}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update scoring weights: {e}")
            raise
    
    async def close(self):
        """Close the scorer."""
        logger.info("Scorer closed")
