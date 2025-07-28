"""Main MCP server implementation."""

import asyncio
import logging
import time
from typing import Dict, List

from mcp.server import Server
from mcp import types
from mcp.server import NotificationOptions
from mcp.server.models import InitializationOptions

from src.models.paper import Paper, SearchRequest
from src.services.arxiv_client import ArxivClient
from src.services.cache_manager import CacheManager
from src.services.pdf_processor import PDFProcessor
from src.services.relevance_ranker import RelevanceRanker
from src.utils.text_utils import format_author_list, truncate_text
from src.config.settings import settings

# Configure logging
logging.basicConfig(
 level=getattr(logging, settings.LOG_LEVEL),
 format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Initialize server
app = Server(settings.SERVER_NAME)

# Initialize services
arxiv_client = ArxivClient()
cache_manager = CacheManager()
pdf_processor = PDFProcessor()
relevance_ranker = RelevanceRanker()

# Initialize services
arxiv_client = ArxivClient()
cache_manager = CacheManager()
pdf_processor = PDFProcessor()
relevance_ranker = RelevanceRanker()


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="search_arxiv_papers",
            description="Search arXiv for academic papers with relevance ranking and full text extraction",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'transformer models', 'quantum computing')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of papers to return"
                    },
                    "years_back": {
                        "type": "integer",
                        "description": "Number of years back to search"
                    },
                    "include_full_text": {
                        "type": "boolean",
                        "description": "Whether to include full paper text"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="clear_cache",
            description="Clear all cached search results",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get_cache_stats",
            description="Get cache statistics and information",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(
    name: str,
    arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls."""
    
    try:
        if name == "search_arxiv_papers":
            return await search_arxiv_papers_tool(arguments)
        elif name == "clear_cache":
            return await clear_cache_tool()
        elif name == "get_cache_stats":
            return await get_cache_stats_tool()
        else:
            raise ValueError(f"Tool not found: {name}")
    except Exception as e:
        logger.error(f"Error in tool call {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error executing tool {name}: {str(e)}"
        )]


async def search_arxiv_papers_tool(arguments: Dict) -> List[types.TextContent]:
    """Search for arXiv papers."""
    
    try:
        # Validate and parse arguments
        search_request = SearchRequest(**arguments)
        
        logger.info(f"Processing search request: {search_request.query}")
        start_time = time.time()
        
        # Check cache first
        cached_papers = await cache_manager.get_cached_results(
            search_request.query, 
            search_request.years_back
        )
        
        if cached_papers:
            papers = cached_papers
            cached = True
            logger.info(f"Using cached results for: {search_request.query}")
        else:
            # Perform fresh search
            papers = await arxiv_client.search_papers(
                query=search_request.query,
                max_results=search_request.max_results * 2, # Get more for ranking
                years_back=search_request.years_back
            )
            
            if not papers:
                return [types.TextContent(
                    type="text",
                    text=f"No papers found for query: '{search_request.query}' in the last {search_request.years_back} years"
                )]
            
            # Cache the raw results
            await cache_manager.cache_results(
                search_request.query, 
                search_request.years_back, 
                papers
            )
            cached = False
        
        # Rank papers by relevance
        ranked_papers = relevance_ranker.rank_papers(papers, search_request.query)
        
        # Select top papers
        top_papers = relevance_ranker.select_top_papers(ranked_papers, search_request.max_results)
        
        if not top_papers:
            return [types.TextContent(
                type="text",
                text=f"No relevant papers found for query: '{search_request.query}' after relevance ranking"
            )]
        
        # Extract full text if requested
        if search_request.include_full_text:
            logger.info(f"Extracting full text for {len(top_papers)} papers")
            top_papers = await pdf_processor.process_papers_batch(top_papers)
        
        # Update processing timestamp
        for paper in top_papers:
            paper.processed_at = time.time()
        
        search_time = time.time() - start_time
        
        # Format results for LLM
        formatted_results = format_papers_for_llm(
            papers=top_papers,
            query=search_request.query,
            search_time=search_time,
            cached=cached,
            include_full_text=search_request.include_full_text
        )
        
        return [types.TextContent(
            type="text",
            text=formatted_results
        )]
        
    except Exception as e:
        logger.error(f"Error in search_arxiv_papers_tool: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error searching arXiv: {str(e)}"
        )]


async def clear_cache_tool() -> List[types.TextContent]:
    """Clear cache tool."""
    try:
        cleared_count = await cache_manager.clear_cache()
        return [types.TextContent(
            type="text",
            text=f"Cache cleared successfully. Removed {cleared_count} cached entries."
        )]
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error clearing cache: {str(e)}"
        )]


async def get_cache_stats_tool() -> List[types.TextContent]:
    """Get cache statistics tool."""
    try:
        stats = await cache_manager.get_cache_stats()
        
        if not stats.get("enabled", False):
            return [types.TextContent(
                type="text",
                text="Cache is disabled in configuration."
            )]
        
        stats_text = f"""
Cache Statistics:
- Status: Enabled
- Total Entries: {stats.get('total_entries', 0)}
- Total Size: {stats.get('total_size_mb', 0)} MB
- Cache Directory: {stats.get('cache_dir', 'N/A')}
- TTL Hours: {stats.get('ttl_hours', 0)}
"""
        
        return [types.TextContent(
            type="text",
            text=stats_text.strip()
        )]
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error getting cache statistics: {str(e)}"
        )]


def format_papers_for_llm(
    papers: List[Paper],
    query: str,
    search_time: float,
    cached: bool,
    include_full_text: bool = True
) -> str:
    """Format papers for LLM analysis."""
    
    if not papers:
        return f"No papers found for query: '{query}'"
    
    # Header information
    header = f"""# arXiv Research Results

**Query:** {query}
**Papers Found:** {len(papers)}
**Search Time:** {search_time:.2f} seconds
**Source:** {'Cache' if cached else 'Fresh Search'}
**Full Text Included:** {'Yes' if include_full_text else 'No'}

---

"""
    
    # Format each paper
    formatted_papers = []
    for i, paper in enumerate(papers, 1):
        paper_text = f"""## Paper {i}: {paper.title}

**Authors:** {format_author_list(paper.authors)}
**Published:** {paper.published.strftime('%B %d, %Y')}
**arXiv ID:** {paper.arxiv_id or 'N/A'}
**Categories:** {', '.join(paper.categories)}
**Relevance Score:** {paper.relevance_score:.3f}
**URL:** {paper.url}

**Abstract:**
{paper.summary}
"""
        
        if include_full_text and paper.full_text:
            # Truncate full text if very long
            full_text = truncate_text(paper.full_text, settings.MAX_FULL_TEXT_LENGTH, 
                "\n\n[Text truncated due to length limit]")
            paper_text += f"""
**Full Text:**
{full_text}
"""
        elif include_full_text:
            paper_text += "\n**Full Text:** [Unable to extract full text from PDF]"
        
        formatted_papers.append(paper_text)
    
    # Combine all sections
    result = header + "\n\n---\n\n".join(formatted_papers)
    
    # Add analysis suggestions
    result += f"""

---

## Analysis Suggestions

Based on the {len(papers)} papers found for "{query}", you can analyze:

1. **Key Trends**: What are the main research directions and methodologies?
2. **Innovation Patterns**: What novel approaches or techniques are emerging?
3. **Research Gaps**: What areas need more investigation?
4. **Methodological Evolution**: How have approaches changed over time?
5. **Cross-Domain Applications**: How is this research being applied in different fields?
6. **Future Directions**: What do the authors suggest for future research?

The papers are ranked by relevance score, with the most relevant papers appearing first.
"""
    
    return result