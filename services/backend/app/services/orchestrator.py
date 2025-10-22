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
from app.core.config import settings

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
        num_ideas: int = 3,
        model_settings: Optional[Dict[str, str]] = None
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
            market_model = model_settings.get('market_analyst', 'gemini-2.0-flash-lite') if model_settings else 'gemini-2.0-flash-lite'
            market_analysis = await self._run_market_analyst(topic, constraints, model_name=market_model)
            logger.info("Market analysis completed")
            
            # Step 2: Idea Generation
            idea_model = model_settings.get('idea_generator', 'gemini-2.0-flash-lite') if model_settings else 'gemini-2.0-flash-lite'
            raw_ideas = await self._run_idea_generator(topic, constraints, market_analysis, num_ideas, model_name=idea_model)
            logger.info(f"Generated {len(raw_ideas)} raw ideas")
            
            # Step 3: Critique and Refinement
            refined_ideas = []
            for idea in raw_ideas:
                # Run critic
                critic_model = model_settings.get('critic', 'gemini-2.0-flash-lite') if model_settings else 'gemini-2.0-flash-lite'
                critique = await self._run_critic(idea, market_analysis, model_name=critic_model)
                
                # Run PM refiner
                pm_model = model_settings.get('pm_refiner', 'gemini-2.0-flash-lite') if model_settings else 'gemini-2.0-flash-lite'
                refined_idea = await self._run_pm_refiner(idea, critique, constraints, model_name=pm_model)
                
                # Run synthesizer
                synth_model = model_settings.get('synthesizer', 'gemini-2.0-flash-lite') if model_settings else 'gemini-2.0-flash-lite'
                synthesizer_output = await self._run_synthesizer(idea, market_analysis, refined_idea, model_name=synth_model)
                
                # Create final idea snapshot with all agent outputs
                final_idea = IdeaSnapshot(
                    id=idea.id,
                    title=idea.title,
                    description=idea.description,
                    market_analysis=market_analysis,
                    feasibility_score=idea.feasibility_score,
                    novelty_score=idea.novelty_score,
                    market_signal_score=idea.market_signal_score,
                    overall_score=idea.overall_score,
                    status=IdeaStatus.COMPLETED,
                    critic_output=critique,
                    pm_refiner_output=refined_idea,
                    synthesizer_output=synthesizer_output
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
        iteration_type: str,
        model_settings: Optional[Dict[str, str]] = None
    ) -> IdeaSnapshot:
        """
        Iterate on an existing idea based on feedback.
        
        Args:
            idea: Existing idea to iterate
            feedback: Feedback for improvement
            iteration_type: Type of iteration to perform
        """
        try:
            logger.info(f"🔄 ITERATION START: idea={idea.id}, type={iteration_type}, feedback='{feedback[:100]}...'")
            
            # Create new version with proper deep copy
            new_idea = idea.model_copy(deep=True)
            new_idea.version = idea.version + 1
            new_idea.status = IdeaStatus.REFINING
            new_idea.updated_at = datetime.utcnow()
            
            # Apply iteration based on type
            if iteration_type == "critique":
                logger.info("→ Running Critic agent with user feedback...")
                critic_model = model_settings.get('critic', 'gemini-2.0-flash-lite') if model_settings else 'gemini-2.0-flash-lite'
                critique = await self._run_critic(idea, idea.market_analysis, feedback, model_name=critic_model)
                new_idea.critic_output = critique
                logger.info(f"✅ Critic updated: {len(critique.get('suggestions', []))} suggestions generated")
                
            elif iteration_type == "refinement":
                logger.info("→ Running PM Refiner agent with user feedback...")
                pm_model = model_settings.get('pm_refiner', 'gemini-2.0-flash-lite') if model_settings else 'gemini-2.0-flash-lite'
                # Pass empty dict as critique and feedback as user_feedback
                refined = await self._run_pm_refiner(idea, {}, {}, user_feedback=feedback, model_name=pm_model)
                new_idea.pm_refiner_output = refined
                logger.info(f"✅ PM Refiner updated: {len(refined.get('features', []))} features, timeline: {refined.get('timeline', 'N/A')}")
                
            elif iteration_type == "synthesis":
                logger.info("→ Running Synthesizer agent with user feedback...")
                synth_model = model_settings.get('synthesizer', 'gemini-2.0-flash-lite') if model_settings else 'gemini-2.0-flash-lite'
                synthesized = await self._run_synthesizer(idea, idea.market_analysis, None, feedback, model_name=synth_model)
                new_idea.synthesizer_output = synthesized
                logger.info(f"✅ Synthesizer updated: {synthesized.get('final_concept', '')[:80]}...")
                
            elif iteration_type == "market_analysis":
                logger.info("→ Running Market Analyst agent with user feedback...")
                market_model = model_settings.get('market_analyst', 'gemini-2.0-flash-lite') if model_settings else 'gemini-2.0-flash-lite'
                # Re-run market analysis with user feedback
                market_analysis = await self._run_market_analyst(idea.title, constraints={}, user_feedback=feedback, model_name=market_model)
                new_idea.market_analysis = market_analysis
                new_idea.market_analyst_output = market_analysis
                logger.info(f"✅ Market Analysis updated: size={market_analysis.get('market_size')}, growth={market_analysis.get('growth_potential')}")
                
            else:
                logger.info("→ Running general iteration...")
                # General iteration
                new_idea.description = await self._apply_feedback(idea.description, feedback)
            
            # Update scores (keep existing if recalculation fails)
            try:
                new_idea = await self._recalculate_scores(new_idea)
                logger.info(f"📊 Scores: Feasibility={new_idea.feasibility_score:.2f}, Novelty={new_idea.novelty_score:.2f}, Market={new_idea.market_signal_score:.2f}, Overall={new_idea.overall_score:.2f}")
            except Exception as score_error:
                logger.warning(f"⚠️  Score recalculation failed, keeping existing scores: {score_error}")
            
            # Update status to completed
            new_idea.status = IdeaStatus.COMPLETED
            
            # Save iteration
            saved_idea = await self.persistence.save_idea_snapshot(new_idea)
            
            # Track analytics
            await self.analytics.track_idea_iteration(idea.id, iteration_type)
            
            logger.info(f"✅ ITERATION COMPLETE: {saved_idea.id} (v{saved_idea.version})")
            return saved_idea
            
        except Exception as e:
            logger.error(f"❌ ITERATION FAILED: {e}", exc_info=True)
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
        constraints: Dict[str, Any] | str = None,
        user_feedback: Optional[str] = None,
        model_name: str = 'gemini-2.0-flash-lite'
    ) -> Dict[str, Any]:
        """Run the market analyst agent using Gemini.
        
        Args:
            topic: The topic to analyze
            constraints: Either constraints dict or user feedback string (for backward compatibility)
            user_feedback: Additional user feedback (optional)
        """
        use_gemini = (
            settings.LLM_PROVIDER.lower() == "gemini" and bool(settings.GEMINI_API_KEY)
        )

        if use_gemini:
            try:
                import google.generativeai as genai
                import json as _json

                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(model_name)

                # Handle constraints as either dict or string (user feedback)
                if isinstance(constraints, str):
                    user_feedback = constraints
                    constraints_text = "none"
                else:
                    constraints_text = ", ".join(
                        f"{k}: {v}" for k, v in (constraints or {}).items()
                    )

                # Build feedback instruction
                feedback_instruction = ""
                if user_feedback:
                    feedback_instruction = (
                        f"\n\n🎯 CRITICAL USER REQUEST - YOU MUST ADDRESS THIS:\n"
                        f"{user_feedback}\n\n"
                        f"IMPORTANT: Read the user's request carefully and make sure your response directly addresses it.\n"
                        f"- If they ask for 'current startups', list specific company names in the competitive_landscape and current_players fields.\n"
                        f"- If they ask for specific segments, focus on those in target_segments.\n"
                        f"- If they ask for trends, make sure key_trends reflects their specific interest.\n"
                        f"- Make your response DIRECTLY answer their question. Do not give generic information.\n"
                    )

                prompt = (
                    f"Analyze the market for startup ideas in the topic: '{topic}'.\n"
                    f"Constraints: {constraints_text or 'none'}."
                    f"{feedback_instruction}\n\n"
                    f"Provide a JSON response with these fields:\n"
                    f"- market_size: 'Small', 'Medium', or 'Large'\n"
                    f"- competition_level: 'Low', 'Medium', or 'High'\n"
                    f"- growth_potential: 'Low', 'Medium', or 'High'\n"
                    f"- key_trends: array of 3-5 relevant trends that DIRECTLY address user feedback\n"
                    f"- target_segments: array of 3-5 target customer segments (if user specified segments, use those)\n"
                    f"- market_opportunity: brief description that incorporates user feedback\n"
                    f"- competitive_landscape: overview of competitors (if user asked for specific startups, NAME THEM)\n"
                    f"- current_players: array of 3-8 specific company/startup names currently in this space (REQUIRED if user asked for startups/competitors)\n"
                    f"Respond with valid JSON only."
                )

                response = await asyncio.to_thread(
                    model.generate_content,
                    prompt,
                )

                raw_text = getattr(response, "text", "") or ""
                
                try:
                    # Try to parse JSON from response
                    start = raw_text.find("{")
                    end = raw_text.rfind("}") + 1
                    if start != -1 and end > start:
                        json_text = raw_text[start:end]
                        return _json.loads(json_text)
                except Exception:
                    pass

            except Exception as llm_error:
                logger.warning(f"Gemini market analysis failed, using fallback: {llm_error}")

        # Fallback mock implementation
        return {
            "market_size": "Large",
            "competition_level": "High",
            "growth_potential": "High",
            "key_trends": ["AI adoption", "Remote work", "Sustainability"],
            "target_segments": ["SMBs", "Enterprises", "Consumers"],
            "market_opportunity": f"Growing market for {topic} solutions",
            "competitive_landscape": "Moderate to high competition with established players"
        }
    
    async def _run_idea_generator(
        self,
        topic: str,
        constraints: Dict[str, Any],
        market_analysis: Dict[str, Any],
        num_ideas: int,
        model_name: str = 'gemini-2.0-flash-lite'
    ) -> List[IdeaSnapshot]:
        """Run the idea generator agent.

        If Gemini is configured, use it to generate realistic titles and descriptions.
        Falls back to deterministic mock ideas if LLM is not available.
        """
        ideas: List[IdeaSnapshot] = []

        use_gemini = (
            settings.LLM_PROVIDER.lower() == "gemini" and bool(settings.GEMINI_API_KEY)
        )

        if use_gemini:
            try:
                import google.generativeai as genai

                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(model_name)

                schema_hint = (
                    "Respond with JSON array of objects: "
                    "[{\"title\": string, \"description\": string}] "
                    f"of length {num_ideas}."
                )

                constraints_text = ", ".join(
                    f"{k}: {v}" for k, v in (constraints or {}).items()
                )
                prompt = (
                    f"Generate {num_ideas} concise startup ideas for the topic: '{topic}'.\n"
                    f"Constraints: {constraints_text or 'none'}.\n"
                    f"Market analysis: {market_analysis}.\n"
                    f"Each idea must have: title (<= 12 words) and description (<= 2 sentences).\n"
                    f"{schema_hint}"
                )

                response = await asyncio.to_thread(
                    model.generate_content,
                    prompt,
                )

                raw_text = getattr(response, "text", "") or ""

                parsed: List[Dict[str, Any]] = []
                try:
                    import json as _json

                    # Try to locate a JSON array in the response
                    start = raw_text.find("[")
                    end = raw_text.rfind("]")
                    if start != -1 and end != -1 and end > start:
                        parsed = _json.loads(raw_text[start : end + 1])
                except Exception:  # fallback handled below
                    parsed = []

                for i in range(num_ideas):
                    item = parsed[i] if i < len(parsed) and isinstance(parsed[i], dict) else {}
                    title = item.get("title") or f"{topic} — Idea {i+1}"
                    description = item.get("description") or (
                        "A focused concept leveraging the given constraints and market context."
                    )

                    ideas.append(
                        IdeaSnapshot(
                            id=str(uuid.uuid4()),
                            title=title,
                            description=description,
                            market_analysis=market_analysis,
                            feasibility_score=0.7,
                            novelty_score=0.8,
                            market_signal_score=0.6,
                            overall_score=0.7,
                            status=IdeaStatus.DRAFT,
                        )
                    )

                return ideas

            except Exception as llm_error:
                logger.warning(
                    f"Gemini generation failed, falling back to mock ideas: {llm_error}"
                )

        # Fallback mock generation
        for i in range(num_ideas):
            ideas.append(
                IdeaSnapshot(
                    id=str(uuid.uuid4()),
                    title=f"{topic} — Idea {i+1}",
                    description="A focused concept leveraging the given constraints and market context.",
                    market_analysis=market_analysis,
                    feasibility_score=0.7,
                    novelty_score=0.8,
                    market_signal_score=0.6,
                    overall_score=0.7,
                    status=IdeaStatus.DRAFT,
                )
            )
        return ideas
    
    async def _run_critic(
        self,
        idea: IdeaSnapshot,
        market_analysis: Optional[Dict[str, Any]] = None,
        feedback: Optional[str] = None,
        model_name: str = 'gemini-2.0-flash-lite'
    ) -> Dict[str, Any]:
        """Run the critic agent using Gemini."""
        use_gemini = (
            settings.LLM_PROVIDER.lower() == "gemini" and bool(settings.GEMINI_API_KEY)
        )

        if use_gemini:
            try:
                import google.generativeai as genai
                import json as _json

                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(model_name)

                market_context = ""
                if market_analysis:
                    market_context = f"Market context: {market_analysis}"

                # Build feedback instruction
                feedback_instruction = ""
                if feedback and feedback != 'none':
                    feedback_instruction = (
                        f"\n\n🎯 CRITICAL USER REQUEST - FOCUS YOUR CRITIQUE HERE:\n"
                        f"{feedback}\n\n"
                        f"MANDATORY: Completely reorient your critique to address this specific feedback.\n"
                        f"- If user asks about X, make X the PRIMARY focus of your analysis.\n"
                        f"- Put the most relevant strengths/weaknesses/suggestions at the TOP of each array.\n"
                        f"- Be SPECIFIC about what the user asked - don't be generic.\n"
                        f"- If they mention competitors, technical details, or market segments, address those explicitly.\n"
                        f"- Your critique should feel custom-tailored to their question.\n"
                    )

                prompt = (
                    f"Critically analyze this startup idea:\n"
                    f"Title: {idea.title}\n"
                    f"Description: {idea.description}\n"
                    f"{market_context}"
                    f"{feedback_instruction}\n\n"
                    f"Provide a JSON response with these fields:\n"
                    f"- strengths: array of 3-5 key strengths (consider feedback)\n"
                    f"- weaknesses: array of 3-5 potential weaknesses (align with feedback focus)\n"
                    f"- suggestions: array of 3-5 improvement suggestions (incorporate feedback direction)\n"
                    f"- score: number between 0.0 and 1.0 (overall viability)\n"
                    f"- risks: array of 3-5 key risks to consider (relevant to feedback)\n"
                    f"- opportunities: array of 3-5 growth opportunities (explore feedback direction)\n"
                    f"Respond with valid JSON only."
                )

                response = await asyncio.to_thread(
                    model.generate_content,
                    prompt,
                )

                raw_text = getattr(response, "text", "") or ""
                
                try:
                    # Try to parse JSON from response
                    start = raw_text.find("{")
                    end = raw_text.rfind("}") + 1
                    if start != -1 and end > start:
                        json_text = raw_text[start:end]
                        return _json.loads(json_text)
                except Exception:
                    pass

            except Exception as llm_error:
                logger.warning(f"Gemini critic analysis failed, using fallback: {llm_error}")

        # Fallback mock implementation
        return {
            "strengths": ["Clear value proposition", "Good market fit"],
            "weaknesses": ["High competition", "Complex implementation"],
            "suggestions": ["Simplify MVP", "Focus on niche market"],
            "score": 0.6,
            "risks": ["Market saturation", "Technical complexity"],
            "opportunities": ["Emerging trends", "Underserved segments"]
        }
    
    async def _run_pm_refiner(
        self,
        idea: IdeaSnapshot,
        critique: Dict[str, Any] | str,
        constraints: Dict[str, Any],
        user_feedback: Optional[str] = None,
        model_name: str = 'gemini-2.0-flash-lite'
    ) -> Dict[str, Any]:
        """Run the PM refiner agent using Gemini.
        
        Args:
            idea: The idea to refine
            critique: Either critic output (dict) or user feedback (str)
            constraints: Any constraints to apply
            user_feedback: Additional user feedback (optional)
        """
        use_gemini = (
            settings.LLM_PROVIDER.lower() == "gemini" and bool(settings.GEMINI_API_KEY)
        )

        if use_gemini:
            try:
                import google.generativeai as genai
                import json as _json

                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(model_name)

                constraints_text = ", ".join(
                    f"{k}: {v}" for k, v in (constraints or {}).items()
                )

                # Handle critique as either dict or string (user feedback)
                critique_text = critique if isinstance(critique, str) else str(critique)
                
                # Build user feedback instruction
                feedback_instruction = ""
                if user_feedback:
                    feedback_instruction = (
                        f"\n\n🎯 CRITICAL USER REQUEST - RESTRUCTURE YOUR REFINEMENTS:\n"
                        f"{user_feedback}\n\n"
                        f"MANDATORY: You MUST completely revise your product refinements based on this feedback.\n"
                        f"- If user says 'focus on X customers', change target_segments and features for X.\n"
                        f"- If user says 'reduce scope', cut the features list significantly.\n"
                        f"- If user says 'add Y feature', ensure Y appears prominently in the features array.\n"
                        f"- If user mentions timeline changes, adjust the timeline field.\n"
                        f"- Make DRAMATIC changes - the user should clearly see their feedback applied.\n"
                        f"- Do NOT just append - REPLACE content to match feedback.\n"
                    )

                prompt = (
                    f"Refine this startup idea from a product management perspective:\n"
                    f"Title: {idea.title}\n"
                    f"Description: {idea.description}\n"
                    f"Critique: {critique_text}\n"
                    f"Constraints: {constraints_text or 'none'}"
                    f"{feedback_instruction}\n\n"
                    f"Provide a JSON response with these fields:\n"
                    f"- refinements: array of 3-5 specific product refinements (apply feedback)\n"
                    f"- priorities: array of 3-5 development priorities (modify per feedback)\n"
                    f"- timeline: realistic MVP timeline (e.g., '3-6 months')\n"
                    f"- resources: array of required team members (adjust if needed)\n"
                    f"- features: array of 5-8 core features for MVP (update based on feedback)\n"
                    f"- user_stories: array of 3-5 key user stories (align with feedback)\n"
                    f"- success_metrics: array of 3-5 key metrics to track\n"
                    f"Respond with valid JSON only."
                )

                response = await asyncio.to_thread(
                    model.generate_content,
                    prompt,
                )

                raw_text = getattr(response, "text", "") or ""
                
                try:
                    # Try to parse JSON from response
                    start = raw_text.find("{")
                    end = raw_text.rfind("}") + 1
                    if start != -1 and end > start:
                        json_text = raw_text[start:end]
                        return _json.loads(json_text)
                except Exception:
                    pass

            except Exception as llm_error:
                logger.warning(f"Gemini PM refinement failed, using fallback: {llm_error}")

        # Fallback mock implementation
        return {
            "refinements": ["Simplified feature set", "Clearer user journey"],
            "priorities": ["Core functionality first", "User feedback loop"],
            "timeline": "3-6 months MVP",
            "resources": ["2 developers", "1 designer"],
            "features": ["User authentication", "Core functionality", "Analytics"],
            "user_stories": ["As a user, I want to...", "As a user, I need to..."],
            "success_metrics": ["User engagement", "Revenue growth", "User retention"]
        }
    
    async def _run_synthesizer(
        self,
        idea: IdeaSnapshot,
        market_analysis: Optional[Dict[str, Any]] = None,
        refined_idea: Optional[Dict[str, Any]] = None,
        feedback: Optional[str] = None,
        model_name: str = 'gemini-2.0-flash-lite'
    ) -> Dict[str, Any]:
        """Run the synthesizer agent using Gemini."""
        use_gemini = (
            settings.LLM_PROVIDER.lower() == "gemini" and bool(settings.GEMINI_API_KEY)
        )

        if use_gemini:
            try:
                import google.generativeai as genai
                import json as _json

                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(model_name)

                market_context = ""
                if market_analysis:
                    market_context = f"Market analysis: {market_analysis}"
                
                refinement_context = ""
                if refined_idea:
                    refinement_context = f"\nPM Refinements: {refined_idea}"

                # Build feedback instruction
                feedback_instruction = ""
                if feedback and feedback != 'none':
                    feedback_instruction = (
                        f"\n\n🎯 CRITICAL USER REQUEST - MODIFY YOUR OUTPUT:\n"
                        f"{feedback}\n\n"
                        f"MANDATORY: You MUST completely rewrite and modify your synthesis based on this feedback.\n"
                        f"- Read the feedback word-by-word and ensure EVERY point is addressed.\n"
                        f"- If they say 'focus on X', make X the PRIMARY focus of your synthesis.\n"
                        f"- If they say 'add Y', explicitly include Y in relevant sections.\n"
                        f"- If they say 'change Z', make sure Z is completely different.\n"
                        f"- Your output should be NOTICEABLY DIFFERENT from the original.\n"
                        f"- Do NOT just add a sentence - RESTRUCTURE to reflect the feedback.\n"
                    )
                
                prompt = (
                    f"Synthesize and finalize this startup idea:\n"
                    f"Title: {idea.title}\n"
                    f"Description: {idea.description}\n"
                    f"{market_context}\n"
                    f"{refinement_context}"
                    f"{feedback_instruction}\n"
                    f"Provide a JSON response with these fields:\n"
                    f"- final_concept: comprehensive 2-3 sentence description (apply feedback here)\n"
                    f"- key_features: array of 5-8 core features (modify based on feedback)\n"
                    f"- business_model: primary revenue model (adjust if feedback requires)\n"
                    f"- go_to_market: strategy for reaching customers (update per feedback)\n"
                    f"- value_proposition: clear value statement (align with feedback)\n"
                    f"- competitive_advantage: key differentiators (incorporate feedback)\n"
                    f"- target_customers: primary customer segments (update if feedback specifies)\n"
                    f"- revenue_projections: realistic 3-year projections\n"
                    f"Respond with valid JSON only."
                )

                response = await asyncio.to_thread(
                    model.generate_content,
                    prompt,
                )

                raw_text = getattr(response, "text", "") or ""
                
                try:
                    # Try to parse JSON from response
                    start = raw_text.find("{")
                    end = raw_text.rfind("}") + 1
                    if start != -1 and end > start:
                        json_text = raw_text[start:end]
                        return _json.loads(json_text)
                except Exception:
                    pass

            except Exception as llm_error:
                logger.warning(f"Gemini synthesis failed, using fallback: {llm_error}")

        # Fallback mock implementation
        return {
            "final_concept": "Polished idea concept",
            "key_features": ["Feature 1", "Feature 2", "Feature 3"],
            "business_model": "SaaS subscription",
            "go_to_market": "Direct sales + partnerships",
            "value_proposition": "Clear value for target customers",
            "competitive_advantage": "Unique positioning in market",
            "target_customers": ["SMBs", "Enterprises"],
            "revenue_projections": "Conservative growth projections"
        }
    
    async def _apply_feedback(self, content: str, feedback: str) -> str:
        """Apply feedback to content using Gemini."""
        use_gemini = (
            settings.LLM_PROVIDER.lower() == "gemini" and bool(settings.GEMINI_API_KEY)
        )

        if use_gemini:
            try:
                import google.generativeai as genai

                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(settings.LLM_MODEL)

                prompt = (
                    f"Refine this content based on the feedback provided:\n\n"
                    f"Original content: {content}\n\n"
                    f"Feedback: {feedback}\n\n"
                    f"Provide an improved version that addresses the feedback while maintaining the core message."
                )

                response = await asyncio.to_thread(
                    model.generate_content,
                    prompt,
                )

                refined_content = getattr(response, "text", "") or ""
                if refined_content.strip():
                    return refined_content.strip()

            except Exception as llm_error:
                logger.warning(f"Gemini feedback application failed, using fallback: {llm_error}")

        # Fallback mock implementation
        return f"{content}\n\n[Refined based on feedback: {feedback}]"
    
    async def _recalculate_scores(self, idea: IdeaSnapshot) -> IdeaSnapshot:
        """Recalculate scores for an idea using Gemini."""
        use_gemini = (
            settings.LLM_PROVIDER.lower() == "gemini" and bool(settings.GEMINI_API_KEY)
        )

        if use_gemini:
            try:
                import google.generativeai as genai
                import json as _json

                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(settings.LLM_MODEL)

                prompt = (
                    f"Evaluate this startup idea and provide scores (0.0 to 1.0):\n"
                    f"Title: {idea.title}\n"
                    f"Description: {idea.description}\n"
                    f"Market Analysis: {idea.market_analysis}\n\n"
                    f"Provide a JSON response with these fields:\n"
                    f"- feasibility_score: technical and business feasibility (0.0-1.0)\n"
                    f"- novelty_score: innovation and uniqueness (0.0-1.0)\n"
                    f"- market_signal_score: market demand and opportunity (0.0-1.0)\n"
                    f"- overall_score: weighted average of all scores (0.0-1.0)\n"
                    f"Respond with valid JSON only."
                )

                response = await asyncio.to_thread(
                    model.generate_content,
                    prompt,
                )

                raw_text = getattr(response, "text", "") or ""
                
                try:
                    # Try to parse JSON from response
                    start = raw_text.find("{")
                    end = raw_text.rfind("}") + 1
                    if start != -1 and end > start:
                        json_text = raw_text[start:end]
                        scores = _json.loads(json_text)
                        
                        # Update scores if valid
                        if "feasibility_score" in scores:
                            idea.feasibility_score = float(scores["feasibility_score"])
                        if "novelty_score" in scores:
                            idea.novelty_score = float(scores["novelty_score"])
                        if "market_signal_score" in scores:
                            idea.market_signal_score = float(scores["market_signal_score"])
                        if "overall_score" in scores:
                            idea.overall_score = float(scores["overall_score"])
                        else:
                            # Calculate overall if not provided
                            idea.overall_score = (idea.feasibility_score + idea.novelty_score + idea.market_signal_score) / 3
                        
                        return idea
                except Exception:
                    pass

            except Exception as llm_error:
                logger.warning(f"Gemini scoring failed, using fallback: {llm_error}")

        # Fallback mock implementation
        idea.overall_score = (idea.feasibility_score + idea.novelty_score + idea.market_signal_score) / 3
        return idea
