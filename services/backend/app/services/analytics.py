"""
Analytics service for tracking metrics and generating insights.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

from app.core.logger import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    """Service for analytics and metrics tracking."""
    
    def __init__(self):
        self.metrics = {}
        self.events = []
    
    async def track_idea_generation(self, topic: str, num_ideas: int):
        """Track idea generation event."""
        try:
            event = {
                "event_type": "idea_generation",
                "topic": topic,
                "num_ideas": num_ideas,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.events.append(event)
            
            # Update metrics
            if "idea_generation" not in self.metrics:
                self.metrics["idea_generation"] = {
                    "total_generations": 0,
                    "total_ideas": 0,
                    "topics": {}
                }
            
            self.metrics["idea_generation"]["total_generations"] += 1
            self.metrics["idea_generation"]["total_ideas"] += num_ideas
            
            if topic not in self.metrics["idea_generation"]["topics"]:
                self.metrics["idea_generation"]["topics"][topic] = 0
            self.metrics["idea_generation"]["topics"][topic] += 1
            
            logger.info(f"Tracked idea generation: {topic}, {num_ideas} ideas")
            
        except Exception as e:
            logger.error(f"Failed to track idea generation: {e}")
    
    async def track_idea_iteration(self, idea_id: str, iteration_type: str):
        """Track idea iteration event."""
        try:
            event = {
                "event_type": "idea_iteration",
                "idea_id": idea_id,
                "iteration_type": iteration_type,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.events.append(event)
            
            # Update metrics
            if "idea_iteration" not in self.metrics:
                self.metrics["idea_iteration"] = {
                    "total_iterations": 0,
                    "by_type": {}
                }
            
            self.metrics["idea_iteration"]["total_iterations"] += 1
            
            if iteration_type not in self.metrics["idea_iteration"]["by_type"]:
                self.metrics["idea_iteration"]["by_type"][iteration_type] = 0
            self.metrics["idea_iteration"]["by_type"][iteration_type] += 1
            
            logger.info(f"Tracked idea iteration: {idea_id}, {iteration_type}")
            
        except Exception as e:
            logger.error(f"Failed to track idea iteration: {e}")
    
    async def track_feedback_submission(self, idea_id: str, feedback_type: str, rating: Optional[int] = None):
        """Track feedback submission event."""
        try:
            event = {
                "event_type": "feedback_submission",
                "idea_id": idea_id,
                "feedback_type": feedback_type,
                "rating": rating,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.events.append(event)
            
            # Update metrics
            if "feedback" not in self.metrics:
                self.metrics["feedback"] = {
                    "total_submissions": 0,
                    "by_type": {},
                    "average_rating": 0.0,
                    "rating_count": 0
                }
            
            self.metrics["feedback"]["total_submissions"] += 1
            
            if feedback_type not in self.metrics["feedback"]["by_type"]:
                self.metrics["feedback"]["by_type"][feedback_type] = 0
            self.metrics["feedback"]["by_type"][feedback_type] += 1
            
            if rating is not None:
                current_avg = self.metrics["feedback"]["average_rating"]
                count = self.metrics["feedback"]["rating_count"]
                new_avg = ((current_avg * count) + rating) / (count + 1)
                self.metrics["feedback"]["average_rating"] = new_avg
                self.metrics["feedback"]["rating_count"] += 1
            
            logger.info(f"Tracked feedback submission: {idea_id}, {feedback_type}")
            
        except Exception as e:
            logger.error(f"Failed to track feedback submission: {e}")
    
    async def get_feedback_analytics(
        self,
        idea_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get feedback analytics for the specified period."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Filter events by date and idea_id
            filtered_events = [
                event for event in self.events
                if event["event_type"] == "feedback_submission"
                and datetime.fromisoformat(event["timestamp"]) >= start_date
                and (idea_id is None or event.get("idea_id") == idea_id)
            ]
            
            # Calculate analytics
            total_feedback = len(filtered_events)
            feedback_by_type = {}
            ratings = []
            
            for event in filtered_events:
                feedback_type = event["feedback_type"]
                if feedback_type not in feedback_by_type:
                    feedback_by_type[feedback_type] = 0
                feedback_by_type[feedback_type] += 1
                
                if event.get("rating") is not None:
                    ratings.append(event["rating"])
            
            average_rating = sum(ratings) / len(ratings) if ratings else None
            
            analytics = {
                "total_feedback": total_feedback,
                "average_rating": average_rating,
                "feedback_by_type": feedback_by_type,
                "rating_distribution": self._calculate_rating_distribution(ratings),
                "trends": self._calculate_trends(filtered_events),
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get feedback analytics: {e}")
            raise
    
    async def get_idea_analytics(self, idea_id: str) -> Dict[str, Any]:
        """Get analytics for a specific idea."""
        try:
            # Filter events for this idea
            idea_events = [
                event for event in self.events
                if event.get("idea_id") == idea_id
            ]
            
            # Calculate metrics
            generations = len([e for e in idea_events if e["event_type"] == "idea_generation"])
            iterations = len([e for e in idea_events if e["event_type"] == "idea_iteration"])
            feedback = len([e for e in idea_events if e["event_type"] == "feedback_submission"])
            
            analytics = {
                "idea_id": idea_id,
                "generations": generations,
                "iterations": iterations,
                "feedback_count": feedback,
                "events": idea_events,
                "created_at": min([datetime.fromisoformat(e["timestamp"]) for e in idea_events]) if idea_events else None,
                "last_activity": max([datetime.fromisoformat(e["timestamp"]) for e in idea_events]) if idea_events else None
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get idea analytics: {e}")
            raise
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get overall system metrics."""
        try:
            return {
                "total_events": len(self.events),
                "metrics": self.metrics,
                "uptime": "24h",  # Mock uptime
                "health": "healthy"
            }
            
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            raise
    
    def _calculate_rating_distribution(self, ratings: List[int]) -> Dict[str, int]:
        """Calculate rating distribution."""
        distribution = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        for rating in ratings:
            distribution[str(rating)] += 1
        return distribution
    
    def _calculate_trends(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate trends from events."""
        # Group events by day
        daily_counts = {}
        for event in events:
            date = datetime.fromisoformat(event["timestamp"]).date()
            if date not in daily_counts:
                daily_counts[date] = 0
            daily_counts[date] += 1
        
        # Calculate trend
        if len(daily_counts) >= 2:
            dates = sorted(daily_counts.keys())
            first_count = daily_counts[dates[0]]
            last_count = daily_counts[dates[-1]]
            trend = "increasing" if last_count > first_count else "decreasing"
        else:
            trend = "stable"
        
        return {
            "daily_counts": daily_counts,
            "trend": trend
        }
