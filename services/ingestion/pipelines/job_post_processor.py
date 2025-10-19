"""
Job post processing pipeline for analyzing startup job postings.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class JobPostProcessor:
    """Processes job postings to extract insights about startup trends."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_job_post(self, job_post: str, **kwargs) -> Dict[str, Any]:
        """
        Process a job post synchronously.
        
        Args:
            job_post: Job post content (text, URL, or structured data)
            **kwargs: Additional processing options
            
        Returns:
            Dictionary containing extracted data
        """
        try:
            logger.info(f"Processing job post: {job_post[:100]}...")
            
            # Parse job post
            parsed_job = self._parse_job_post(job_post)
            
            # Extract insights
            insights = self._extract_insights(parsed_job)
            
            # Create chunks
            chunks = self._create_chunks(parsed_job)
            
            result = {
                'source_type': 'job_post',
                'source_content': job_post,
                'parsed_job': parsed_job,
                'insights': insights,
                'chunks': chunks,
                'total_chunks': len(chunks),
                'processed_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Job post processing completed: {len(chunks)} chunks created")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process job post: {e}")
            raise
    
    async def process_job_post_async(self, job_post: str, **kwargs) -> Dict[str, Any]:
        """
        Process a job post asynchronously.
        
        Args:
            job_post: Job post content (text, URL, or structured data)
            **kwargs: Additional processing options
            
        Returns:
            Dictionary containing extracted data
        """
        try:
            logger.info(f"Processing job post async: {job_post[:100]}...")
            
            # Parse job post
            parsed_job = await self._parse_job_post_async(job_post)
            
            # Extract insights
            insights = await self._extract_insights_async(parsed_job)
            
            # Create chunks
            chunks = self._create_chunks(parsed_job)
            
            result = {
                'source_type': 'job_post',
                'source_content': job_post,
                'parsed_job': parsed_job,
                'insights': insights,
                'chunks': chunks,
                'total_chunks': len(chunks),
                'processed_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Job post processing completed: {len(chunks)} chunks created")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process job post: {e}")
            raise
    
    def _parse_job_post(self, job_post: str) -> Dict[str, Any]:
        """Parse job post content."""
        # Mock implementation - would normally use NLP to extract structured data
        return {
            'title': self._extract_title(job_post),
            'company': self._extract_company(job_post),
            'location': self._extract_location(job_post),
            'job_type': self._extract_job_type(job_post),
            'description': self._extract_description(job_post),
            'requirements': self._extract_requirements(job_post),
            'benefits': self._extract_benefits(job_post),
            'salary_range': self._extract_salary_range(job_post),
            'technologies': self._extract_technologies(job_post),
            'experience_level': self._extract_experience_level(job_post),
            'remote_work': self._extract_remote_work(job_post),
            'posted_date': self._extract_posted_date(job_post)
        }
    
    async def _parse_job_post_async(self, job_post: str) -> Dict[str, Any]:
        """Parse job post content asynchronously."""
        # For now, use synchronous version
        # In a real implementation, this would use async NLP processing
        return self._parse_job_post(job_post)
    
    def _extract_title(self, job_post: str) -> str:
        """Extract job title."""
        # Mock implementation - would normally use NLP
        lines = job_post.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            if any(word in line.lower() for word in ['engineer', 'developer', 'manager', 'analyst']):
                return line.strip()
        return "Software Engineer"  # Default title
    
    def _extract_company(self, job_post: str) -> str:
        """Extract company name."""
        # Mock implementation - would normally use NLP
        lines = job_post.split('\n')
        for line in lines[:3]:  # Check first 3 lines
            if 'at' in line.lower() and len(line.strip()) < 50:
                return line.split('at')[-1].strip()
        return "Unknown Company"
    
    def _extract_location(self, job_post: str) -> str:
        """Extract job location."""
        # Mock implementation - would normally use NLP
        location_patterns = [
            r'(?:in|at|located in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+,\s*[A-Z]{2})',  # City, State format
            r'([A-Z][a-z]+,\s*[A-Z][a-z]+)'  # City, Country format
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, job_post, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "Remote"  # Default to remote
    
    def _extract_job_type(self, job_post: str) -> str:
        """Extract job type (full-time, part-time, contract, etc.)."""
        job_post_lower = job_post.lower()
        if 'full-time' in job_post_lower or 'full time' in job_post_lower:
            return 'Full-time'
        elif 'part-time' in job_post_lower or 'part time' in job_post_lower:
            return 'Part-time'
        elif 'contract' in job_post_lower:
            return 'Contract'
        elif 'intern' in job_post_lower:
            return 'Internship'
        else:
            return 'Full-time'  # Default
    
    def _extract_description(self, job_post: str) -> str:
        """Extract job description."""
        # Mock implementation - would normally use NLP
        lines = job_post.split('\n')
        description_lines = []
        in_description = False
        
        for line in lines:
            if any(word in line.lower() for word in ['description', 'about', 'role']):
                in_description = True
                continue
            elif any(word in line.lower() for word in ['requirements', 'qualifications', 'benefits']):
                break
            elif in_description and line.strip():
                description_lines.append(line.strip())
        
        return ' '.join(description_lines[:10])  # Limit to first 10 lines
    
    def _extract_requirements(self, job_post: str) -> List[str]:
        """Extract job requirements."""
        # Mock implementation - would normally use NLP
        requirements = []
        lines = job_post.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['required', 'must have', 'need']):
                if line.strip():
                    requirements.append(line.strip())
        
        return requirements[:5]  # Limit to 5 requirements
    
    def _extract_benefits(self, job_post: str) -> List[str]:
        """Extract job benefits."""
        # Mock implementation - would normally use NLP
        benefits = []
        lines = job_post.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['benefit', 'perk', 'offer', 'provide']):
                if line.strip():
                    benefits.append(line.strip())
        
        return benefits[:5]  # Limit to 5 benefits
    
    def _extract_salary_range(self, job_post: str) -> str:
        """Extract salary range."""
        # Mock implementation - would normally use NLP
        salary_patterns = [
            r'\$[\d,]+(?:-\$[\d,]+)?',
            r'[\d,]+(?:-[\d,]+)?\s*(?:k|K)',
            r'salary[:\s]*\$?[\d,]+(?:-\$?[\d,]+)?'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, job_post, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "Not specified"
    
    def _extract_technologies(self, job_post: str) -> List[str]:
        """Extract technologies mentioned."""
        # Mock implementation - would normally use NLP
        tech_keywords = [
            'python', 'javascript', 'java', 'react', 'node.js', 'aws', 'docker',
            'kubernetes', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'machine learning', 'ai', 'blockchain', 'web3', 'api', 'microservices'
        ]
        
        mentioned_tech = []
        job_post_lower = job_post.lower()
        
        for tech in tech_keywords:
            if tech in job_post_lower:
                mentioned_tech.append(tech)
        
        return mentioned_tech
    
    def _extract_experience_level(self, job_post: str) -> str:
        """Extract experience level required."""
        job_post_lower = job_post.lower()
        
        if any(word in job_post_lower for word in ['senior', 'lead', 'principal', 'architect']):
            return 'Senior'
        elif any(word in job_post_lower for word in ['junior', 'entry', 'graduate', 'new grad']):
            return 'Junior'
        elif any(word in job_post_lower for word in ['mid', 'intermediate', '3-5 years']):
            return 'Mid-level'
        else:
            return 'Not specified'
    
    def _extract_remote_work(self, job_post: str) -> bool:
        """Extract remote work availability."""
        job_post_lower = job_post.lower()
        remote_keywords = ['remote', 'work from home', 'wfh', 'distributed']
        return any(keyword in job_post_lower for keyword in remote_keywords)
    
    def _extract_posted_date(self, job_post: str) -> str:
        """Extract posted date."""
        # Mock implementation - would normally use NLP
        return datetime.utcnow().isoformat()
    
    def _extract_insights(self, parsed_job: Dict[str, Any]) -> Dict[str, Any]:
        """Extract insights from parsed job post."""
        return {
            'trending_technologies': self._identify_trending_technologies(parsed_job),
            'market_demand': self._assess_market_demand(parsed_job),
            'startup_stage': self._infer_startup_stage(parsed_job),
            'funding_indicators': self._identify_funding_indicators(parsed_job),
            'growth_indicators': self._identify_growth_indicators(parsed_job)
        }
    
    async def _extract_insights_async(self, parsed_job: Dict[str, Any]) -> Dict[str, Any]:
        """Extract insights from parsed job post asynchronously."""
        # For now, use synchronous version
        # In a real implementation, this would use async NLP processing
        return self._extract_insights(parsed_job)
    
    def _identify_trending_technologies(self, parsed_job: Dict[str, Any]) -> List[str]:
        """Identify trending technologies from job post."""
        # Mock implementation - would normally use ML models
        trending_tech = []
        technologies = parsed_job.get('technologies', [])
        
        for tech in technologies:
            if tech in ['ai', 'machine learning', 'blockchain', 'web3']:
                trending_tech.append(tech)
        
        return trending_tech
    
    def _assess_market_demand(self, parsed_job: Dict[str, Any]) -> str:
        """Assess market demand for the role."""
        # Mock implementation - would normally use market data
        technologies = parsed_job.get('technologies', [])
        
        if len(technologies) > 5:
            return 'High'
        elif len(technologies) > 2:
            return 'Medium'
        else:
            return 'Low'
    
    def _infer_startup_stage(self, parsed_job: Dict[str, Any]) -> str:
        """Infer startup stage from job post."""
        # Mock implementation - would normally use ML models
        description = parsed_job.get('description', '').lower()
        
        if any(word in description for word in ['early stage', 'startup', 'founding']):
            return 'Early Stage'
        elif any(word in description for word in ['scale', 'growth', 'expansion']):
            return 'Growth Stage'
        else:
            return 'Unknown'
    
    def _identify_funding_indicators(self, parsed_job: Dict[str, Any]) -> List[str]:
        """Identify funding indicators from job post."""
        # Mock implementation - would normally use NLP
        indicators = []
        description = parsed_job.get('description', '').lower()
        
        if 'series a' in description or 'series b' in description:
            indicators.append('Series Funding')
        if 'venture' in description or 'vc' in description:
            indicators.append('VC Backed')
        if 'funding' in description:
            indicators.append('Funding Mentioned')
        
        return indicators
    
    def _identify_growth_indicators(self, parsed_job: Dict[str, Any]) -> List[str]:
        """Identify growth indicators from job post."""
        # Mock implementation - would normally use NLP
        indicators = []
        description = parsed_job.get('description', '').lower()
        
        if 'hiring' in description or 'team' in description:
            indicators.append('Team Expansion')
        if 'scale' in description or 'growth' in description:
            indicators.append('Scaling')
        if 'remote' in description or 'distributed' in description:
            indicators.append('Remote Work')
        
        return indicators
    
    def _create_chunks(self, parsed_job: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create text chunks from parsed job post."""
        chunks = []
        
        # Create chunks from different sections
        sections = [
            ('title', parsed_job.get('title', '')),
            ('description', parsed_job.get('description', '')),
            ('requirements', ' '.join(parsed_job.get('requirements', []))),
            ('benefits', ' '.join(parsed_job.get('benefits', []))),
            ('technologies', ' '.join(parsed_job.get('technologies', [])))
        ]
        
        for section_name, content in sections:
            if content:
                chunks.append({
                    'text': content,
                    'section': section_name,
                    'company': parsed_job.get('company', ''),
                    'location': parsed_job.get('location', ''),
                    'job_type': parsed_job.get('job_type', ''),
                    'technologies': parsed_job.get('technologies', []),
                    'experience_level': parsed_job.get('experience_level', ''),
                    'remote_work': parsed_job.get('remote_work', False)
                })
        
        return chunks
