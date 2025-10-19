"""
Retrieval service for similarity search and document retrieval.
"""

import asyncio
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import json
from datetime import datetime

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class Retriever:
    """Service for similarity search and document retrieval."""
    
    def __init__(self):
        self.vector_store = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the retriever with vector store."""
        try:
            # Initialize vector store
            await self._init_vector_store()
            
            self.initialized = True
            logger.info("Retriever initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize retriever: {e}")
            raise
    
    async def _init_vector_store(self):
        """Initialize vector store based on configuration."""
        try:
            if settings.VECTOR_DB_TYPE == "faiss":
                from faiss_index import FAISSIndex
                self.vector_store = FAISSIndex()
            elif settings.VECTOR_DB_TYPE == "pinecone":
                from vendor_adapters import PineconeAdapter
                self.vector_store = PineconeAdapter()
            elif settings.VECTOR_DB_TYPE == "weaviate":
                from vendor_adapters import WeaviateAdapter
                self.vector_store = WeaviateAdapter()
            else:
                raise ValueError(f"Unsupported vector DB type: {settings.VECTOR_DB_TYPE}")
            
            await self.vector_store.initialize()
            logger.info(f"Vector store initialized: {settings.VECTOR_DB_TYPE}")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    async def search_similar(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of similar documents with scores
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Searching for {top_k} similar documents")
            
            # Perform similarity search
            results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                filters=filters
            )
            
            logger.info(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise
    
    async def search_by_text(
        self,
        query_text: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for documents using text query.
        
        Args:
            query_text: Text query
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of similar documents with scores
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Searching by text: {query_text[:100]}...")
            
            # Generate query embedding
            from embedder import Embedder
            embedder = Embedder()
            await embedder.initialize()
            
            query_embedding = await embedder.embed_text([query_text])
            query_embedding = query_embedding[0]
            
            # Perform similarity search
            results = await self.search_similar(
                query_embedding=query_embedding,
                top_k=top_k,
                filters=filters
            )
            
            logger.info(f"Found {len(results)} documents for text query")
            return results
            
        except Exception as e:
            logger.error(f"Text search failed: {e}")
            raise
    
    async def search_by_image(
        self,
        image_path: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for documents using image query.
        
        Args:
            image_path: Path to query image
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of similar documents with scores
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Searching by image: {image_path}")
            
            # Generate query embedding
            from embedder import Embedder
            embedder = Embedder()
            await embedder.initialize()
            
            query_embedding = await embedder.embed_image([image_path])
            query_embedding = query_embedding[0]
            
            # Perform similarity search
            results = await self.search_similar(
                query_embedding=query_embedding,
                top_k=top_k,
                filters=filters
            )
            
            logger.info(f"Found {len(results)} documents for image query")
            return results
            
        except Exception as e:
            logger.error(f"Image search failed: {e}")
            raise
    
    async def search_multimodal(
        self,
        query_text: Optional[str] = None,
        query_image: Optional[str] = None,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for documents using multimodal query.
        
        Args:
            query_text: Optional text query
            query_image: Optional image query
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of similar documents with scores
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info("Performing multimodal search")
            
            # Generate query embeddings
            from embedder import Embedder
            embedder = Embedder()
            await embedder.initialize()
            
            query_embeddings = []
            
            if query_text:
                text_embedding = await embedder.embed_text([query_text])
                query_embeddings.append(text_embedding[0])
            
            if query_image:
                image_embedding = await embedder.embed_image([query_image])
                query_embeddings.append(image_embedding[0])
            
            if not query_embeddings:
                raise ValueError("At least one query (text or image) must be provided")
            
            # Combine embeddings if both are provided
            if len(query_embeddings) == 2:
                # Simple average combination
                combined_embedding = np.mean(query_embeddings, axis=0).tolist()
            else:
                combined_embedding = query_embeddings[0]
            
            # Perform similarity search
            results = await self.search_similar(
                query_embedding=combined_embedding,
                top_k=top_k,
                filters=filters
            )
            
            logger.info(f"Found {len(results)} documents for multimodal query")
            return results
            
        except Exception as e:
            logger.error(f"Multimodal search failed: {e}")
            raise
    
    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of documents to add
            embeddings: List of document embeddings
            
        Returns:
            List of document IDs
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Adding {len(documents)} documents to vector store")
            
            # Add documents to vector store
            doc_ids = await self.vector_store.add_documents(
                documents=documents,
                embeddings=embeddings
            )
            
            logger.info(f"Added {len(doc_ids)} documents to vector store")
            return doc_ids
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    async def update_document(
        self,
        doc_id: str,
        document: Dict[str, Any],
        embedding: List[float]
    ) -> bool:
        """
        Update a document in the vector store.
        
        Args:
            doc_id: Document ID to update
            document: Updated document
            embedding: Updated embedding
            
        Returns:
            Success status
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Updating document: {doc_id}")
            
            # Update document in vector store
            success = await self.vector_store.update_document(
                doc_id=doc_id,
                document=document,
                embedding=embedding
            )
            
            logger.info(f"Document update {'successful' if success else 'failed'}: {doc_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to update document {doc_id}: {e}")
            raise
    
    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the vector store.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            Success status
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Deleting document: {doc_id}")
            
            # Delete document from vector store
            success = await self.vector_store.delete_document(doc_id)
            
            logger.info(f"Document deletion {'successful' if success else 'failed'}: {doc_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            raise
    
    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document or None if not found
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Getting document: {doc_id}")
            
            # Get document from vector store
            document = await self.vector_store.get_document(doc_id)
            
            logger.info(f"Document {'found' if document else 'not found'}: {doc_id}")
            return document
            
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        try:
            if not self.initialized:
                await self.initialize()
            
            stats = await self.vector_store.get_stats()
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            raise
    
    async def close(self):
        """Close the retriever."""
        try:
            if self.vector_store:
                await self.vector_store.close()
            
            logger.info("Retriever closed")
            
        except Exception as e:
            logger.error(f"Error closing retriever: {e}")
