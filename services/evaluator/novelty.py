"""
Novelty detection service for startup ideas.
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class NoveltyDetector:
    """Service for detecting novelty in startup ideas."""
    
    def __init__(self):
        self.embedder = None
        self.retriever = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the novelty detector."""
        try:
            # Initialize embedder
            from app.services.embeddings.embedder import Embedder
            self.embedder = Embedder()
            await self.embedder.initialize()
            
            # Initialize retriever
            from app.services.embeddings.retriever import Retriever
            self.retriever = Retriever()
            await self.retriever.initialize()
            
            self.initialized = True
            logger.info("Novelty detector initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize novelty detector: {e}")
            raise
    
    async def detect_novelty(
        self,
        idea: Dict[str, Any],
        reference_ideas: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Detect novelty of a startup idea.
        
        Args:
            idea: Idea to analyze for novelty
            reference_ideas: Optional reference ideas for comparison
            
        Returns:
            Novelty analysis results
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Detecting novelty for idea: {idea.get('title', 'Unknown')}")
            
            # Extract idea text for embedding
            idea_text = self._extract_idea_text(idea)
            
            # Generate embedding for the idea
            idea_embedding = await self.embedder.embed_text([idea_text])
            idea_embedding = idea_embedding[0]
            
            # Find similar ideas
            if reference_ideas:
                similar_ideas = await self._find_similar_ideas(idea_embedding, reference_ideas)
            else:
                similar_ideas = await self._search_similar_ideas(idea_embedding)
            
            # Calculate novelty metrics
            novelty_metrics = await self._calculate_novelty_metrics(
                idea_embedding, similar_ideas
            )
            
            # Analyze novelty aspects
            novelty_aspects = await self._analyze_novelty_aspects(idea, similar_ideas)
            
            # Generate novelty report
            novelty_report = await self._generate_novelty_report(
                idea, novelty_metrics, novelty_aspects, similar_ideas
            )
            
            results = {
                "novelty_score": novelty_metrics["overall_novelty"],
                "novelty_metrics": novelty_metrics,
                "novelty_aspects": novelty_aspects,
                "similar_ideas": similar_ideas,
                "novelty_report": novelty_report,
                "novelty_metadata": {
                    "idea_id": idea.get("id", "unknown"),
                    "analyzed_at": datetime.utcnow().isoformat(),
                    "detector": "novelty_detector"
                }
            }
            
            logger.info(f"Novelty detection completed: {novelty_metrics['overall_novelty']:.3f}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to detect novelty: {e}")
            raise
    
    def _extract_idea_text(self, idea: Dict[str, Any]) -> str:
        """Extract text content from idea for embedding."""
        try:
            # Combine key text fields
            text_parts = [
                idea.get("title", ""),
                idea.get("problem", ""),
                idea.get("solution", ""),
                idea.get("target_market", ""),
                idea.get("business_model", ""),
                " ".join(idea.get("key_features", [])),
                " ".join(idea.get("differentiators", [])),
                " ".join(idea.get("technology_requirements", []))
            ]
            
            # Filter out empty parts and join
            idea_text = " ".join(part for part in text_parts if part.strip())
            
            return idea_text
            
        except Exception as e:
            logger.error(f"Failed to extract idea text: {e}")
            return ""
    
    async def _find_similar_ideas(
        self,
        idea_embedding: List[float],
        reference_ideas: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find similar ideas from reference set."""
        try:
            similar_ideas = []
            
            for ref_idea in reference_ideas:
                # Extract text from reference idea
                ref_text = self._extract_idea_text(ref_idea)
                
                # Generate embedding
                ref_embedding = await self.embedder.embed_text([ref_text])
                ref_embedding = ref_embedding[0]
                
                # Calculate similarity
                similarity = self._calculate_cosine_similarity(idea_embedding, ref_embedding)
                
                if similarity > 0.3:  # Threshold for similarity
                    similar_idea = {
                        "idea": ref_idea,
                        "similarity": similarity,
                        "text": ref_text
                    }
                    similar_ideas.append(similar_idea)
            
            # Sort by similarity
            similar_ideas.sort(key=lambda x: x["similarity"], reverse=True)
            
            return similar_ideas[:10]  # Top 10 similar ideas
            
        except Exception as e:
            logger.error(f"Failed to find similar ideas: {e}")
            return []
    
    async def _search_similar_ideas(self, idea_embedding: List[float]) -> List[Dict[str, Any]]:
        """Search for similar ideas in vector store."""
        try:
            # Search vector store
            results = await self.retriever.search_similar(
                query_embedding=idea_embedding,
                top_k=10
            )
            
            # Format results
            similar_ideas = []
            for result in results:
                similar_idea = {
                    "idea": result["document"],
                    "similarity": result["score"],
                    "text": result["document"].get("text", "")
                }
                similar_ideas.append(similar_idea)
            
            return similar_ideas
            
        except Exception as e:
            logger.error(f"Failed to search similar ideas: {e}")
            return []
    
    def _calculate_cosine_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Failed to calculate cosine similarity: {e}")
            return 0.0
    
    async def _calculate_novelty_metrics(
        self,
        idea_embedding: List[float],
        similar_ideas: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate novelty metrics."""
        try:
            if not similar_ideas:
                return {
                    "overall_novelty": 1.0,
                    "similarity_score": 0.0,
                    "uniqueness_score": 1.0,
                    "novelty_threshold": settings.NOVELTY_THRESHOLD
                }
            
            # Calculate similarity scores
            similarities = [idea["similarity"] for idea in similar_ideas]
            
            # Overall novelty (inverted similarity)
            max_similarity = max(similarities)
            overall_novelty = 1.0 - max_similarity
            
            # Average similarity
            avg_similarity = np.mean(similarities)
            
            # Uniqueness score (based on distance from cluster)
            uniqueness_score = 1.0 - avg_similarity
            
            # Novelty threshold check
            meets_threshold = overall_novelty >= settings.NOVELTY_THRESHOLD
            
            metrics = {
                "overall_novelty": round(overall_novelty, 3),
                "similarity_score": round(avg_similarity, 3),
                "uniqueness_score": round(uniqueness_score, 3),
                "novelty_threshold": settings.NOVELTY_THRESHOLD,
                "meets_threshold": meets_threshold,
                "similar_ideas_count": len(similar_ideas),
                "max_similarity": round(max_similarity, 3)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate novelty metrics: {e}")
            return {
                "overall_novelty": 0.5,
                "similarity_score": 0.5,
                "uniqueness_score": 0.5,
                "novelty_threshold": settings.NOVELTY_THRESHOLD,
                "meets_threshold": False
            }
    
    async def _analyze_novelty_aspects(
        self,
        idea: Dict[str, Any],
        similar_ideas: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze specific aspects of novelty."""
        try:
            aspects = {
                "problem_novelty": await self._analyze_problem_novelty(idea, similar_ideas),
                "solution_novelty": await self._analyze_solution_novelty(idea, similar_ideas),
                "market_novelty": await self._analyze_market_novelty(idea, similar_ideas),
                "technology_novelty": await self._analyze_technology_novelty(idea, similar_ideas),
                "business_model_novelty": await self._analyze_business_model_novelty(idea, similar_ideas)
            }
            
            return aspects
            
        except Exception as e:
            logger.error(f"Failed to analyze novelty aspects: {e}")
            return {}
    
    async def _analyze_problem_novelty(
        self,
        idea: Dict[str, Any],
        similar_ideas: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze novelty of the problem statement."""
        try:
            problem = idea.get("problem", "")
            if not problem:
                return {"novelty_score": 0.5, "analysis": "No problem statement provided"}
            
            # Check for unique problem keywords
            unique_keywords = ["unprecedented", "unmet", "emerging", "new", "novel", "unique"]
            problem_lower = problem.lower()
            unique_count = sum(1 for keyword in unique_keywords if keyword in problem_lower)
            
            # Analyze against similar ideas
            similar_problems = [idea["idea"].get("problem", "") for idea in similar_ideas]
            problem_similarity = self._calculate_text_similarity(problem, similar_problems)
            
            novelty_score = (unique_count * 0.2) + (1.0 - problem_similarity) * 0.8
            novelty_score = min(novelty_score, 1.0)
            
            return {
                "novelty_score": round(novelty_score, 3),
                "unique_keywords_found": unique_count,
                "problem_similarity": round(problem_similarity, 3),
                "analysis": f"Problem novelty: {novelty_score:.1%}"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze problem novelty: {e}")
            return {"novelty_score": 0.5, "analysis": "Analysis failed"}
    
    async def _analyze_solution_novelty(
        self,
        idea: Dict[str, Any],
        similar_ideas: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze novelty of the solution."""
        try:
            solution = idea.get("solution", "")
            if not solution:
                return {"novelty_score": 0.5, "analysis": "No solution provided"}
            
            # Check for innovative solution keywords
            innovative_keywords = ["revolutionary", "disruptive", "breakthrough", "cutting-edge", "pioneering"]
            solution_lower = solution.lower()
            innovative_count = sum(1 for keyword in innovative_keywords if keyword in solution_lower)
            
            # Analyze against similar ideas
            similar_solutions = [idea["idea"].get("solution", "") for idea in similar_ideas]
            solution_similarity = self._calculate_text_similarity(solution, similar_solutions)
            
            novelty_score = (innovative_count * 0.2) + (1.0 - solution_similarity) * 0.8
            novelty_score = min(novelty_score, 1.0)
            
            return {
                "novelty_score": round(novelty_score, 3),
                "innovative_keywords_found": innovative_count,
                "solution_similarity": round(solution_similarity, 3),
                "analysis": f"Solution novelty: {novelty_score:.1%}"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze solution novelty: {e}")
            return {"novelty_score": 0.5, "analysis": "Analysis failed"}
    
    async def _analyze_market_novelty(
        self,
        idea: Dict[str, Any],
        similar_ideas: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze novelty of the target market."""
        try:
            target_market = idea.get("target_market", "")
            if not target_market:
                return {"novelty_score": 0.5, "analysis": "No target market specified"}
            
            # Check for emerging market keywords
            emerging_keywords = ["emerging", "untapped", "new", "growing", "developing"]
            market_lower = target_market.lower()
            emerging_count = sum(1 for keyword in emerging_keywords if keyword in market_lower)
            
            # Analyze against similar ideas
            similar_markets = [idea["idea"].get("target_market", "") for idea in similar_ideas]
            market_similarity = self._calculate_text_similarity(target_market, similar_markets)
            
            novelty_score = (emerging_count * 0.2) + (1.0 - market_similarity) * 0.8
            novelty_score = min(novelty_score, 1.0)
            
            return {
                "novelty_score": round(novelty_score, 3),
                "emerging_keywords_found": emerging_count,
                "market_similarity": round(market_similarity, 3),
                "analysis": f"Market novelty: {novelty_score:.1%}"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze market novelty: {e}")
            return {"novelty_score": 0.5, "analysis": "Analysis failed"}
    
    async def _analyze_technology_novelty(
        self,
        idea: Dict[str, Any],
        similar_ideas: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze novelty of the technology stack."""
        try:
            tech_requirements = idea.get("technology_requirements", [])
            if not tech_requirements:
                return {"novelty_score": 0.5, "analysis": "No technology requirements specified"}
            
            # Check for cutting-edge technologies
            cutting_edge_tech = ["ai", "blockchain", "quantum", "ar", "vr", "iot", "ml", "deep learning"]
            tech_lower = " ".join(tech_requirements).lower()
            cutting_edge_count = sum(1 for tech in cutting_edge_tech if tech in tech_lower)
            
            # Analyze against similar ideas
            similar_tech = []
            for idea_data in similar_ideas:
                similar_tech.extend(idea_data["idea"].get("technology_requirements", []))
            
            tech_similarity = self._calculate_text_similarity(
                " ".join(tech_requirements), similar_tech
            )
            
            novelty_score = (cutting_edge_count * 0.2) + (1.0 - tech_similarity) * 0.8
            novelty_score = min(novelty_score, 1.0)
            
            return {
                "novelty_score": round(novelty_score, 3),
                "cutting_edge_technologies": cutting_edge_count,
                "technology_similarity": round(tech_similarity, 3),
                "analysis": f"Technology novelty: {novelty_score:.1%}"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze technology novelty: {e}")
            return {"novelty_score": 0.5, "analysis": "Analysis failed"}
    
    async def _analyze_business_model_novelty(
        self,
        idea: Dict[str, Any],
        similar_ideas: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze novelty of the business model."""
        try:
            business_model = idea.get("business_model", "")
            if not business_model:
                return {"novelty_score": 0.5, "analysis": "No business model specified"}
            
            # Check for innovative business model keywords
            innovative_keywords = ["subscription", "freemium", "marketplace", "platform", "saas", "p2p"]
            model_lower = business_model.lower()
            innovative_count = sum(1 for keyword in innovative_keywords if keyword in model_lower)
            
            # Analyze against similar ideas
            similar_models = [idea["idea"].get("business_model", "") for idea in similar_ideas]
            model_similarity = self._calculate_text_similarity(business_model, similar_models)
            
            novelty_score = (innovative_count * 0.2) + (1.0 - model_similarity) * 0.8
            novelty_score = min(novelty_score, 1.0)
            
            return {
                "novelty_score": round(novelty_score, 3),
                "innovative_keywords_found": innovative_count,
                "model_similarity": round(model_similarity, 3),
                "analysis": f"Business model novelty: {novelty_score:.1%}"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze business model novelty: {e}")
            return {"novelty_score": 0.5, "analysis": "Analysis failed"}
    
    def _calculate_text_similarity(self, text: str, similar_texts: List[str]) -> float:
        """Calculate text similarity using simple word overlap."""
        try:
            if not similar_texts:
                return 0.0
            
            # Simple word-based similarity
            text_words = set(text.lower().split())
            similarities = []
            
            for similar_text in similar_texts:
                similar_words = set(similar_text.lower().split())
                if text_words and similar_words:
                    overlap = len(text_words.intersection(similar_words))
                    union = len(text_words.union(similar_words))
                    similarity = overlap / union if union > 0 else 0.0
                    similarities.append(similarity)
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate text similarity: {e}")
            return 0.0
    
    async def _generate_novelty_report(
        self,
        idea: Dict[str, Any],
        novelty_metrics: Dict[str, Any],
        novelty_aspects: Dict[str, Any],
        similar_ideas: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive novelty report."""
        try:
            # Overall assessment
            overall_novelty = novelty_metrics["overall_novelty"]
            if overall_novelty >= 0.8:
                assessment = "Highly novel"
            elif overall_novelty >= 0.6:
                assessment = "Moderately novel"
            elif overall_novelty >= 0.4:
                assessment = "Somewhat novel"
            else:
                assessment = "Low novelty"
            
            # Key insights
            insights = []
            if novelty_metrics["meets_threshold"]:
                insights.append("Meets novelty threshold")
            else:
                insights.append("Below novelty threshold")
            
            if similar_ideas:
                insights.append(f"Found {len(similar_ideas)} similar ideas")
                insights.append(f"Most similar idea: {similar_ideas[0]['idea'].get('title', 'Unknown')}")
            
            # Recommendations
            recommendations = []
            if overall_novelty < 0.5:
                recommendations.append("Consider adding more unique differentiators")
                recommendations.append("Explore emerging technologies or markets")
                recommendations.append("Focus on solving problems in new ways")
            
            # Aspect analysis
            aspect_analysis = {}
            for aspect, data in novelty_aspects.items():
                if isinstance(data, dict) and "novelty_score" in data:
                    score = data["novelty_score"]
                    if score >= 0.7:
                        aspect_analysis[aspect] = "High novelty"
                    elif score >= 0.4:
                        aspect_analysis[aspect] = "Moderate novelty"
                    else:
                        aspect_analysis[aspect] = "Low novelty"
            
            report = {
                "overall_assessment": assessment,
                "novelty_score": overall_novelty,
                "key_insights": insights,
                "recommendations": recommendations,
                "aspect_analysis": aspect_analysis,
                "similar_ideas_summary": {
                    "count": len(similar_ideas),
                    "top_similarity": similar_ideas[0]["similarity"] if similar_ideas else 0.0
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate novelty report: {e}")
            return {
                "overall_assessment": "Analysis failed",
                "novelty_score": 0.5,
                "key_insights": ["Analysis failed"],
                "recommendations": ["Unable to provide recommendations"],
                "aspect_analysis": {},
                "similar_ideas_summary": {"count": 0, "top_similarity": 0.0}
            }
    
    async def close(self):
        """Close the novelty detector."""
        try:
            if self.embedder:
                await self.embedder.close()
            if self.retriever:
                await self.retriever.close()
            
            logger.info("Novelty detector closed")
            
        except Exception as e:
            logger.error(f"Error closing novelty detector: {e}")
