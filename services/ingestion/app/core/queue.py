"""
Queue management for background tasks using Redis.
"""

import asyncio
import json
from typing import Any, Dict, Optional
import redis.asyncio as redis
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class QueueManager:
    """Redis-based queue manager for background tasks."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.connection_pool: Optional[redis.ConnectionPool] = None
    
    async def initialize(self):
        """Initialize Redis connection."""
        try:
            self.connection_pool = redis.ConnectionPool.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            self.redis_client = redis.Redis(connection_pool=self.connection_pool)
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
        if self.connection_pool:
            await self.connection_pool.disconnect()
        logger.info("Redis connection closed")
    
    async def health_check(self):
        """Check if queue is healthy."""
        try:
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Queue health check failed: {e}")
            return False
    
    async def enqueue_task(
        self,
        queue_name: str,
        task_name: str,
        task_data: Dict[str, Any],
        priority: int = 0,
        delay: int = 0
    ) -> str:
        """
        Enqueue a background task.
        
        Args:
            queue_name: Name of the queue
            task_name: Name of the task function
            task_data: Task parameters
            priority: Task priority (higher = more priority)
            delay: Delay in seconds before task execution
            
        Returns:
            Task ID
        """
        if not self.redis_client:
            raise RuntimeError("Queue not initialized")
        
        task_id = f"{task_name}_{asyncio.get_event_loop().time()}"
        task_payload = {
            "id": task_id,
            "name": task_name,
            "data": task_data,
            "priority": priority,
            "created_at": asyncio.get_event_loop().time()
        }
        
        # Add to queue with delay if specified
        if delay > 0:
            await self.redis_client.zadd(
                f"{queue_name}:delayed",
                {json.dumps(task_payload): asyncio.get_event_loop().time() + delay}
            )
        else:
            await self.redis_client.lpush(
                f"{queue_name}:pending",
                json.dumps(task_payload)
            )
        
        logger.info(f"Enqueued task {task_name} with ID {task_id}")
        return task_id
    
    async def dequeue_task(self, queue_name: str) -> Optional[Dict[str, Any]]:
        """
        Dequeue a task from the queue.
        
        Args:
            queue_name: Name of the queue
            
        Returns:
            Task payload or None if no tasks available
        """
        if not self.redis_client:
            raise RuntimeError("Queue not initialized")
        
        # Check for delayed tasks that are ready
        now = asyncio.get_event_loop().time()
        ready_tasks = await self.redis_client.zrangebyscore(
            f"{queue_name}:delayed",
            0,
            now,
            start=0,
            num=1
        )
        
        if ready_tasks:
            task_payload = json.loads(ready_tasks[0])
            await self.redis_client.zrem(f"{queue_name}:delayed", ready_tasks[0])
            await self.redis_client.lpush(f"{queue_name}:pending", ready_tasks[0])
        
        # Get next pending task
        task_data = await self.redis_client.brpop(f"{queue_name}:pending", timeout=1)
        if task_data:
            return json.loads(task_data[1])
        
        return None
    
    async def get_queue_stats(self, queue_name: str) -> Dict[str, int]:
        """
        Get queue statistics.
        
        Args:
            queue_name: Name of the queue
            
        Returns:
            Dictionary with queue statistics
        """
        if not self.redis_client:
            raise RuntimeError("Queue not initialized")
        
        pending = await self.redis_client.llen(f"{queue_name}:pending")
        delayed = await self.redis_client.zcard(f"{queue_name}:delayed")
        processing = await self.redis_client.llen(f"{queue_name}:processing")
        completed = await self.redis_client.llen(f"{queue_name}:completed")
        failed = await self.redis_client.llen(f"{queue_name}:failed")
        
        return {
            "pending": pending,
            "delayed": delayed,
            "processing": processing,
            "completed": completed,
            "failed": failed
        }
    
    async def mark_task_completed(self, queue_name: str, task_id: str):
        """Mark a task as completed."""
        if not self.redis_client:
            raise RuntimeError("Queue not initialized")
        
        await self.redis_client.lpush(f"{queue_name}:completed", task_id)
        await self.redis_client.lrem(f"{queue_name}:processing", 1, task_id)
    
    async def mark_task_failed(self, queue_name: str, task_id: str, error: str):
        """Mark a task as failed."""
        if not self.redis_client:
            raise RuntimeError("Queue not initialized")
        
        failed_task = {"id": task_id, "error": error, "failed_at": asyncio.get_event_loop().time()}
        await self.redis_client.lpush(f"{queue_name}:failed", json.dumps(failed_task))
        await self.redis_client.lrem(f"{queue_name}:processing", 1, task_id)
