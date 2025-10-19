"""
Visual novelty detection service for startup ideas.
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class VisualNoveltyDetector:
    """Service for detecting visual novelty in startup ideas."""
    
    def __init__(self):
        self.embedder = None
        self.retriever = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the visual novelty detector."""
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
            logger.info("Visual novelty detector initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize visual novelty detector: {e}")
            raise
    
    async def detect_visual_novelty(
        self,
        idea: Dict[str, Any],
        reference_images: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Detect visual novelty of a startup idea.
        
        Args:
            idea: Idea to analyze for visual novelty
            reference_images: Optional reference images for comparison
            
        Returns:
            Visual novelty analysis results
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Detecting visual novelty for idea: {idea.get('title', 'Unknown')}")
            
            # Extract visual elements from idea
            visual_elements = self._extract_visual_elements(idea)
            
            if not visual_elements:
                return {
                    "visual_novelty_score": 0.5,
                    "visual_elements": [],
                    "analysis": "No visual elements found",
                    "visual_metadata": {
                        "idea_id": idea.get("id", "unknown"),
                        "analyzed_at": datetime.utcnow().isoformat(),
                        "detector": "visual_novelty_detector"
                    }
                }
            
            # Generate embeddings for visual elements
            visual_embeddings = await self._generate_visual_embeddings(visual_elements)
            
            # Find similar visual elements
            if reference_images:
                similar_visuals = await self._find_similar_visuals(
                    visual_embeddings, reference_images
                )
            else:
                similar_visuals = await self._search_similar_visuals(visual_embeddings)
            
            # Calculate visual novelty metrics
            visual_novelty_metrics = await self._calculate_visual_novelty_metrics(
                visual_embeddings, similar_visuals
            )
            
            # Analyze visual aspects
            visual_aspects = await self._analyze_visual_aspects(
                visual_elements, similar_visuals
            )
            
            # Generate visual novelty report
            visual_report = await self._generate_visual_novelty_report(
                idea, visual_novelty_metrics, visual_aspects, similar_visuals
            )
            
            results = {
                "visual_novelty_score": visual_novelty_metrics["overall_visual_novelty"],
                "visual_novelty_metrics": visual_novelty_metrics,
                "visual_aspects": visual_aspects,
                "similar_visuals": similar_visuals,
                "visual_report": visual_report,
                "visual_elements": visual_elements,
                "visual_metadata": {
                    "idea_id": idea.get("id", "unknown"),
                    "analyzed_at": datetime.utcnow().isoformat(),
                    "detector": "visual_novelty_detector"
                }
            }
            
            logger.info(f"Visual novelty detection completed: {visual_novelty_metrics['overall_visual_novelty']:.3f}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to detect visual novelty: {e}")
            raise
    
    def _extract_visual_elements(self, idea: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract visual elements from idea."""
        try:
            visual_elements = []
            
            # Extract mockup URL if available
            mockup_url = idea.get("mockup_url")
            if mockup_url:
                visual_elements.append({
                    "type": "mockup",
                    "url": mockup_url,
                    "description": "Generated mockup"
                })
            
            # Extract competitor analysis visuals
            competitor_analysis = idea.get("competitor_analysis", {})
            if competitor_analysis:
                competitor_images = competitor_analysis.get("images", [])
                for img in competitor_images:
                    visual_elements.append({
                        "type": "competitor_image",
                        "url": img.get("url", ""),
                        "description": img.get("description", "Competitor image")
                    })
            
            # Extract visual descriptions from text
            visual_descriptions = self._extract_visual_descriptions(idea)
            for desc in visual_descriptions:
                visual_elements.append({
                    "type": "description",
                    "text": desc,
                    "description": "Visual description"
                })
            
            return visual_elements
            
        except Exception as e:
            logger.error(f"Failed to extract visual elements: {e}")
            return []
    
    def _extract_visual_descriptions(self, idea: Dict[str, Any]) -> List[str]:
        """Extract visual descriptions from idea text."""
        try:
            descriptions = []
            
            # Look for visual keywords in different fields
            visual_keywords = ["design", "interface", "ui", "ux", "mockup", "prototype", "wireframe", "layout"]
            
            fields_to_check = [
                "description", "solution", "key_features", "differentiators"
            ]
            
            for field in fields_to_check:
                content = idea.get(field, "")
                if isinstance(content, str):
                    if any(keyword in content.lower() for keyword in visual_keywords):
                        descriptions.append(content)
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, str) and any(keyword in item.lower() for keyword in visual_keywords):
                            descriptions.append(item)
            
            return descriptions
            
        except Exception as e:
            logger.error(f"Failed to extract visual descriptions: {e}")
            return []
    
    async def _generate_visual_embeddings(
        self,
        visual_elements: List[Dict[str, Any]]
    ) -> List[List[float]]:
        """Generate embeddings for visual elements."""
        try:
            embeddings = []
            
            for element in visual_elements:
                if element["type"] == "mockup" or element["type"] == "competitor_image":
                    # Generate image embedding
                    if element.get("url"):
                        image_embedding = await self.embedder.embed_image([element["url"]])
                        embeddings.append(image_embedding[0])
                    else:
                        # Mock embedding for missing URL
                        embeddings.append([0.1] * settings.IMAGE_EMBEDDING_DIMENSION)
                
                elif element["type"] == "description":
                    # Generate text embedding
                    text_embedding = await self.embedder.embed_text([element["text"]])
                    embeddings.append(text_embedding[0])
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate visual embeddings: {e}")
            return []
    
    async def _find_similar_visuals(
        self,
        visual_embeddings: List[List[float]],
        reference_images: List[str]
    ) -> List[Dict[str, Any]]:
        """Find similar visuals from reference set."""
        try:
            similar_visuals = []
            
            for embedding in visual_embeddings:
                # Generate embeddings for reference images
                ref_embeddings = await self.embedder.embed_image(reference_images)
                
                # Calculate similarities
                for ref_img, ref_embedding in zip(reference_images, ref_embeddings):
                    similarity = self._calculate_cosine_similarity(embedding, ref_embedding)
                    
                    if similarity > 0.3:  # Threshold for similarity
                        similar_visual = {
                            "reference_image": ref_img,
                            "similarity": similarity,
                            "type": "reference_image"
                        }
                        similar_visuals.append(similar_visual)
            
            # Sort by similarity
            similar_visuals.sort(key=lambda x: x["similarity"], reverse=True)
            
            return similar_visuals[:10]  # Top 10 similar visuals
            
        except Exception as e:
            logger.error(f"Failed to find similar visuals: {e}")
            return []
    
    async def _search_similar_visuals(
        self,
        visual_embeddings: List[List[float]]
    ) -> List[Dict[str, Any]]:
        """Search for similar visuals in vector store."""
        try:
            similar_visuals = []
            
            for embedding in visual_embeddings:
                # Search vector store
                results = await self.retriever.search_similar(
                    query_embedding=embedding,
                    top_k=5
                )
                
                # Format results
                for result in results:
                    similar_visual = {
                        "reference_image": result["document"].get("url", ""),
                        "similarity": result["score"],
                        "type": "vector_store_result",
                        "document": result["document"]
                    }
                    similar_visuals.append(similar_visual)
            
            # Sort by similarity
            similar_visuals.sort(key=lambda x: x["similarity"], reverse=True)
            
            return similar_visuals[:10]  # Top 10 similar visuals
            
        except Exception as e:
            logger.error(f"Failed to search similar visuals: {e}")
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
    
    async def _calculate_visual_novelty_metrics(
        self,
        visual_embeddings: List[List[float]],
        similar_visuals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate visual novelty metrics."""
        try:
            if not similar_visuals:
                return {
                    "overall_visual_novelty": 1.0,
                    "visual_similarity_score": 0.0,
                    "visual_uniqueness_score": 1.0,
                    "visual_novelty_threshold": settings.VISUAL_NOVELTY_THRESHOLD
                }
            
            # Calculate similarity scores
            similarities = [visual["similarity"] for visual in similar_visuals]
            
            # Overall visual novelty (inverted similarity)
            max_similarity = max(similarities)
            overall_visual_novelty = 1.0 - max_similarity
            
            # Average similarity
            avg_similarity = np.mean(similarities)
            
            # Visual uniqueness score
            visual_uniqueness_score = 1.0 - avg_similarity
            
            # Visual novelty threshold check
            meets_threshold = overall_visual_novelty >= settings.VISUAL_NOVELTY_THRESHOLD
            
            metrics = {
                "overall_visual_novelty": round(overall_visual_novelty, 3),
                "visual_similarity_score": round(avg_similarity, 3),
                "visual_uniqueness_score": round(visual_uniqueness_score, 3),
                "visual_novelty_threshold": settings.VISUAL_NOVELTY_THRESHOLD,
                "meets_threshold": meets_threshold,
                "similar_visuals_count": len(similar_visuals),
                "max_visual_similarity": round(max_similarity, 3)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate visual novelty metrics: {e}")
            return {
                "overall_visual_novelty": 0.5,
                "visual_similarity_score": 0.5,
                "visual_uniqueness_score": 0.5,
                "visual_novelty_threshold": settings.VISUAL_NOVELTY_THRESHOLD,
                "meets_threshold": False
            }
    
    async def _analyze_visual_aspects(
        self,
        visual_elements: List[Dict[str, Any]],
        similar_visuals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze specific aspects of visual novelty."""
        try:
            aspects = {
                "design_novelty": await self._analyze_design_novelty(visual_elements, similar_visuals),
                "interface_novelty": await self._analyze_interface_novelty(visual_elements, similar_visuals),
                "color_novelty": await self._analyze_color_novelty(visual_elements, similar_visuals),
                "layout_novelty": await self._analyze_layout_novelty(visual_elements, similar_visuals)
            }
            
            return aspects
            
        except Exception as e:
            logger.error(f"Failed to analyze visual aspects: {e}")
            return {}
    
    async def _analyze_design_novelty(
        self,
        visual_elements: List[Dict[str, Any]],
        similar_visuals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze novelty of design elements."""
        try:
            # Look for design-related keywords
            design_keywords = ["modern", "minimalist", "innovative", "unique", "cutting-edge"]
            design_text = " ".join([elem.get("description", "") for elem in visual_elements])
            design_lower = design_text.lower()
            
            design_keyword_count = sum(1 for keyword in design_keywords if keyword in design_lower)
            
            # Calculate novelty based on keywords and similarity
            similarity_score = np.mean([v["similarity"] for v in similar_visuals]) if similar_visuals else 0.0
            design_novelty = (design_keyword_count * 0.2) + (1.0 - similarity_score) * 0.8
            design_novelty = min(design_novelty, 1.0)
            
            return {
                "novelty_score": round(design_novelty, 3),
                "design_keywords_found": design_keyword_count,
                "similarity_score": round(similarity_score, 3),
                "analysis": f"Design novelty: {design_novelty:.1%}"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze design novelty: {e}")
            return {"novelty_score": 0.5, "analysis": "Analysis failed"}
    
    async def _analyze_interface_novelty(
        self,
        visual_elements: List[Dict[str, Any]],
        similar_visuals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze novelty of interface elements."""
        try:
            # Look for interface-related keywords
            interface_keywords = ["intuitive", "user-friendly", "responsive", "adaptive", "gesture-based"]
            interface_text = " ".join([elem.get("description", "") for elem in visual_elements])
            interface_lower = interface_text.lower()
            
            interface_keyword_count = sum(1 for keyword in interface_keywords if keyword in interface_lower)
            
            # Calculate novelty
            similarity_score = np.mean([v["similarity"] for v in similar_visuals]) if similar_visuals else 0.0
            interface_novelty = (interface_keyword_count * 0.2) + (1.0 - similarity_score) * 0.8
            interface_novelty = min(interface_novelty, 1.0)
            
            return {
                "novelty_score": round(interface_novelty, 3),
                "interface_keywords_found": interface_keyword_count,
                "similarity_score": round(similarity_score, 3),
                "analysis": f"Interface novelty: {interface_novelty:.1%}"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze interface novelty: {e}")
            return {"novelty_score": 0.5, "analysis": "Analysis failed"}
    
    async def _analyze_color_novelty(
        self,
        visual_elements: List[Dict[str, Any]],
        similar_visuals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze novelty of color schemes."""
        try:
            # Look for color-related keywords
            color_keywords = ["vibrant", "bold", "contrasting", "monochromatic", "gradient"]
            color_text = " ".join([elem.get("description", "") for elem in visual_elements])
            color_lower = color_text.lower()
            
            color_keyword_count = sum(1 for keyword in color_keywords if keyword in color_lower)
            
            # Calculate novelty
            similarity_score = np.mean([v["similarity"] for v in similar_visuals]) if similar_visuals else 0.0
            color_novelty = (color_keyword_count * 0.2) + (1.0 - similarity_score) * 0.8
            color_novelty = min(color_novelty, 1.0)
            
            return {
                "novelty_score": round(color_novelty, 3),
                "color_keywords_found": color_keyword_count,
                "similarity_score": round(similarity_score, 3),
                "analysis": f"Color novelty: {color_novelty:.1%}"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze color novelty: {e}")
            return {"novelty_score": 0.5, "analysis": "Analysis failed"}
    
    async def _analyze_layout_novelty(
        self,
        visual_elements: List[Dict[str, Any]],
        similar_visuals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze novelty of layout elements."""
        try:
            # Look for layout-related keywords
            layout_keywords = ["grid", "flexible", "modular", "asymmetric", "hierarchical"]
            layout_text = " ".join([elem.get("description", "") for elem in visual_elements])
            layout_lower = layout_text.lower()
            
            layout_keyword_count = sum(1 for keyword in layout_keywords if keyword in layout_lower)
            
            # Calculate novelty
            similarity_score = np.mean([v["similarity"] for v in similar_visuals]) if similar_visuals else 0.0
            layout_novelty = (layout_keyword_count * 0.2) + (1.0 - similarity_score) * 0.8
            layout_novelty = min(layout_novelty, 1.0)
            
            return {
                "novelty_score": round(layout_novelty, 3),
                "layout_keywords_found": layout_keyword_count,
                "similarity_score": round(similarity_score, 3),
                "analysis": f"Layout novelty: {layout_novelty:.1%}"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze layout novelty: {e}")
            return {"novelty_score": 0.5, "analysis": "Analysis failed"}
    
    async def _generate_visual_novelty_report(
        self,
        idea: Dict[str, Any],
        visual_novelty_metrics: Dict[str, Any],
        visual_aspects: Dict[str, Any],
        similar_visuals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive visual novelty report."""
        try:
            # Overall assessment
            overall_visual_novelty = visual_novelty_metrics["overall_visual_novelty"]
            if overall_visual_novelty >= 0.8:
                assessment = "Highly visually novel"
            elif overall_visual_novelty >= 0.6:
                assessment = "Moderately visually novel"
            elif overall_visual_novelty >= 0.4:
                assessment = "Somewhat visually novel"
            else:
                assessment = "Low visual novelty"
            
            # Key insights
            insights = []
            if visual_novelty_metrics["meets_threshold"]:
                insights.append("Meets visual novelty threshold")
            else:
                insights.append("Below visual novelty threshold")
            
            if similar_visuals:
                insights.append(f"Found {len(similar_visuals)} similar visuals")
                insights.append(f"Most similar visual: {similar_visuals[0].get('reference_image', 'Unknown')}")
            
            # Recommendations
            recommendations = []
            if overall_visual_novelty < 0.5:
                recommendations.append("Consider more unique visual design elements")
                recommendations.append("Explore innovative color schemes and layouts")
                recommendations.append("Focus on distinctive interface patterns")
            
            # Aspect analysis
            aspect_analysis = {}
            for aspect, data in visual_aspects.items():
                if isinstance(data, dict) and "novelty_score" in data:
                    score = data["novelty_score"]
                    if score >= 0.7:
                        aspect_analysis[aspect] = "High visual novelty"
                    elif score >= 0.4:
                        aspect_analysis[aspect] = "Moderate visual novelty"
                    else:
                        aspect_analysis[aspect] = "Low visual novelty"
            
            report = {
                "overall_assessment": assessment,
                "visual_novelty_score": overall_visual_novelty,
                "key_insights": insights,
                "recommendations": recommendations,
                "aspect_analysis": aspect_analysis,
                "similar_visuals_summary": {
                    "count": len(similar_visuals),
                    "top_similarity": similar_visuals[0]["similarity"] if similar_visuals else 0.0
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate visual novelty report: {e}")
            return {
                "overall_assessment": "Analysis failed",
                "visual_novelty_score": 0.5,
                "key_insights": ["Analysis failed"],
                "recommendations": ["Unable to provide recommendations"],
                "aspect_analysis": {},
                "similar_visuals_summary": {"count": 0, "top_similarity": 0.0}
            }
    
    async def close(self):
        """Close the visual novelty detector."""
        try:
            if self.embedder:
                await self.embedder.close()
            if self.retriever:
                await self.retriever.close()
            
            logger.info("Visual novelty detector closed")
            
        except Exception as e:
            logger.error(f"Error closing visual novelty detector: {e}")
