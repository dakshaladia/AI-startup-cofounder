"""
Vendor adapters for external vector databases (Pinecone, Weaviate).
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
import uuid

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class PineconeAdapter:
    """Pinecone vector database adapter."""
    
    def __init__(self):
        self.client = None
        self.index = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize Pinecone client and index."""
        try:
            import pinecone
            
            # Initialize Pinecone
            pinecone.init(
                api_key=settings.PINECONE_API_KEY,
                environment=settings.PINECONE_ENVIRONMENT
            )
            
            # Get or create index
            if settings.PINECONE_INDEX_NAME not in pinecone.list_indexes():
                pinecone.create_index(
                    name=settings.PINECONE_INDEX_NAME,
                    dimension=settings.TEXT_EMBEDDING_DIMENSION,
                    metric="cosine"
                )
            
            self.index = pinecone.Index(settings.PINECONE_INDEX_NAME)
            self.initialized = True
            
            logger.info(f"Pinecone adapter initialized with index {settings.PINECONE_INDEX_NAME}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone adapter: {e}")
            raise
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Prepare query
            query_params = {
                "vector": query_embedding,
                "top_k": top_k,
                "include_metadata": True
            }
            
            if filters:
                query_params["filter"] = filters
            
            # Perform search
            results = self.index.query(**query_params)
            
            # Format results
            formatted_results = []
            for match in results.matches:
                result = {
                    "doc_id": match.id,
                    "document": match.metadata,
                    "score": float(match.score),
                    "index": match.id
                }
                formatted_results.append(result)
            
            logger.info(f"Pinecone search returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Pinecone search failed: {e}")
            raise
    
    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> List[str]:
        """Add documents to Pinecone."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Prepare vectors
            vectors = []
            doc_ids = []
            
            for document, embedding in zip(documents, embeddings):
                doc_id = str(uuid.uuid4())
                doc_ids.append(doc_id)
                
                vector = {
                    "id": doc_id,
                    "values": embedding,
                    "metadata": document
                }
                vectors.append(vector)
            
            # Upsert vectors
            self.index.upsert(vectors=vectors)
            
            logger.info(f"Added {len(doc_ids)} documents to Pinecone")
            return doc_ids
            
        except Exception as e:
            logger.error(f"Failed to add documents to Pinecone: {e}")
            raise
    
    async def update_document(
        self,
        doc_id: str,
        document: Dict[str, Any],
        embedding: List[float]
    ) -> bool:
        """Update a document in Pinecone."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Update vector
            vector = {
                "id": doc_id,
                "values": embedding,
                "metadata": document
            }
            
            self.index.upsert(vectors=[vector])
            
            logger.info(f"Updated document {doc_id} in Pinecone")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document {doc_id} in Pinecone: {e}")
            raise
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document from Pinecone."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Delete vector
            self.index.delete(ids=[doc_id])
            
            logger.info(f"Deleted document {doc_id} from Pinecone")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id} from Pinecone: {e}")
            raise
    
    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document from Pinecone."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Fetch vector
            results = self.index.fetch(ids=[doc_id])
            
            if doc_id in results.vectors:
                vector = results.vectors[doc_id]
                return vector.metadata
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document {doc_id} from Pinecone: {e}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get Pinecone index statistics."""
        try:
            if not self.initialized:
                await self.initialize()
            
            stats = self.index.describe_index_stats()
            
            return {
                "total_documents": stats.total_vector_count,
                "index_size": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_type": "Pinecone"
            }
            
        except Exception as e:
            logger.error(f"Failed to get Pinecone stats: {e}")
            raise
    
    async def close(self):
        """Close Pinecone connection."""
        try:
            logger.info("Pinecone adapter closed")
            
        except Exception as e:
            logger.error(f"Error closing Pinecone adapter: {e}")


class WeaviateAdapter:
    """Weaviate vector database adapter."""
    
    def __init__(self):
        self.client = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize Weaviate client."""
        try:
            import weaviate
            
            # Initialize Weaviate client
            self.client = weaviate.Client(
                url=settings.WEAVIATE_URL,
                api_key=settings.WEAVIATE_API_KEY
            )
            
            # Test connection
            self.client.is_ready()
            
            self.initialized = True
            logger.info(f"Weaviate adapter initialized with URL {settings.WEAVIATE_URL}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Weaviate adapter: {e}")
            raise
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Prepare query
            query = {
                "vector": query_embedding,
                "limit": top_k
            }
            
            if filters:
                query["where"] = filters
            
            # Perform search
            results = self.client.query.get("Document", ["*"]).with_near_vector(query).do()
            
            # Format results
            formatted_results = []
            for result in results["data"]["Get"]["Document"]:
                formatted_result = {
                    "doc_id": result["_id"],
                    "document": result,
                    "score": result.get("_additional", {}).get("distance", 0.0),
                    "index": result["_id"]
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"Weaviate search returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Weaviate search failed: {e}")
            raise
    
    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> List[str]:
        """Add documents to Weaviate."""
        try:
            if not self.initialized:
                await self.initialize()
            
            doc_ids = []
            
            for document, embedding in zip(documents, embeddings):
                doc_id = str(uuid.uuid4())
                doc_ids.append(doc_id)
                
                # Add document to Weaviate
                self.client.data_object.create(
                    data_object=document,
                    class_name="Document",
                    vector=embedding
                )
            
            logger.info(f"Added {len(doc_ids)} documents to Weaviate")
            return doc_ids
            
        except Exception as e:
            logger.error(f"Failed to add documents to Weaviate: {e}")
            raise
    
    async def update_document(
        self,
        doc_id: str,
        document: Dict[str, Any],
        embedding: List[float]
    ) -> bool:
        """Update a document in Weaviate."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Update document in Weaviate
            self.client.data_object.update(
                data_object=document,
                class_name="Document",
                uuid=doc_id,
                vector=embedding
            )
            
            logger.info(f"Updated document {doc_id} in Weaviate")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document {doc_id} in Weaviate: {e}")
            raise
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document from Weaviate."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Delete document from Weaviate
            self.client.data_object.delete(
                class_name="Document",
                uuid=doc_id
            )
            
            logger.info(f"Deleted document {doc_id} from Weaviate")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id} from Weaviate: {e}")
            raise
    
    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document from Weaviate."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Get document from Weaviate
            result = self.client.data_object.get_by_id(
                uuid=doc_id,
                class_name="Document"
            )
            
            return result if result else None
            
        except Exception as e:
            logger.error(f"Failed to get document {doc_id} from Weaviate: {e}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get Weaviate statistics."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Get schema info
            schema = self.client.schema.get()
            
            return {
                "total_documents": 0,  # Would need to query for actual count
                "index_size": 0,
                "dimension": 0,
                "index_type": "Weaviate"
            }
            
        except Exception as e:
            logger.error(f"Failed to get Weaviate stats: {e}")
            raise
    
    async def close(self):
        """Close Weaviate connection."""
        try:
            logger.info("Weaviate adapter closed")
            
        except Exception as e:
            logger.error(f"Error closing Weaviate adapter: {e}")
