"""
Background worker for processing ingestion tasks.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import traceback

from app.core.queue import QueueManager
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class IngestWorker:
    """Background worker for processing ingestion tasks."""
    
    def __init__(self, worker_id: int, queue_name: str = 'ingestion', timeout: int = 300):
        self.worker_id = worker_id
        self.queue_name = queue_name
        self.timeout = timeout
        self.queue_manager = QueueManager()
        self.running = False
    
    async def start(self):
        """Start the worker."""
        try:
            logger.info(f"Starting ingestion worker {self.worker_id}")
            self.running = True
            
            # Initialize queue manager
            await self.queue_manager.initialize()
            
            # Start processing loop
            await self._process_loop()
            
        except Exception as e:
            logger.error(f"Worker {self.worker_id} failed to start: {e}")
            raise
        finally:
            await self.queue_manager.close()
    
    async def stop(self):
        """Stop the worker."""
        logger.info(f"Stopping ingestion worker {self.worker_id}")
        self.running = False
    
    async def _process_loop(self):
        """Main processing loop."""
        while self.running:
            try:
                # Get next task from queue
                task = await self.queue_manager.dequeue_task(self.queue_name)
                
                if task:
                    await self._process_task(task)
                else:
                    # No tasks available, wait a bit
                    await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Worker {self.worker_id} error in processing loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _process_task(self, task: Dict[str, Any]):
        """Process a single task."""
        task_id = task.get('id')
        task_name = task.get('name')
        task_data = task.get('data', {})
        
        try:
            logger.info(f"Worker {self.worker_id} processing task {task_id}: {task_name}")
            
            # Mark task as processing
            await self.queue_manager.redis_client.lpush(f"{self.queue_name}:processing", task_id)
            
            # Process based on task type
            if task_name == 'process_pdf':
                result = await self._process_pdf_task(task_data)
            elif task_name == 'process_image':
                result = await self._process_image_task(task_data)
            elif task_name == 'process_news':
                result = await self._process_news_task(task_data)
            elif task_name == 'process_job_post':
                result = await self._process_job_post_task(task_data)
            else:
                raise ValueError(f"Unknown task type: {task_name}")
            
            # Mark task as completed
            await self.queue_manager.mark_task_completed(self.queue_name, task_id)
            
            logger.info(f"Worker {self.worker_id} completed task {task_id}")
            
        except Exception as e:
            logger.error(f"Worker {self.worker_id} failed to process task {task_id}: {e}")
            logger.error(traceback.format_exc())
            
            # Mark task as failed
            await self.queue_manager.mark_task_failed(self.queue_name, task_id, str(e))
    
    async def _process_pdf_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process PDF task."""
        from pipelines.pdf_processor import PDFProcessor
        
        pdf_path = task_data.get('pdf_path')
        if not pdf_path:
            raise ValueError("PDF path not provided")
        
        processor = PDFProcessor()
        result = await processor.process_pdf_async(pdf_path, **task_data.get('options', {}))
        
        # Save result to database/vector store
        await self._save_result(result)
        
        return result
    
    async def _process_image_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process image task."""
        from pipelines.image_processor import ImageProcessor
        
        image_path = task_data.get('image_path')
        if not image_path:
            raise ValueError("Image path not provided")
        
        processor = ImageProcessor()
        result = await processor.process_image_async(image_path, **task_data.get('options', {}))
        
        # Save result to database/vector store
        await self._save_result(result)
        
        return result
    
    async def _process_news_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process news task."""
        from pipelines.news_scraper import NewsScraper
        
        source = task_data.get('source')
        if not source:
            raise ValueError("News source not provided")
        
        scraper = NewsScraper()
        result = await scraper.scrape_news_async(source, **task_data.get('options', {}))
        
        # Save result to database/vector store
        await self._save_result(result)
        
        return result
    
    async def _process_job_post_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process job post task."""
        from pipelines.job_post_processor import JobPostProcessor
        
        job_post = task_data.get('job_post')
        if not job_post:
            raise ValueError("Job post content not provided")
        
        processor = JobPostProcessor()
        result = await processor.process_job_post_async(job_post, **task_data.get('options', {}))
        
        # Save result to database/vector store
        await self._save_result(result)
        
        return result
    
    async def _save_result(self, result: Dict[str, Any]):
        """Save processing result to database/vector store."""
        try:
            # In a real implementation, this would save to database and vector store
            # For now, just log the result
            logger.info(f"Saved result with {result.get('total_chunks', 0)} chunks")
            
        except Exception as e:
            logger.error(f"Failed to save result: {e}")
            raise


class IngestWorkerManager:
    """Manager for multiple ingestion workers."""
    
    def __init__(self, num_workers: int = 3, queue_name: str = 'ingestion'):
        self.num_workers = num_workers
        self.queue_name = queue_name
        self.workers = []
        self.worker_tasks = []
    
    async def start_workers(self):
        """Start all workers."""
        logger.info(f"Starting {self.num_workers} ingestion workers")
        
        for i in range(self.num_workers):
            worker = IngestWorker(worker_id=i, queue_name=self.queue_name)
            self.workers.append(worker)
            
            # Start worker in background
            task = asyncio.create_task(worker.start())
            self.worker_tasks.append(task)
        
        # Wait for all workers to complete
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
    
    async def stop_workers(self):
        """Stop all workers."""
        logger.info("Stopping all ingestion workers")
        
        for worker in self.workers:
            await worker.stop()
        
        # Cancel all worker tasks
        for task in self.worker_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
    
    async def get_worker_stats(self) -> Dict[str, Any]:
        """Get statistics about workers."""
        queue_manager = QueueManager()
        await queue_manager.initialize()
        
        try:
            stats = await queue_manager.get_queue_stats(self.queue_name)
            return {
                'num_workers': self.num_workers,
                'queue_stats': stats,
                'workers': [
                    {
                        'worker_id': i,
                        'status': 'running' if self.workers[i].running else 'stopped'
                    }
                    for i in range(len(self.workers))
                ]
            }
        finally:
            await queue_manager.close()


# CLI entry point
async def main():
    """Main entry point for worker."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingestion Worker')
    parser.add_argument('--workers', type=int, default=3, help='Number of workers')
    parser.add_argument('--queue', type=str, default='ingestion', help='Queue name')
    parser.add_argument('--timeout', type=int, default=300, help='Worker timeout')
    
    args = parser.parse_args()
    
    manager = IngestWorkerManager(
        num_workers=args.workers,
        queue_name=args.queue
    )
    
    try:
        await manager.start_workers()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
        await manager.stop_workers()
    except Exception as e:
        logger.error(f"Worker manager failed: {e}")
        raise


if __name__ == '__main__':
    asyncio.run(main())
