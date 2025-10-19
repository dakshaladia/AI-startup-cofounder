"""
OpenAI LLM client wrapper.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
import openai
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    """OpenAI LLM client wrapper."""
    
    def __init__(self):
        self.client = None
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
    
    async def initialize(self):
        """Initialize the OpenAI client."""
        try:
            if not settings.OPENAI_API_KEY:
                raise ValueError("OpenAI API key not configured")
            
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Test the connection
            await self.test_connection()
            
            logger.info("OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    async def test_connection(self):
        """Test the OpenAI connection."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            logger.info("OpenAI connection test successful")
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            raise
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text using OpenAI.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI text generation failed: {e}")
            raise
    
    async def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured output using OpenAI.
        
        Args:
            prompt: User prompt
            schema: JSON schema for output
            system_prompt: System prompt
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Structured output
        """
        try:
            # Add schema instruction to prompt
            schema_prompt = f"""
            Please respond with a JSON object that matches this schema:
            {json.dumps(schema, indent=2)}
            
            {prompt}
            """
            
            response = await self.generate_text(
                prompt=schema_prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                **kwargs
            )
            
            # Parse JSON response
            try:
                return json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response: {response}")
                raise ValueError(f"Invalid JSON response: {e}")
            
        except Exception as e:
            logger.error(f"OpenAI structured generation failed: {e}")
            raise
    
    async def generate_embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-ada-002"
    ) -> List[List[float]]:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of texts to embed
            model: Embedding model to use
            
        Returns:
            List of embedding vectors
        """
        try:
            response = await self.client.embeddings.create(
                model=model,
                input=texts
            )
            
            return [embedding.embedding for embedding in response.data]
            
        except Exception as e:
            logger.error(f"OpenAI embeddings generation failed: {e}")
            raise
    
    async def generate_image_caption(
        self,
        image_url: str,
        prompt: str = "Describe this image in detail."
    ) -> str:
        """
        Generate caption for an image.
        
        Args:
            image_url: URL of the image
            prompt: Prompt for caption generation
            
        Returns:
            Generated caption
        """
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI image caption generation failed: {e}")
            raise
    
    async def moderate_content(self, text: str) -> Dict[str, Any]:
        """
        Moderate content for safety.
        
        Args:
            text: Text to moderate
            
        Returns:
            Moderation results
        """
        try:
            response = await self.client.moderations.create(input=text)
            
            return {
                "flagged": response.results[0].flagged,
                "categories": response.results[0].categories,
                "category_scores": response.results[0].category_scores
            }
            
        except Exception as e:
            logger.error(f"OpenAI content moderation failed: {e}")
            raise
    
    async def close(self):
        """Close the OpenAI client."""
        try:
            if self.client:
                await self.client.close()
            logger.info("OpenAI client closed")
        except Exception as e:
            logger.error(f"Error closing OpenAI client: {e}")
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        # Mock implementation - would normally track usage
        return {
            "total_requests": 0,
            "total_tokens": 0,
            "cost": 0.0
        }
