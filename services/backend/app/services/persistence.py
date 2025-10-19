"""
Persistence service for database and vector store operations.
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from app.models.idea import IdeaSnapshot
from app.models.feedback import Feedback
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class PersistenceService:
    """Service for persisting data to database and vector store."""
    
    def __init__(self):
        self.db_client = None
        self.vector_client = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize database and vector store connections."""
        try:
            # Initialize database connection
            await self._init_database()
            
            # Initialize vector store
            await self._init_vector_store()
            
            self.initialized = True
            logger.info("Persistence service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize persistence service: {e}")
            raise
    
    async def close(self):
        """Close all connections."""
        try:
            if self.db_client:
                await self.db_client.close()
            if self.vector_client:
                await self.vector_client.close()
            logger.info("Persistence service connections closed")
        except Exception as e:
            logger.error(f"Error closing persistence service: {e}")
    
    async def health_check(self):
        """Check if persistence service is healthy."""
        try:
            # Check database connection
            if self.db_client:
                await self.db_client.execute("SELECT 1")
            
            # Check vector store connection
            if self.vector_client:
                await self.vector_client.ping()
            
            return True
        except Exception as e:
            logger.error(f"Persistence health check failed: {e}")
            return False
    
    # Idea operations
    
    async def save_idea_snapshot(self, idea: IdeaSnapshot) -> IdeaSnapshot:
        """Save an idea snapshot to the database."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Save to database
            idea_id = await self._save_idea_to_db(idea)
            idea.id = idea_id
            
            # Save to vector store
            await self._save_idea_to_vector(idea)
            
            logger.info(f"Idea snapshot saved: {idea_id}")
            return idea
            
        except Exception as e:
            logger.error(f"Failed to save idea snapshot: {e}")
            raise
    
    async def get_idea(self, idea_id: str) -> Optional[IdeaSnapshot]:
        """Get an idea by ID."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Get from database
            idea_data = await self._get_idea_from_db(idea_id)
            if not idea_data:
                return None
            
            return IdeaSnapshot(**idea_data)
            
        except Exception as e:
            logger.error(f"Failed to get idea {idea_id}: {e}")
            raise
    
    async def get_ideas(
        self,
        page: int = 1,
        page_size: int = 10,
        topic_filter: Optional[str] = None,
        min_score: Optional[float] = None
    ) -> List[IdeaSnapshot]:
        """Get paginated list of ideas with optional filtering."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Get from database
            ideas_data = await self._get_ideas_from_db(
                page=page,
                page_size=page_size,
                topic_filter=topic_filter,
                min_score=min_score
            )
            
            return [IdeaSnapshot(**idea_data) for idea_data in ideas_data]
            
        except Exception as e:
            logger.error(f"Failed to get ideas: {e}")
            raise
    
    async def delete_idea(self, idea_id: str) -> bool:
        """Delete an idea by ID."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Delete from database
            success = await self._delete_idea_from_db(idea_id)
            
            # Delete from vector store
            if success:
                await self._delete_idea_from_vector(idea_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete idea {idea_id}: {e}")
            raise
    
    # Feedback operations
    
    async def save_feedback(self, feedback: Feedback) -> Feedback:
        """Save feedback to the database."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Save to database
            feedback_id = await self._save_feedback_to_db(feedback)
            feedback.id = feedback_id
            
            logger.info(f"Feedback saved: {feedback_id}")
            return feedback
            
        except Exception as e:
            logger.error(f"Failed to save feedback: {e}")
            raise
    
    async def get_feedback(self, feedback_id: str) -> Optional[Feedback]:
        """Get feedback by ID."""
        try:
            if not self.initialized:
                await self.initialize()
            
            feedback_data = await self._get_feedback_from_db(feedback_id)
            if not feedback_data:
                return None
            
            return Feedback(**feedback_data)
            
        except Exception as e:
            logger.error(f"Failed to get feedback {feedback_id}: {e}")
            raise
    
    async def get_feedback_for_idea(
        self,
        idea_id: str,
        page: int = 1,
        page_size: int = 10,
        feedback_type: Optional[str] = None
    ) -> List[Feedback]:
        """Get feedback for a specific idea."""
        try:
            if not self.initialized:
                await self.initialize()
            
            feedback_data = await self._get_feedback_for_idea_from_db(
                idea_id=idea_id,
                page=page,
                page_size=page_size,
                feedback_type=feedback_type
            )
            
            return [Feedback(**feedback) for feedback in feedback_data]
            
        except Exception as e:
            logger.error(f"Failed to get feedback for idea {idea_id}: {e}")
            raise
    
    async def update_feedback(self, feedback: Feedback) -> bool:
        """Update an existing feedback item."""
        try:
            if not self.initialized:
                await self.initialize()
            
            success = await self._update_feedback_in_db(feedback)
            return success
            
        except Exception as e:
            logger.error(f"Failed to update feedback: {e}")
            raise
    
    async def delete_feedback(self, feedback_id: str) -> bool:
        """Delete a feedback item."""
        try:
            if not self.initialized:
                await self.initialize()
            
            success = await self._delete_feedback_from_db(feedback_id)
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete feedback {feedback_id}: {e}")
            raise
    
    # Vector store operations
    
    async def query_docs(
        self,
        query_embedding: List[float],
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Query documents from vector store."""
        try:
            if not self.initialized:
                await self.initialize()
            
            results = await self._query_vector_store(
                query_embedding=query_embedding,
                filters=filters,
                top_k=top_k
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to query documents: {e}")
            raise
    
    async def upsert_doc(self, doc: Dict[str, Any]) -> str:
        """Upsert a document to vector store."""
        try:
            if not self.initialized:
                await self.initialize()
            
            doc_id = await self._upsert_to_vector_store(doc)
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to upsert document: {e}")
            raise
    
    # Private methods for database operations
    
    async def _init_database(self):
        """Initialize database connection."""
        # Mock implementation - would normally use asyncpg or similar
        self.db_client = MockDatabaseClient()
        await self.db_client.connect()
    
    async def _init_vector_store(self):
        """Initialize vector store connection."""
        if settings.VECTOR_DB_TYPE == "faiss":
            self.vector_client = MockFAISSClient()
        elif settings.VECTOR_DB_TYPE == "pinecone":
            self.vector_client = MockPineconeClient()
        elif settings.VECTOR_DB_TYPE == "weaviate":
            self.vector_client = MockWeaviateClient()
        else:
            raise ValueError(f"Unsupported vector DB type: {settings.VECTOR_DB_TYPE}")
        
        await self.vector_client.initialize()
    
    async def _save_idea_to_db(self, idea: IdeaSnapshot) -> str:
        """Save idea to database."""
        # Mock implementation
        return idea.id
    
    async def _get_idea_from_db(self, idea_id: str) -> Optional[Dict[str, Any]]:
        """Get idea from database."""
        # Mock implementation
        return None
    
    async def _get_ideas_from_db(
        self,
        page: int,
        page_size: int,
        topic_filter: Optional[str] = None,
        min_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Get ideas from database."""
        # Mock implementation
        return []
    
    async def _delete_idea_from_db(self, idea_id: str) -> bool:
        """Delete idea from database."""
        # Mock implementation
        return True
    
    async def _save_feedback_to_db(self, feedback: Feedback) -> str:
        """Save feedback to database."""
        # Mock implementation
        return feedback.id
    
    async def _get_feedback_from_db(self, feedback_id: str) -> Optional[Dict[str, Any]]:
        """Get feedback from database."""
        # Mock implementation
        return None
    
    async def _get_feedback_for_idea_from_db(
        self,
        idea_id: str,
        page: int,
        page_size: int,
        feedback_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get feedback for idea from database."""
        # Mock implementation
        return []
    
    async def _update_feedback_in_db(self, feedback: Feedback) -> bool:
        """Update feedback in database."""
        # Mock implementation
        return True
    
    async def _delete_feedback_from_db(self, feedback_id: str) -> bool:
        """Delete feedback from database."""
        # Mock implementation
        return True
    
    async def _save_idea_to_vector(self, idea: IdeaSnapshot):
        """Save idea to vector store."""
        # Mock implementation
        pass
    
    async def _delete_idea_from_vector(self, idea_id: str):
        """Delete idea from vector store."""
        # Mock implementation
        pass
    
    async def _query_vector_store(
        self,
        query_embedding: List[float],
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Query vector store."""
        # Mock implementation
        return []
    
    async def _upsert_to_vector_store(self, doc: Dict[str, Any]) -> str:
        """Upsert document to vector store."""
        # Mock implementation
        return "mock_doc_id"


# Mock clients for development
class MockDatabaseClient:
    async def connect(self):
        pass
    
    async def close(self):
        pass
    
    async def execute(self, query: str):
        pass


class MockFAISSClient:
    async def initialize(self):
        pass
    
    async def close(self):
        pass
    
    async def ping(self):
        pass


class MockPineconeClient:
    async def initialize(self):
        pass
    
    async def close(self):
        pass
    
    async def ping(self):
        pass


class MockWeaviateClient:
    async def initialize(self):
        pass
    
    async def close(self):
        pass
    
    async def ping(self):
        pass
