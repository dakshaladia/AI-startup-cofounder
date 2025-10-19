"""
Embedding service for generating text and image embeddings.
"""

import asyncio
import numpy as np
from typing import List, Dict, Any, Optional, Union
import json
from datetime import datetime

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class Embedder:
    """Service for generating embeddings for text and images."""
    
    def __init__(self):
        self.text_model = None
        self.image_model = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the embedder with models."""
        try:
            # Initialize text embedding model
            await self._init_text_model()
            
            # Initialize image embedding model
            await self._init_image_model()
            
            self.initialized = True
            logger.info("Embedder initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedder: {e}")
            raise
    
    async def _init_text_model(self):
        """Initialize text embedding model."""
        try:
            if settings.MOCK_EMBEDDINGS:
                # Mock text model for development
                self.text_model = MockTextEmbedder()
            else:
                # Real text embedding model
                from sentence_transformers import SentenceTransformer
                self.text_model = SentenceTransformer(settings.TEXT_EMBEDDING_MODEL)
            
            logger.info(f"Text embedding model initialized: {settings.TEXT_EMBEDDING_MODEL}")
            
        except Exception as e:
            logger.error(f"Failed to initialize text model: {e}")
            raise
    
    async def _init_image_model(self):
        """Initialize image embedding model."""
        try:
            if settings.MOCK_EMBEDDINGS:
                # Mock image model for development
                self.image_model = MockImageEmbedder()
            else:
                # Real image embedding model
                from sentence_transformers import SentenceTransformer
                self.image_model = SentenceTransformer(settings.IMAGE_EMBEDDING_MODEL)
            
            logger.info(f"Image embedding model initialized: {settings.IMAGE_EMBEDDING_MODEL}")
            
        except Exception as e:
            logger.error(f"Failed to initialize image model: {e}")
            raise
    
    async def embed_text(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for text inputs.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Generating embeddings for {len(texts)} texts")
            
            # Generate embeddings
            embeddings = await self._generate_text_embeddings(texts)
            
            logger.info(f"Generated {len(embeddings)} text embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate text embeddings: {e}")
            raise
    
    async def embed_image(self, images: List[Union[str, bytes]]) -> List[List[float]]:
        """
        Generate embeddings for image inputs.
        
        Args:
            images: List of image paths or bytes
            
        Returns:
            List of embedding vectors
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Generating embeddings for {len(images)} images")
            
            # Generate embeddings
            embeddings = await self._generate_image_embeddings(images)
            
            logger.info(f"Generated {len(embeddings)} image embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate image embeddings: {e}")
            raise
    
    async def embed_multimodal(
        self,
        texts: List[str],
        images: List[Union[str, bytes]]
    ) -> Dict[str, List[List[float]]]:
        """
        Generate embeddings for multimodal inputs.
        
        Args:
            texts: List of texts to embed
            images: List of images to embed
            
        Returns:
            Dictionary with text and image embeddings
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Generating multimodal embeddings for {len(texts)} texts and {len(images)} images")
            
            # Generate embeddings concurrently
            text_task = asyncio.create_task(self.embed_text(texts))
            image_task = asyncio.create_task(self.embed_image(images))
            
            text_embeddings, image_embeddings = await asyncio.gather(text_task, image_task)
            
            result = {
                "text_embeddings": text_embeddings,
                "image_embeddings": image_embeddings
            }
            
            logger.info("Multimodal embeddings generated successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate multimodal embeddings: {e}")
            raise
    
    async def _generate_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate text embeddings using the model."""
        try:
            if settings.MOCK_EMBEDDINGS:
                # Mock embeddings for development
                return self.text_model.embed_texts(texts)
            else:
                # Real embeddings
                embeddings = self.text_model.encode(texts)
                return embeddings.tolist()
                
        except Exception as e:
            logger.error(f"Text embedding generation failed: {e}")
            raise
    
    async def _generate_image_embeddings(self, images: List[Union[str, bytes]]) -> List[List[float]]:
        """Generate image embeddings using the model."""
        try:
            if settings.MOCK_EMBEDDINGS:
                # Mock embeddings for development
                return self.image_model.embed_images(images)
            else:
                # Real embeddings
                embeddings = self.image_model.encode(images)
                return embeddings.tolist()
                
        except Exception as e:
            logger.error(f"Image embedding generation failed: {e}")
            raise
    
    async def get_embedding_dimensions(self) -> Dict[str, int]:
        """Get embedding dimensions for text and image models."""
        try:
            if not self.initialized:
                await self.initialize()
            
            return {
                "text_dimension": settings.TEXT_EMBEDDING_DIMENSION,
                "image_dimension": settings.IMAGE_EMBEDDING_DIMENSION
            }
            
        except Exception as e:
            logger.error(f"Failed to get embedding dimensions: {e}")
            raise
    
    async def close(self):
        """Close the embedder."""
        try:
            if self.text_model:
                del self.text_model
            if self.image_model:
                del self.image_model
            
            logger.info("Embedder closed")
            
        except Exception as e:
            logger.error(f"Error closing embedder: {e}")


class MockTextEmbedder:
    """Mock text embedder for development."""
    
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate mock text embeddings."""
        embeddings = []
        for text in texts:
            # Generate deterministic mock embedding based on text
            embedding = [hash(text) % 100 / 100.0 for _ in range(self.dimension)]
            embeddings.append(embedding)
        return embeddings


class MockImageEmbedder:
    """Mock image embedder for development."""
    
    def __init__(self, dimension: int = 512):
        self.dimension = dimension
    
    def embed_images(self, images: List[Union[str, bytes]]) -> List[List[float]]:
        """Generate mock image embeddings."""
        embeddings = []
        for image in images:
            # Generate deterministic mock embedding based on image
            if isinstance(image, str):
                # Image path
                embedding = [hash(image) % 100 / 100.0 for _ in range(self.dimension)]
            else:
                # Image bytes
                embedding = [hash(str(image)) % 100 / 100.0 for _ in range(self.dimension)]
            embeddings.append(embedding)
        return embeddings
