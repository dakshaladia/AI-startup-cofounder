"""
News scraping pipeline for collecting startup and tech news.
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta
import logging
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class NewsScraper:
    """Scrapes news articles from various sources."""
    
    def __init__(self, rate_limit: float = 1.0, max_articles: int = 100):
        self.rate_limit = rate_limit
        self.max_articles = max_articles
        self.session = None
    
    def scrape_news(self, source: str, **kwargs) -> Dict[str, Any]:
        """
        Scrape news from a source synchronously.
        
        Args:
            source: News source (url, rss_feed, or predefined source)
            **kwargs: Additional scraping options
            
        Returns:
            Dictionary containing scraped articles
        """
        try:
            logger.info(f"Scraping news from: {source}")
            
            # Determine source type
            if source.startswith('http'):
                if 'rss' in source.lower() or source.endswith('.xml'):
                    articles = self._scrape_rss_feed(source)
                else:
                    articles = self._scrape_website(source)
            else:
                articles = self._scrape_predefined_source(source)
            
            # Filter and process articles
            filtered_articles = self._filter_articles(articles, **kwargs)
            
            # Create chunks
            chunks = self._create_chunks(filtered_articles)
            
            result = {
                'source_type': 'news',
                'source_url': source,
                'articles': filtered_articles,
                'chunks': chunks,
                'total_articles': len(filtered_articles),
                'total_chunks': len(chunks),
                'scraped_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"News scraping completed: {len(filtered_articles)} articles")
            return result
            
        except Exception as e:
            logger.error(f"Failed to scrape news from {source}: {e}")
            raise
    
    async def scrape_news_async(self, source: str, **kwargs) -> Dict[str, Any]:
        """
        Scrape news from a source asynchronously.
        
        Args:
            source: News source (url, rss_feed, or predefined source)
            **kwargs: Additional scraping options
            
        Returns:
            Dictionary containing scraped articles
        """
        try:
            logger.info(f"Scraping news async from: {source}")
            
            # Initialize session
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Determine source type
            if source.startswith('http'):
                if 'rss' in source.lower() or source.endswith('.xml'):
                    articles = await self._scrape_rss_feed_async(source)
                else:
                    articles = await self._scrape_website_async(source)
            else:
                articles = await self._scrape_predefined_source_async(source)
            
            # Filter and process articles
            filtered_articles = self._filter_articles(articles, **kwargs)
            
            # Create chunks
            chunks = self._create_chunks(filtered_articles)
            
            result = {
                'source_type': 'news',
                'source_url': source,
                'articles': filtered_articles,
                'chunks': chunks,
                'total_articles': len(filtered_articles),
                'total_chunks': len(chunks),
                'scraped_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"News scraping completed: {len(filtered_articles)} articles")
            return result
            
        except Exception as e:
            logger.error(f"Failed to scrape news from {source}: {e}")
            raise
        finally:
            if self.session:
                await self.session.close()
    
    def _scrape_rss_feed(self, rss_url: str) -> List[Dict[str, Any]]:
        """Scrape articles from RSS feed."""
        # Mock implementation - would normally use feedparser
        articles = []
        for i in range(5):  # Mock 5 articles
            articles.append({
                'title': f'Startup News Article {i+1}',
                'url': f'https://example.com/article{i+1}',
                'content': f'This is the content of article {i+1} about startups and technology.',
                'published_at': (datetime.utcnow() - timedelta(days=i)).isoformat(),
                'author': f'Author {i+1}',
                'source': 'RSS Feed'
            })
        return articles
    
    async def _scrape_rss_feed_async(self, rss_url: str) -> List[Dict[str, Any]]:
        """Scrape articles from RSS feed asynchronously."""
        # Mock implementation - would normally use async feedparser
        articles = []
        for i in range(5):  # Mock 5 articles
            articles.append({
                'title': f'Startup News Article {i+1}',
                'url': f'https://example.com/article{i+1}',
                'content': f'This is the content of article {i+1} about startups and technology.',
                'published_at': (datetime.utcnow() - timedelta(days=i)).isoformat(),
                'author': f'Author {i+1}',
                'source': 'RSS Feed'
            })
        return articles
    
    def _scrape_website(self, website_url: str) -> List[Dict[str, Any]]:
        """Scrape articles from website."""
        # Mock implementation - would normally use requests + BeautifulSoup
        articles = []
        for i in range(3):  # Mock 3 articles
            articles.append({
                'title': f'Website Article {i+1}',
                'url': f'{website_url}/article{i+1}',
                'content': f'This is the content of article {i+1} from the website.',
                'published_at': (datetime.utcnow() - timedelta(hours=i*6)).isoformat(),
                'author': f'Website Author {i+1}',
                'source': 'Website'
            })
        return articles
    
    async def _scrape_website_async(self, website_url: str) -> List[Dict[str, Any]]:
        """Scrape articles from website asynchronously."""
        # Mock implementation - would normally use aiohttp + BeautifulSoup
        articles = []
        for i in range(3):  # Mock 3 articles
            articles.append({
                'title': f'Website Article {i+1}',
                'url': f'{website_url}/article{i+1}',
                'content': f'This is the content of article {i+1} from the website.',
                'published_at': (datetime.utcnow() - timedelta(hours=i*6)).isoformat(),
                'author': f'Website Author {i+1}',
                'source': 'Website'
            })
        return articles
    
    def _scrape_predefined_source(self, source: str) -> List[Dict[str, Any]]:
        """Scrape articles from predefined source."""
        # Mock implementation for predefined sources
        sources = {
            'techcrunch': self._get_techcrunch_articles(),
            'hackernews': self._get_hackernews_articles(),
            'startup_news': self._get_startup_news_articles()
        }
        
        return sources.get(source, [])
    
    async def _scrape_predefined_source_async(self, source: str) -> List[Dict[str, Any]]:
        """Scrape articles from predefined source asynchronously."""
        # Mock implementation for predefined sources
        sources = {
            'techcrunch': self._get_techcrunch_articles(),
            'hackernews': self._get_hackernews_articles(),
            'startup_news': self._get_startup_news_articles()
        }
        
        return sources.get(source, [])
    
    def _get_techcrunch_articles(self) -> List[Dict[str, Any]]:
        """Get mock TechCrunch articles."""
        return [
            {
                'title': 'AI Startup Raises $50M Series A',
                'url': 'https://techcrunch.com/ai-startup-series-a',
                'content': 'An AI startup focused on enterprise solutions has raised $50M in Series A funding...',
                'published_at': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                'author': 'TechCrunch Staff',
                'source': 'TechCrunch'
            },
            {
                'title': 'New Fintech Platform Launches',
                'url': 'https://techcrunch.com/fintech-platform-launch',
                'content': 'A new fintech platform has launched with innovative payment solutions...',
                'published_at': (datetime.utcnow() - timedelta(hours=5)).isoformat(),
                'author': 'TechCrunch Staff',
                'source': 'TechCrunch'
            }
        ]
    
    def _get_hackernews_articles(self) -> List[Dict[str, Any]]:
        """Get mock Hacker News articles."""
        return [
            {
                'title': 'Show HN: Open Source AI Tool',
                'url': 'https://news.ycombinator.com/item?id=123456',
                'content': 'I built an open source AI tool for developers...',
                'published_at': (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                'author': 'HN User',
                'source': 'Hacker News'
            }
        ]
    
    def _get_startup_news_articles(self) -> List[Dict[str, Any]]:
        """Get mock startup news articles."""
        return [
            {
                'title': 'Startup Ecosystem Trends 2024',
                'url': 'https://startupnews.com/trends-2024',
                'content': 'Analysis of startup ecosystem trends for 2024...',
                'published_at': (datetime.utcnow() - timedelta(days=1)).isoformat(),
                'author': 'Startup News',
                'source': 'Startup News'
            }
        ]
    
    def _filter_articles(self, articles: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """Filter articles based on criteria."""
        filtered = articles
        
        # Filter by date
        if 'days_back' in kwargs:
            cutoff_date = datetime.utcnow() - timedelta(days=kwargs['days_back'])
            filtered = [
                article for article in filtered
                if datetime.fromisoformat(article['published_at']) >= cutoff_date
            ]
        
        # Filter by keywords
        if 'keywords' in kwargs:
            keywords = kwargs['keywords']
            filtered = [
                article for article in filtered
                if any(keyword.lower() in article['title'].lower() or 
                      keyword.lower() in article['content'].lower() 
                      for keyword in keywords)
            ]
        
        # Filter by source
        if 'sources' in kwargs:
            sources = kwargs['sources']
            filtered = [
                article for article in filtered
                if article['source'] in sources
            ]
        
        # Limit number of articles
        if 'max_articles' in kwargs:
            filtered = filtered[:kwargs['max_articles']]
        elif self.max_articles:
            filtered = filtered[:self.max_articles]
        
        return filtered
    
    def _create_chunks(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create text chunks from articles."""
        chunks = []
        
        for article in articles:
            # Create chunks from title and content
            text = f"{article['title']}\n\n{article['content']}"
            
            # Split into sentences (simple implementation)
            sentences = text.split('. ')
            
            # Create chunks from sentences
            chunk_text = ""
            for sentence in sentences:
                if len(chunk_text + sentence) > 500:  # Chunk size limit
                    if chunk_text:
                        chunks.append({
                            'text': chunk_text.strip(),
                            'article_title': article['title'],
                            'article_url': article['url'],
                            'article_author': article['author'],
                            'article_published_at': article['published_at'],
                            'source': article['source']
                        })
                    chunk_text = sentence
                else:
                    chunk_text += sentence + ". "
            
            # Add remaining text as chunk
            if chunk_text.strip():
                chunks.append({
                    'text': chunk_text.strip(),
                    'article_title': article['title'],
                    'article_url': article['url'],
                    'article_author': article['author'],
                    'article_published_at': article['published_at'],
                    'source': article['source']
                })
        
        return chunks
