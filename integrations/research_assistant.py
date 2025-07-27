"""Research assistant for the arXiv Research MCP Server."""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.arxiv_client import ArxivClient
from src.services.relevance_ranker import RelevanceRanker
from src.services.cache_manager import CacheManager
from src.services.pdf_processor import PDFProcessor
from src.models.paper import Paper

logger = logging.getLogger(__name__)


class ResearchAssistant:
    """Research assistant for interacting with the arXiv Research MCP Server."""
    
    def __init__(self, server_path: str = None):
        """Initialize the research assistant."""
        self.server_path = server_path or str(Path(__file__).parent.parent / "scripts" / "run_server.py")
        self.arxiv_client = ArxivClient()
        self.ranker = RelevanceRanker()
        self.cache_manager = CacheManager()
        self.pdf_processor = PDFProcessor()
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass
    
    async def search_papers(
        self,
        query: str,
        max_results: int = 10,
        years_back: int = 4,
        include_full_text: bool = True
    ) -> str:
        """
        Search for papers on arXiv and return formatted results.
        
        Args:
            query: Research query
            max_results: Maximum number of papers to return
            years_back: Number of years back to search
            include_full_text: Whether to include full paper text
            
        Returns:
            Formatted string with search results
        """
        try:
            # Check cache first
            cache_key = f"{query}_{max_results}_{years_back}_{include_full_text}"
            cached_results = self.cache_manager.get(cache_key)
            
            if cached_results:
                logger.info(f"Using cached results for query: {query}")
                return cached_results
            
            # Search arXiv
            logger.info(f"Searching arXiv for: {query}")
            papers = await self.arxiv_client.search(
                query=query,
                max_results=max_results,
                years_back=years_back
            )
            
            # Extract full text if requested
            if include_full_text:
                for paper in papers:
                    try:
                        if paper.pdf_url:
                            paper.full_text = await self.pdf_processor.extract_text(paper.pdf_url)
                    except Exception as e:
                        logger.warning(f"Failed to extract text for {paper.id}: {e}")
                        paper.full_text = ""
            
            # Rank papers by relevance
            ranked_papers = self.ranker.rank_papers(papers, query)
            
            # Format results
            formatted_results = self._format_results(ranked_papers, query)
            
            # Cache results
            self.cache_manager.set(cache_key, formatted_results)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching papers: {e}")
            return f"Error searching papers: {str(e)}"
    
    def _format_results(self, papers: List[Paper], query: str) -> str:
        """Format papers into a readable string."""
        if not papers:
            return f"No papers found for query: {query}"
        
        result = f"# Research Results for: {query}\n\n"
        result += f"Found {len(papers)} relevant papers:\n\n"
        
        for i, paper in enumerate(papers, 1):
            result += f"## Paper {i}: {paper.title}\n\n"
            result += f"**Authors:** {', '.join(paper.authors)}\n\n"
            result += f"**Published:** {paper.published.strftime('%B %d, %Y')}\n\n"
            result += f"**Categories:** {', '.join(paper.categories)}\n\n"
            result += f"**URL:** {paper.url}\n\n"
            result += f"**arXiv ID:** {paper.id}\n\n"
            result += f"**Relevance Score:** {paper.relevance_score:.3f}\n\n"
            result += f"**Abstract:**\n{paper.summary}\n\n"
            
            if hasattr(paper, 'full_text') and paper.full_text:
                result += f"**Full Text:**\n{paper.full_text[:1000]}...\n\n"
            
            result += "---\n\n"
        
        return result
    
    async def get_cache_stats(self) -> str:
        """Get cache statistics."""
        try:
            stats = self.cache_manager.get_stats()
            return json.dumps(stats, indent=2)
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return f"Error getting cache stats: {str(e)}"
    
    async def clear_cache(self) -> str:
        """Clear the cache."""
        try:
            self.cache_manager.clear()
            return "Cache cleared successfully"
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return f"Error clearing cache: {str(e)}"


# Example usage
if __name__ == "__main__":
    async def main():
        async with ResearchAssistant() as assistant:
            results = await assistant.search_papers(
                query="machine learning",
                max_results=5,
                years_back=2,
                include_full_text=False
            )
            print(results)
    
    asyncio.run(main())
