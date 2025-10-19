"""
CLI for ingestion jobs.
"""

import asyncio
import click
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

from pipelines.news_scraper import NewsScraper
from pipelines.pdf_processor import PDFProcessor
from pipelines.image_processor import ImageProcessor
from pipelines.job_post_processor import JobPostProcessor
from workers.ingest_worker import IngestWorker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """AI Startup Co-Founder ingestion CLI."""
    pass


@cli.command()
@click.option('--source', '-s', required=True, help='Source type (news, pdf, image, job_post)')
@click.option('--input', '-i', required=True, help='Input file or URL')
@click.option('--output', '-o', help='Output directory')
@click.option('--config', '-c', help='Configuration file path')
@click.option('--async', 'async_mode', is_flag=True, help='Run in async mode')
def process(source: str, input: str, output: Optional[str], config: Optional[str], async_mode: bool):
    """Process a single source."""
    try:
        if async_mode:
            asyncio.run(_process_async(source, input, output, config))
        else:
            _process_sync(source, input, output, config)
    except Exception as e:
        logger.error(f"Failed to process {source}: {e}")
        raise click.ClickException(str(e))


@cli.command()
@click.option('--config', '-c', required=True, help='Batch configuration file')
@click.option('--async', 'async_mode', is_flag=True, help='Run in async mode')
def batch(config: str, async_mode: bool):
    """Process multiple sources from configuration file."""
    try:
        with open(config, 'r') as f:
            batch_config = json.load(f)
        
        if async_mode:
            asyncio.run(_batch_process_async(batch_config))
        else:
            _batch_process_sync(batch_config)
    except Exception as e:
        logger.error(f"Failed to process batch: {e}")
        raise click.ClickException(str(e))


@cli.command()
@click.option('--queue', '-q', default='ingestion', help='Queue name')
@click.option('--workers', '-w', default=1, help='Number of workers')
@click.option('--timeout', '-t', default=300, help='Worker timeout in seconds')
def worker(queue: str, workers: int, timeout: int):
    """Start ingestion workers."""
    try:
        asyncio.run(_start_workers(queue, workers, timeout))
    except Exception as e:
        logger.error(f"Failed to start workers: {e}")
        raise click.ClickException(str(e))


def _process_sync(source: str, input: str, output: Optional[str], config: Optional[str]):
    """Process source synchronously."""
    logger.info(f"Processing {source} from {input}")
    
    # Load configuration
    config_data = {}
    if config:
        with open(config, 'r') as f:
            config_data = json.load(f)
    
    # Initialize processor based on source type
    if source == 'news':
        processor = NewsScraper()
        result = processor.scrape_news(input, **config_data)
    elif source == 'pdf':
        processor = PDFProcessor()
        result = processor.process_pdf(input, **config_data)
    elif source == 'image':
        processor = ImageProcessor()
        result = processor.process_image(input, **config_data)
    elif source == 'job_post':
        processor = JobPostProcessor()
        result = processor.process_job_post(input, **config_data)
    else:
        raise ValueError(f"Unsupported source type: {source}")
    
    # Save result
    if output:
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        with open(output_path / f"{source}_result.json", 'w') as f:
            json.dump(result, f, indent=2)
    
    logger.info(f"Processing completed: {len(result.get('chunks', []))} chunks created")


async def _process_async(source: str, input: str, output: Optional[str], config: Optional[str]):
    """Process source asynchronously."""
    logger.info(f"Processing {source} from {input} (async)")
    
    # Load configuration
    config_data = {}
    if config:
        with open(config, 'r') as f:
            config_data = json.load(f)
    
    # Initialize processor based on source type
    if source == 'news':
        processor = NewsScraper()
        result = await processor.scrape_news_async(input, **config_data)
    elif source == 'pdf':
        processor = PDFProcessor()
        result = await processor.process_pdf_async(input, **config_data)
    elif source == 'image':
        processor = ImageProcessor()
        result = await processor.process_image_async(input, **config_data)
    elif source == 'job_post':
        processor = JobPostProcessor()
        result = await processor.process_job_post_async(input, **config_data)
    else:
        raise ValueError(f"Unsupported source type: {source}")
    
    # Save result
    if output:
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        with open(output_path / f"{source}_result.json", 'w') as f:
            json.dump(result, f, indent=2)
    
    logger.info(f"Processing completed: {len(result.get('chunks', []))} chunks created")


def _batch_process_sync(batch_config: Dict[str, Any]):
    """Process multiple sources synchronously."""
    logger.info(f"Processing batch with {len(batch_config.get('sources', []))} sources")
    
    for source_config in batch_config.get('sources', []):
        try:
            _process_sync(
                source=source_config['type'],
                input=source_config['input'],
                output=source_config.get('output'),
                config=source_config.get('config')
            )
        except Exception as e:
            logger.error(f"Failed to process {source_config}: {e}")
            continue
    
    logger.info("Batch processing completed")


async def _batch_process_async(batch_config: Dict[str, Any]):
    """Process multiple sources asynchronously."""
    logger.info(f"Processing batch with {len(batch_config.get('sources', []))} sources (async)")
    
    tasks = []
    for source_config in batch_config.get('sources', []):
        task = _process_async(
            source=source_config['type'],
            input=source_config['input'],
            output=source_config.get('output'),
            config=source_config.get('config')
        )
        tasks.append(task)
    
    await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("Batch processing completed")


async def _start_workers(queue: str, workers: int, timeout: int):
    """Start ingestion workers."""
    logger.info(f"Starting {workers} workers for queue {queue}")
    
    worker_tasks = []
    for i in range(workers):
        worker = IngestWorker(worker_id=i, queue_name=queue, timeout=timeout)
        task = asyncio.create_task(worker.start())
        worker_tasks.append(task)
    
    try:
        await asyncio.gather(*worker_tasks)
    except KeyboardInterrupt:
        logger.info("Shutting down workers...")
        for task in worker_tasks:
            task.cancel()
        await asyncio.gather(*worker_tasks, return_exceptions=True)


if __name__ == '__main__':
    cli()
