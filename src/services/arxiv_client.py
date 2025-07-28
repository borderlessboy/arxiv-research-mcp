"""arXiv API client service."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional
import xml.etree.ElementTree as ET

import feedparser
import httpx
from asyncio_throttle import Throttler

from src.models.paper import Paper
from src.utils.date_utils import parse_arxiv_date
from config.settings import settings

logger = logging.getLogger(__name__)


class ArxivClient:
    """Client for interacting with the arXiv API."""
    
    def __init__(self):
        self.base_url = settings.ARXIV_API_BASE_URL
        self.timeout = settings.ARXIV_REQUEST_TIMEOUT
        self.throttler = Throttler(rate_limit=1/settings.REQUEST_RATE_LIMIT)
        
    async def search_papers(
        self,
        query: str,
        max_results: int = 50,
        years_back: int = 4,
        sort_by: str = "submittedDate",
        sort_order: str = "descending"
    ) -> List[Paper]:
        """Search for papers on arXiv."""
        
        logger.info(f"Searching arXiv for: {query} (max_results={max_results}, years_back={years_back})")
        
        params = {
            'search_query': self._build_search_query(query),
            'start': 0,
            'max_results': max_results * 2,  # Get more to allow for filtering
            'sortBy': sort_by,
            'sortOrder': sort_order
        }
        
        try:
            async with self.throttler:
                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                    response = await client.get(self.base_url, params=params)
                    response.raise_for_status()
                    
            papers = self._parse_arxiv_response(response.content)
            filtered_papers = self._filter_by_date(papers, years_back)
            
            logger.info(f"Found {len(papers)} papers, {len(filtered_papers)} after date filtering")
            return filtered_papers[:max_results]
            
        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
            raise
    
    def _build_search_query(self, query: str) -> str:
        """Build arXiv search query with proper formatting."""
        # Add field prefixes for better search results
        terms = query.lower().split()
        formatted_terms = []
        
        for term in terms:
            # Search in title, abstract, and categories
            formatted_terms.append(f"(ti:{term} OR abs:{term} OR cat:{term})")
        
        return " AND ".join(formatted_terms)
    
    def _parse_arxiv_response(self, content: bytes) -> List[Paper]:
        """Parse arXiv API response into Paper objects."""
        feed = feedparser.parse(content)
        papers = []
        
        for entry in feed.entries:
            try:
                # Extract arXiv ID from URL
                arxiv_id = entry.id.split('/')[-1]
                
                paper = Paper(
                    title=entry.title.strip(),
                    authors=[author.name for author in entry.authors],
                    published=parse_arxiv_date(entry.published),
                    summary=entry.summary.strip().replace('\n', ' '),
                    url=entry.link,
                    pdf_url=entry.link.replace('/abs/', '/pdf/'),
                    categories=[tag.term for tag in entry.tags],
                    arxiv_id=arxiv_id
                )
                papers.append(paper)
                
            except Exception as e:
                logger.warning(f"Error parsing paper entry: {e}")
                continue
                
        return papers
    
    def _filter_by_date(self, papers: List[Paper], years_back: int) -> List[Paper]:
        """Filter papers by publication date."""
        cutoff_date = datetime.now() - timedelta(days=years_back * 365)
        return [paper for paper in papers if paper.published >= cutoff_date]