"""
Local LLM client wrapper for running models locally.
"""

import asyncio
import json
import aiohttp
from typing import List, Dict, Any, Optional

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class LocalLLMClient:
    """Local LLM client wrapper."""
    
    def __init__(self):
        self.base_url = settings.LOCAL_LLM_URL
        self.model = settings.LOCAL_LLM_MODEL
        self.session = None
    
    async def initialize(self):
        """Initialize the local LLM client."""
        try:
            self.session = aiohttp.ClientSession()
            
            # Test the connection
            await self.test_connection()
            
            logger.info("Local LLM client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize local LLM client: {e}")
            raise
    
    async def test_connection(self):
        """Test the local LLM connection."""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    logger.info("Local LLM connection test successful")
                else:
                    raise Exception(f"Local LLM returned status {response.status}")
        except Exception as e:
            logger.error(f"Local LLM connection test failed: {e}")
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
        Generate text using local LLM.
        
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
            # Prepare the request
            request_data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature or 0.7,
                    "num_predict": max_tokens or 1000
                }
            }
            
            if system_prompt:
                request_data["system"] = system_prompt
            
            # Make request to local LLM
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=request_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "")
                else:
                    raise Exception(f"Local LLM returned status {response.status}")
            
        except Exception as e:
            logger.error(f"Local LLM text generation failed: {e}")
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
        Generate structured output using local LLM.
        
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
            logger.error(f"Local LLM structured generation failed: {e}")
            raise
    
    async def generate_embeddings(
        self,
        texts: List[str],
        model: str = "nomic-embed-text"
    ) -> List[List[float]]:
        """
        Generate embeddings for texts using local model.
        
        Args:
            texts: List of texts to embed
            model: Embedding model to use
            
        Returns:
            List of embedding vectors
        """
        try:
            # For local models, we might need to use a different approach
            # This is a mock implementation
            embeddings = []
            for text in texts:
                # Mock embedding generation
                # In a real implementation, this would call a local embedding model
                embedding = [0.1] * 384  # Mock 384-dimensional embedding
                embeddings.append(embedding)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Local LLM embeddings generation failed: {e}")
            raise
    
    async def generate_image_caption(
        self,
        image_url: str,
        prompt: str = "Describe this image in detail."
    ) -> str:
        """
        Generate caption for an image using local model.
        
        Args:
            image_url: URL of the image
            prompt: Prompt for caption generation
            
        Returns:
            Generated caption
        """
        try:
            # Mock implementation for local image captioning
            # In a real implementation, this would use a local vision model
            return f"Image caption for {image_url}: This is a mock caption generated by local LLM."
            
        except Exception as e:
            logger.error(f"Local LLM image caption generation failed: {e}")
            raise
    
    async def moderate_content(self, text: str) -> Dict[str, Any]:
        """
        Moderate content for safety using local model.
        
        Args:
            text: Text to moderate
            
        Returns:
            Moderation results
        """
        try:
            # Mock implementation for local content moderation
            # In a real implementation, this would use a local moderation model
            return {
                "flagged": False,
                "categories": {},
                "category_scores": {}
            }
            
        except Exception as e:
            logger.error(f"Local LLM content moderation failed: {e}")
            raise
    
    async def close(self):
        """Close the local LLM client."""
        try:
            if self.session:
                await self.session.close()
            logger.info("Local LLM client closed")
        except Exception as e:
            logger.error(f"Error closing local LLM client: {e}")
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        # Mock implementation - would normally track usage
        return {
            "total_requests": 0,
            "total_tokens": 0,
            "cost": 0.0
        }
