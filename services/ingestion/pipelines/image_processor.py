"""
Image processing pipeline for captioning, embedding, and analysis.
"""

import asyncio
import aiofiles
from PIL import Image
import io
import json
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Processes images to extract captions, embeddings, and metadata."""
    
    def __init__(self, max_size: int = 1024, quality: int = 85):
        self.max_size = max_size
        self.quality = quality
    
    def process_image(self, image_path: str, **kwargs) -> Dict[str, Any]:
        """
        Process an image file synchronously.
        
        Args:
            image_path: Path to the image file
            **kwargs: Additional processing options
            
        Returns:
            Dictionary containing extracted data
        """
        try:
            logger.info(f"Processing image: {image_path}")
            
            # Load image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Extract metadata
            metadata = self._extract_metadata(pil_image, image_path)
            
            # Resize if needed
            resized_image = self._resize_image(pil_image)
            
            # Generate caption
            caption = self._generate_caption(resized_image)
            
            # Generate embedding
            embedding = self._generate_embedding(resized_image)
            
            # Extract colors
            colors = self._extract_colors(resized_image)
            
            # Detect objects (mock implementation)
            objects = self._detect_objects(resized_image)
            
            result = {
                'source_type': 'image',
                'source_path': image_path,
                'metadata': metadata,
                'caption': caption,
                'embedding': embedding,
                'colors': colors,
                'objects': objects,
                'processed_at': self._get_timestamp()
            }
            
            logger.info(f"Image processing completed: {image_path}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process image {image_path}: {e}")
            raise
    
    async def process_image_async(self, image_path: str, **kwargs) -> Dict[str, Any]:
        """
        Process an image file asynchronously.
        
        Args:
            image_path: Path to the image file
            **kwargs: Additional processing options
            
        Returns:
            Dictionary containing extracted data
        """
        try:
            logger.info(f"Processing image async: {image_path}")
            
            # Load image asynchronously
            async with aiofiles.open(image_path, 'rb') as f:
                image_data = await f.read()
            
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Extract metadata
            metadata = self._extract_metadata(pil_image, image_path)
            
            # Resize if needed
            resized_image = self._resize_image(pil_image)
            
            # Process image components concurrently
            caption_task = asyncio.create_task(self._generate_caption_async(resized_image))
            embedding_task = asyncio.create_task(self._generate_embedding_async(resized_image))
            colors_task = asyncio.create_task(self._extract_colors_async(resized_image))
            objects_task = asyncio.create_task(self._detect_objects_async(resized_image))
            
            # Wait for all tasks to complete
            caption, embedding, colors, objects = await asyncio.gather(
                caption_task, embedding_task, colors_task, objects_task
            )
            
            result = {
                'source_type': 'image',
                'source_path': image_path,
                'metadata': metadata,
                'caption': caption,
                'embedding': embedding,
                'colors': colors,
                'objects': objects,
                'processed_at': self._get_timestamp()
            }
            
            logger.info(f"Image processing completed: {image_path}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process image {image_path}: {e}")
            raise
    
    def _extract_metadata(self, image: Image.Image, image_path: str) -> Dict[str, Any]:
        """Extract metadata from image."""
        return {
            'filename': Path(image_path).name,
            'format': image.format,
            'mode': image.mode,
            'size': image.size,
            'width': image.width,
            'height': image.height,
            'has_transparency': image.mode in ('RGBA', 'LA'),
            'exif': self._extract_exif(image)
        }
    
    def _extract_exif(self, image: Image.Image) -> Dict[str, Any]:
        """Extract EXIF data from image."""
        try:
            exif_data = image._getexif()
            if exif_data:
                return {
                    'camera_make': exif_data.get(271, ''),
                    'camera_model': exif_data.get(272, ''),
                    'date_taken': exif_data.get(306, ''),
                    'orientation': exif_data.get(274, 1)
                }
        except Exception:
            pass
        return {}
    
    def _resize_image(self, image: Image.Image) -> Image.Image:
        """Resize image if it's too large."""
        if max(image.size) > self.max_size:
            ratio = self.max_size / max(image.size)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            return image.resize(new_size, Image.Resampling.LANCZOS)
        return image
    
    def _generate_caption(self, image: Image.Image) -> str:
        """Generate caption for image (mock implementation)."""
        # In a real implementation, this would use BLIP-2 or similar model
        return f"Image showing {image.width}x{image.height} pixels"
    
    async def _generate_caption_async(self, image: Image.Image) -> str:
        """Generate caption for image asynchronously."""
        # For now, use synchronous version
        # In a real implementation, this would use async captioning
        return self._generate_caption(image)
    
    def _generate_embedding(self, image: Image.Image) -> List[float]:
        """Generate embedding for image (mock implementation)."""
        # In a real implementation, this would use CLIP or similar model
        # Return a mock embedding vector
        return [0.1] * 512  # 512-dimensional embedding
    
    async def _generate_embedding_async(self, image: Image.Image) -> List[float]:
        """Generate embedding for image asynchronously."""
        # For now, use synchronous version
        # In a real implementation, this would use async embedding
        return self._generate_embedding(image)
    
    def _extract_colors(self, image: Image.Image) -> Dict[str, Any]:
        """Extract dominant colors from image."""
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize for faster processing
            small_image = image.resize((150, 150))
            
            # Get color palette
            palette = small_image.getcolors(maxcolors=256*256*256)
            if not palette:
                return {'dominant_colors': [], 'color_count': 0}
            
            # Sort by frequency
            palette.sort(key=lambda x: x[0], reverse=True)
            
            # Get top colors
            dominant_colors = []
            for count, color in palette[:10]:
                dominant_colors.append({
                    'color': color,
                    'count': count,
                    'percentage': (count / (150 * 150)) * 100
                })
            
            return {
                'dominant_colors': dominant_colors,
                'color_count': len(palette)
            }
            
        except Exception as e:
            logger.error(f"Failed to extract colors: {e}")
            return {'dominant_colors': [], 'color_count': 0}
    
    async def _extract_colors_async(self, image: Image.Image) -> Dict[str, Any]:
        """Extract dominant colors from image asynchronously."""
        # For now, use synchronous version
        # In a real implementation, this would use async color extraction
        return self._extract_colors(image)
    
    def _detect_objects(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Detect objects in image (mock implementation)."""
        # In a real implementation, this would use YOLO or similar model
        return [
            {
                'object': 'mock_object',
                'confidence': 0.8,
                'bbox': [0.1, 0.1, 0.9, 0.9]
            }
        ]
    
    async def _detect_objects_async(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Detect objects in image asynchronously."""
        # For now, use synchronous version
        # In a real implementation, this would use async object detection
        return self._detect_objects(image)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def process_image_batch(self, image_paths: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Process multiple images in batch."""
        results = []
        for image_path in image_paths:
            try:
                result = self.process_image(image_path, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process image {image_path}: {e}")
                results.append({
                    'source_type': 'image',
                    'source_path': image_path,
                    'error': str(e),
                    'processed_at': self._get_timestamp()
                })
        return results
    
    async def process_image_batch_async(self, image_paths: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Process multiple images in batch asynchronously."""
        tasks = []
        for image_path in image_paths:
            task = asyncio.create_task(self.process_image_async(image_path, **kwargs))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'source_type': 'image',
                    'source_path': image_paths[i],
                    'error': str(result),
                    'processed_at': self._get_timestamp()
                })
            else:
                processed_results.append(result)
        
        return processed_results
