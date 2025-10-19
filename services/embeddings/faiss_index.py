"""
FAISS index implementation for local vector storage.
"""

import asyncio
import numpy as np
import faiss
import json
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class FAISSIndex:
    """FAISS-based vector index for local development."""
    
    def __init__(self):
        self.index = None
        self.dimension = None
        self.documents = {}
        self.embeddings = []
        self.initialized = False
    
    async def initialize(self):
        """Initialize the FAISS index."""
        try:
            # Get dimension from settings
            self.dimension = settings.TEXT_EMBEDDING_DIMENSION
            
            # Create or load index
            index_path = Path(settings.VECTOR_DB_PATH)
            if index_path.exists():
                await self._load_index(index_path)
            else:
                await self._create_index()
            
            self.initialized = True
            logger.info(f"FAISS index initialized with dimension {self.dimension}")
            
        except Exception as e:
            logger.error(f"Failed to initialize FAISS index: {e}")
            raise
    
    async def _create_index(self):
        """Create a new FAISS index."""
        try:
            # Create FAISS index
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
            
            # Initialize empty data structures
            self.documents = {}
            self.embeddings = []
            
            logger.info("Created new FAISS index")
            
        except Exception as e:
            logger.error(f"Failed to create FAISS index: {e}")
            raise
    
    async def _load_index(self, index_path: Path):
        """Load existing FAISS index."""
        try:
            # Load index file
            index_file = index_path / "index.faiss"
            if index_file.exists():
                self.index = faiss.read_index(str(index_file))
                self.dimension = self.index.d
            else:
                await self._create_index()
                return
            
            # Load documents
            docs_file = index_path / "documents.json"
            if docs_file.exists():
                with open(docs_file, 'r') as f:
                    self.documents = json.load(f)
            
            # Load embeddings
            embeddings_file = index_path / "embeddings.pkl"
            if embeddings_file.exists():
                with open(embeddings_file, 'rb') as f:
                    self.embeddings = pickle.load(f)
            
            logger.info(f"Loaded FAISS index with {len(self.documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            raise
    
    async def _save_index(self, index_path: Path):
        """Save FAISS index to disk."""
        try:
            # Create directory if it doesn't exist
            index_path.mkdir(parents=True, exist_ok=True)
            
            # Save index
            index_file = index_path / "index.faiss"
            faiss.write_index(self.index, str(index_file))
            
            # Save documents
            docs_file = index_path / "documents.json"
            with open(docs_file, 'w') as f:
                json.dump(self.documents, f, indent=2)
            
            # Save embeddings
            embeddings_file = index_path / "embeddings.pkl"
            with open(embeddings_file, 'wb') as f:
                pickle.dump(self.embeddings, f)
            
            logger.info(f"Saved FAISS index to {index_path}")
            
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")
            raise
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
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
            
            # Convert query to numpy array
            query_vector = np.array([query_embedding], dtype=np.float32)
            
            # Search index
            scores, indices = self.index.search(query_vector, top_k)
            
            # Get results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:  # No more results
                    break
                
                # Get document
                doc_id = list(self.documents.keys())[idx]
                document = self.documents[doc_id]
                
                # Apply filters if provided
                if filters and not self._matches_filters(document, filters):
                    continue
                
                result = {
                    "doc_id": doc_id,
                    "document": document,
                    "score": float(score),
                    "index": int(idx)
                }
                results.append(result)
            
            logger.info(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def _matches_filters(self, document: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if document matches filters."""
        try:
            for key, value in filters.items():
                if key not in document:
                    return False
                
                if isinstance(value, list):
                    if document[key] not in value:
                        return False
                elif isinstance(value, dict):
                    if not self._matches_filters(document[key], value):
                        return False
                else:
                    if document[key] != value:
                        return False
            
            return True
            
        except Exception:
            return False
    
    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> List[str]:
        """
        Add documents to the index.
        
        Args:
            documents: List of documents to add
            embeddings: List of document embeddings
            
        Returns:
            List of document IDs
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            doc_ids = []
            
            for document, embedding in zip(documents, embeddings):
                # Generate document ID
                doc_id = str(uuid.uuid4())
                doc_ids.append(doc_id)
                
                # Add to documents
                self.documents[doc_id] = document
                
                # Add to embeddings
                self.embeddings.append(embedding)
            
            # Update FAISS index
            if self.embeddings:
                embeddings_array = np.array(self.embeddings, dtype=np.float32)
                self.index.add(embeddings_array)
            
            # Save index
            index_path = Path(settings.VECTOR_DB_PATH)
            await self._save_index(index_path)
            
            logger.info(f"Added {len(doc_ids)} documents to FAISS index")
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
        Update a document in the index.
        
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
            
            if doc_id not in self.documents:
                logger.warning(f"Document {doc_id} not found for update")
                return False
            
            # Update document
            self.documents[doc_id] = document
            
            # Update embedding
            doc_index = list(self.documents.keys()).index(doc_id)
            self.embeddings[doc_index] = embedding
            
            # Rebuild index
            if self.embeddings:
                embeddings_array = np.array(self.embeddings, dtype=np.float32)
                self.index.reset()
                self.index.add(embeddings_array)
            
            # Save index
            index_path = Path(settings.VECTOR_DB_PATH)
            await self._save_index(index_path)
            
            logger.info(f"Updated document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document {doc_id}: {e}")
            raise
    
    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the index.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            Success status
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            if doc_id not in self.documents:
                logger.warning(f"Document {doc_id} not found for deletion")
                return False
            
            # Get document index
            doc_index = list(self.documents.keys()).index(doc_id)
            
            # Remove document and embedding
            del self.documents[doc_id]
            del self.embeddings[doc_index]
            
            # Rebuild index
            if self.embeddings:
                embeddings_array = np.array(self.embeddings, dtype=np.float32)
                self.index.reset()
                self.index.add(embeddings_array)
            else:
                self.index.reset()
            
            # Save index
            index_path = Path(settings.VECTOR_DB_PATH)
            await self._save_index(index_path)
            
            logger.info(f"Deleted document {doc_id}")
            return True
            
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
            
            document = self.documents.get(doc_id)
            return document
            
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        try:
            if not self.initialized:
                await self.initialize()
            
            stats = {
                "total_documents": len(self.documents),
                "index_size": self.index.ntotal if self.index else 0,
                "dimension": self.dimension,
                "index_type": "FAISS"
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            raise
    
    async def close(self):
        """Close the FAISS index."""
        try:
            # Save index before closing
            if self.initialized:
                index_path = Path(settings.VECTOR_DB_PATH)
                await self._save_index(index_path)
            
            logger.info("FAISS index closed")
            
        except Exception as e:
            logger.error(f"Error closing FAISS index: {e}")
