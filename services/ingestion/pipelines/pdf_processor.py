"""
PDF processing pipeline for extracting text, images, and metadata.
"""

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import json
from typing import List, Dict, Any, Optional, Tuple
import asyncio
import aiofiles
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Processes PDF files to extract text, images, and metadata."""
    
    def __init__(self, ocr_language: str = 'eng', chunk_size: int = 500, chunk_overlap: int = 50):
        self.ocr_language = ocr_language
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_pdf(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """
        Process a PDF file synchronously.
        
        Args:
            pdf_path: Path to the PDF file
            **kwargs: Additional processing options
            
        Returns:
            Dictionary containing extracted data
        """
        try:
            logger.info(f"Processing PDF: {pdf_path}")
            
            # Open PDF document
            doc = fitz.open(pdf_path)
            
            # Extract metadata
            metadata = self._extract_metadata(doc)
            
            # Process each page
            pages = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_data = self._process_page(page, page_num + 1)
                pages.append(page_data)
            
            # Close document
            doc.close()
            
            # Create chunks
            chunks = self._create_chunks(pages)
            
            result = {
                'source_type': 'pdf',
                'source_path': pdf_path,
                'metadata': metadata,
                'pages': pages,
                'chunks': chunks,
                'total_pages': len(pages),
                'total_chunks': len(chunks)
            }
            
            logger.info(f"PDF processing completed: {len(chunks)} chunks created")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process PDF {pdf_path}: {e}")
            raise
    
    async def process_pdf_async(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """
        Process a PDF file asynchronously.
        
        Args:
            pdf_path: Path to the PDF file
            **kwargs: Additional processing options
            
        Returns:
            Dictionary containing extracted data
        """
        try:
            logger.info(f"Processing PDF async: {pdf_path}")
            
            # Open PDF document
            doc = fitz.open(pdf_path)
            
            # Extract metadata
            metadata = self._extract_metadata(doc)
            
            # Process pages concurrently
            page_tasks = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                task = asyncio.create_task(self._process_page_async(page, page_num + 1))
                page_tasks.append(task)
            
            pages = await asyncio.gather(*page_tasks)
            
            # Close document
            doc.close()
            
            # Create chunks
            chunks = self._create_chunks(pages)
            
            result = {
                'source_type': 'pdf',
                'source_path': pdf_path,
                'metadata': metadata,
                'pages': pages,
                'chunks': chunks,
                'total_pages': len(pages),
                'total_chunks': len(chunks)
            }
            
            logger.info(f"PDF processing completed: {len(chunks)} chunks created")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process PDF {pdf_path}: {e}")
            raise
    
    def _extract_metadata(self, doc: fitz.Document) -> Dict[str, Any]:
        """Extract metadata from PDF document."""
        metadata = doc.metadata
        return {
            'title': metadata.get('title', ''),
            'author': metadata.get('author', ''),
            'subject': metadata.get('subject', ''),
            'creator': metadata.get('creator', ''),
            'producer': metadata.get('producer', ''),
            'creation_date': metadata.get('creationDate', ''),
            'modification_date': metadata.get('modDate', ''),
            'page_count': len(doc),
            'file_size': doc.page_count  # This would be actual file size in real implementation
        }
    
    def _process_page(self, page: fitz.Page, page_num: int) -> Dict[str, Any]:
        """Process a single PDF page."""
        try:
            # Extract text
            text = page.get_text()
            
            # Extract images
            images = self._extract_images(page, page_num)
            
            # Run OCR on page if needed
            ocr_text = self._run_ocr_on_page(page)
            
            return {
                'page_number': page_num,
                'text': text,
                'ocr_text': ocr_text,
                'images': images,
                'image_count': len(images),
                'text_length': len(text),
                'has_images': len(images) > 0
            }
            
        except Exception as e:
            logger.error(f"Failed to process page {page_num}: {e}")
            return {
                'page_number': page_num,
                'text': '',
                'ocr_text': '',
                'images': [],
                'image_count': 0,
                'text_length': 0,
                'has_images': False,
                'error': str(e)
            }
    
    async def _process_page_async(self, page: fitz.Page, page_num: int) -> Dict[str, Any]:
        """Process a single PDF page asynchronously."""
        try:
            # Extract text
            text = page.get_text()
            
            # Extract images
            images = await self._extract_images_async(page, page_num)
            
            # Run OCR on page if needed
            ocr_text = await self._run_ocr_on_page_async(page)
            
            return {
                'page_number': page_num,
                'text': text,
                'ocr_text': ocr_text,
                'images': images,
                'image_count': len(images),
                'text_length': len(text),
                'has_images': len(images) > 0
            }
            
        except Exception as e:
            logger.error(f"Failed to process page {page_num}: {e}")
            return {
                'page_number': page_num,
                'text': '',
                'ocr_text': '',
                'images': [],
                'image_count': 0,
                'text_length': 0,
                'has_images': False,
                'error': str(e)
            }
    
    def _extract_images(self, page: fitz.Page, page_num: int) -> List[Dict[str, Any]]:
        """Extract images from a PDF page."""
        images = []
        try:
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    pix = fitz.Pixmap(page.parent, xref)
                    
                    # Convert to PIL Image
                    img_data = pix.tobytes("png")
                    pil_image = Image.open(io.BytesIO(img_data))
                    
                    # Generate caption (mock implementation)
                    caption = self._generate_image_caption(pil_image)
                    
                    image_data = {
                        'image_index': img_index,
                        'page_number': page_num,
                        'width': pil_image.width,
                        'height': pil_image.height,
                        'format': pil_image.format,
                        'caption': caption,
                        'data': img_data  # Base64 encoded in real implementation
                    }
                    
                    images.append(image_data)
                    pix = None  # Free memory
                    
                except Exception as e:
                    logger.error(f"Failed to extract image {img_index} from page {page_num}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Failed to extract images from page {page_num}: {e}")
        
        return images
    
    async def _extract_images_async(self, page: fitz.Page, page_num: int) -> List[Dict[str, Any]]:
        """Extract images from a PDF page asynchronously."""
        # For now, use synchronous version
        # In a real implementation, this would use async image processing
        return self._extract_images(page, page_num)
    
    def _run_ocr_on_page(self, page: fitz.Page) -> str:
        """Run OCR on a PDF page."""
        try:
            # Convert page to image
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            pil_image = Image.open(io.BytesIO(img_data))
            
            # Run OCR
            ocr_text = pytesseract.image_to_string(pil_image, lang=self.ocr_language)
            
            return ocr_text.strip()
            
        except Exception as e:
            logger.error(f"OCR failed on page: {e}")
            return ""
    
    async def _run_ocr_on_page_async(self, page: fitz.Page) -> str:
        """Run OCR on a PDF page asynchronously."""
        # For now, use synchronous version
        # In a real implementation, this would use async OCR
        return self._run_ocr_on_page(page)
    
    def _generate_image_caption(self, image: Image.Image) -> str:
        """Generate caption for an image (mock implementation)."""
        # In a real implementation, this would use BLIP-2 or similar model
        return f"Image with dimensions {image.width}x{image.height}"
    
    def _create_chunks(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create text chunks from processed pages."""
        chunks = []
        
        for page in pages:
            # Combine text and OCR text
            combined_text = f"{page['text']}\n{page['ocr_text']}".strip()
            
            if not combined_text:
                continue
            
            # Split into chunks
            page_chunks = self._split_text_into_chunks(
                combined_text,
                page['page_number'],
                self.chunk_size,
                self.chunk_overlap
            )
            
            chunks.extend(page_chunks)
        
        return chunks
    
    def _split_text_into_chunks(
        self,
        text: str,
        page_number: int,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks."""
        chunks = []
        words = text.split()
        
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            
            chunk = {
                'text': chunk_text,
                'page_number': page_number,
                'chunk_index': len(chunks),
                'start_word': start,
                'end_word': end,
                'word_count': len(chunk_words),
                'char_count': len(chunk_text)
            }
            
            chunks.append(chunk)
            
            # Move start position with overlap
            start = end - chunk_overlap
            if start >= len(words):
                break
        
        return chunks
