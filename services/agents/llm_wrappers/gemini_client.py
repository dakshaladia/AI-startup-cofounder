"""
Gemini LLM client for AI Startup Co-Founder agents.
"""

import google.generativeai as genai
from typing import List, Dict, Any, Optional
import asyncio
import json

from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class GeminiClient:
    """Gemini LLM client for agent operations."""
    
    def __init__(self):
        self.model = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the Gemini client."""
        try:
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is required")
            
            # Configure Gemini
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Initialize the model
            self.model = genai.GenerativeModel(settings.LLM_MODEL)
            
            self.initialized = True
            logger.info("Gemini client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text using Gemini."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Generate content
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature or settings.LLM_TEMPERATURE,
                    max_output_tokens=max_tokens or settings.LLM_MAX_TOKENS,
                )
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Failed to generate text: {e}")
            raise
    
    async def generate_structured_output(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """Generate structured output using Gemini."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Create structured prompt
            schema_prompt = f"""
            Please respond with a JSON object that matches this schema:
            {json.dumps(schema, indent=2)}
            
            User prompt: {prompt}
            """
            
            if system_prompt:
                schema_prompt = f"{system_prompt}\n\n{schema_prompt}"
            
            # Generate content
            response = await asyncio.to_thread(
                self.model.generate_content,
                schema_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature or settings.LLM_TEMPERATURE,
                    max_output_tokens=settings.LLM_MAX_TOKENS,
                )
            )
            
            # Parse JSON response
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response, returning raw text")
                return {"content": response.text}
            
        except Exception as e:
            logger.error(f"Failed to generate structured output: {e}")
            raise
    
    async def generate_embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-004"
    ) -> List[List[float]]:
        """Generate embeddings using Gemini."""
        try:
            if not self.initialized:
                await self.initialize()
            
            embeddings = []
            for text in texts:
                # Use Gemini's embedding model
                result = await asyncio.to_thread(
                    genai.embed_content,
                    model=model,
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result['embedding'])
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Chat completion using Gemini."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Convert messages to Gemini format
            chat = self.model.start_chat(history=[])
            
            # Get the last user message
            user_message = None
            for message in reversed(messages):
                if message.get("role") == "user":
                    user_message = message.get("content")
                    break
            
            if not user_message:
                raise ValueError("No user message found in messages")
            
            # Generate response
            response = await asyncio.to_thread(
                chat.send_message,
                user_message,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature or settings.LLM_TEMPERATURE,
                    max_output_tokens=max_tokens or settings.LLM_MAX_TOKENS,
                )
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Failed to complete chat: {e}")
            raise
    
    async def close(self):
        """Close the Gemini client."""
        try:
            self.initialized = False
            self.model = None
            logger.info("Gemini client closed")
        except Exception as e:
            logger.error(f"Error closing Gemini client: {e}")
