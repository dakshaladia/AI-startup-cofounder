"""
Core agent orchestration for the multi-agent pipeline.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class AgentOrchestrator:
    """Orchestrates the multi-agent pipeline for idea generation."""
    
    def __init__(self):
        self.agents = {}
        self.llm_client = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the orchestrator and agents."""
        try:
            # Initialize LLM client
            await self._init_llm_client()
            
            # Initialize agents
            await self._init_agents()
            
            self.initialized = True
            logger.info("Agent orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent orchestrator: {e}")
            raise
    
    async def _init_llm_client(self):
        """Initialize LLM client."""
        if settings.LLM_PROVIDER == "gemini":
            from llm_wrappers.gemini_client import GeminiClient
            self.llm_client = GeminiClient()
        elif settings.LLM_PROVIDER == "openai":
            from llm_wrappers.openai_client import OpenAIClient
            self.llm_client = OpenAIClient()
        elif settings.LLM_PROVIDER == "local":
            from llm_wrappers.local_llm import LocalLLMClient
            self.llm_client = LocalLLMClient()
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
        
        await self.llm_client.initialize()
    
    async def _init_agents(self):
        """Initialize all agents."""
        from agents.market_analyst import MarketAnalyst
        from agents.idea_generator import IdeaGenerator
        from agents.critic import Critic
        from agents.pm_refiner import PMRefiner
        from agents.synthesizer import Synthesizer
        
        self.agents = {
            'market_analyst': MarketAnalyst(self.llm_client),
            'idea_generator': IdeaGenerator(self.llm_client),
            'critic': Critic(self.llm_client),
            'pm_refiner': PMRefiner(self.llm_client),
            'synthesizer': Synthesizer(self.llm_client)
        }
        
        # Initialize all agents
        for agent_name, agent in self.agents.items():
            await agent.initialize()
            logger.info(f"Initialized agent: {agent_name}")
    
    async def run_pipeline(
        self,
        topic: str,
        constraints: Dict[str, Any],
        num_ideas: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Run the complete multi-agent pipeline.
        
        Pipeline:
        1. Market Analyst - analyzes market conditions
        2. Idea Generator - creates initial ideas
        3. Critic - evaluates and critiques ideas
        4. PM/Refiner - refines ideas based on feedback
        5. Synthesizer - creates final polished ideas
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Starting pipeline for topic: {topic}")
            
            # Step 1: Market Analysis
            market_analysis = await self._run_market_analyst(topic, constraints)
            logger.info("Market analysis completed")
            
            # Step 2: Idea Generation
            raw_ideas = await self._run_idea_generator(topic, constraints, market_analysis, num_ideas)
            logger.info(f"Generated {len(raw_ideas)} raw ideas")
            
            # Step 3: Critique and Refinement
            refined_ideas = []
            for idea in raw_ideas:
                # Run critic
                critique = await self._run_critic(idea, market_analysis)
                
                # Run PM refiner
                refined_idea = await self._run_pm_refiner(idea, critique, constraints)
                
                # Run synthesizer
                final_idea = await self._run_synthesizer(refined_idea, market_analysis)
                
                refined_ideas.append(final_idea)
            
            logger.info(f"Pipeline completed: {len(refined_ideas)} ideas generated")
            return refined_ideas
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
    
    async def _run_market_analyst(
        self,
        topic: str,
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run the market analyst agent."""
        try:
            agent = self.agents['market_analyst']
            result = await agent.analyze_market(topic, constraints)
            return result
        except Exception as e:
            logger.error(f"Market analyst failed: {e}")
            raise
    
    async def _run_idea_generator(
        self,
        topic: str,
        constraints: Dict[str, Any],
        market_analysis: Dict[str, Any],
        num_ideas: int
    ) -> List[Dict[str, Any]]:
        """Run the idea generator agent."""
        try:
            agent = self.agents['idea_generator']
            result = await agent.generate_ideas(topic, constraints, market_analysis, num_ideas)
            return result
        except Exception as e:
            logger.error(f"Idea generator failed: {e}")
            raise
    
    async def _run_critic(
        self,
        idea: Dict[str, Any],
        market_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run the critic agent."""
        try:
            agent = self.agents['critic']
            result = await agent.critique_idea(idea, market_analysis)
            return result
        except Exception as e:
            logger.error(f"Critic failed: {e}")
            raise
    
    async def _run_pm_refiner(
        self,
        idea: Dict[str, Any],
        critique: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run the PM refiner agent."""
        try:
            agent = self.agents['pm_refiner']
            result = await agent.refine_idea(idea, critique, constraints)
            return result
        except Exception as e:
            logger.error(f"PM refiner failed: {e}")
            raise
    
    async def _run_synthesizer(
        self,
        idea: Dict[str, Any],
        market_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run the synthesizer agent."""
        try:
            agent = self.agents['synthesizer']
            result = await agent.synthesize_idea(idea, market_analysis)
            return result
        except Exception as e:
            logger.error(f"Synthesizer failed: {e}")
            raise
    
    async def run_single_agent(
        self,
        agent_name: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a single agent with input data."""
        try:
            if not self.initialized:
                await self.initialize()
            
            if agent_name not in self.agents:
                raise ValueError(f"Unknown agent: {agent_name}")
            
            agent = self.agents[agent_name]
            result = await agent.process(input_data)
            return result
            
        except Exception as e:
            logger.error(f"Single agent {agent_name} failed: {e}")
            raise
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        if not self.initialized:
            return {"status": "not_initialized"}
        
        status = {}
        for agent_name, agent in self.agents.items():
            try:
                agent_status = await agent.get_status()
                status[agent_name] = agent_status
            except Exception as e:
                status[agent_name] = {"status": "error", "error": str(e)}
        
        return status
    
    async def close(self):
        """Close the orchestrator and all agents."""
        try:
            if self.llm_client:
                await self.llm_client.close()
            
            for agent_name, agent in self.agents.items():
                try:
                    await agent.close()
                except Exception as e:
                    logger.error(f"Failed to close agent {agent_name}: {e}")
            
            logger.info("Agent orchestrator closed")
            
        except Exception as e:
            logger.error(f"Error closing orchestrator: {e}")


# Global orchestrator instance
orchestrator = AgentOrchestrator()
