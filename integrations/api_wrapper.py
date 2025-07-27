"""FastAPI wrapper for the arXiv Research MCP Server."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.research_assistant import ResearchAssistant

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="arXiv Research API",
    description="API wrapper for the arXiv Research MCP Server",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Server path
SERVER_PATH = str(Path(__file__).parent.parent / "scripts" / "run_server.py")


# Pydantic models
class SearchRequest(BaseModel):
    """Search request model."""
    query: str = Field(..., description="Search query")
    max_results: int = Field(default=10, ge=1, le=50, description="Maximum results")
    years_back: int = Field(default=4, ge=1, le=20, description="Years to search back")
    include_full_text: bool = Field(default=True, description="Include full text")


class SearchResponse(BaseModel):
    """Search response model."""
    query: str
    results: str
    timestamp: datetime
    search_params: Dict


class BatchRequest(BaseModel):
    """Batch search request model."""
    topics: List[str] = Field(..., description="List of topics to search")
    max_results: int = Field(default=10, ge=1, le=20)
    years_back: int = Field(default=4, ge=1, le=10)
    include_full_text: bool = Field(default=False)


class BatchResponse(BaseModel):
    """Batch search response model."""
    results: Dict[str, str]
    total_topics: int
    successful_searches: int
    failed_searches: int
    timestamp: datetime


class CacheStatsResponse(BaseModel):
    """Cache statistics response model."""
    stats: str
    timestamp: datetime


# API endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "arXiv Research API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/search",
            "batch": "/batch",
            "cache/stats": "/cache/stats",
            "cache/clear": "/cache/clear"
        }
    }


@app.post("/search", response_model=SearchResponse)
async def search_papers(request: SearchRequest):
    """Search for papers."""
    try:
        async with ResearchAssistant(SERVER_PATH) as assistant:
            results = await assistant.search_papers(
                query=request.query,
                max_results=request.max_results,
                years_back=request.years_back,
                include_full_text=request.include_full_text
            )
        
        return SearchResponse(
            query=request.query,
            results=results,
            timestamp=datetime.now(),
            search_params=request.dict()
        )
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch", response_model=BatchResponse)
async def batch_search(request: BatchRequest):
    """Batch search for multiple topics."""
    results = {}
    successful = 0
    failed = 0
    
    try:
        async with ResearchAssistant(SERVER_PATH) as assistant:
            for topic in request.topics:
                try:
                    logger.info(f"Searching for topic: {topic}")
                    result = await assistant.search_papers(
                        query=topic,
                        max_results=request.max_results,
                        years_back=request.years_back,
                        include_full_text=request.include_full_text
                    )
                    results[topic] = result
                    successful += 1
                
                except Exception as e:
                    logger.error(f"Error searching for {topic}: {e}")
                    results[topic] = f"Error: {str(e)}"
                    failed += 1
        
        return BatchResponse(
            results=results,
            total_topics=len(request.topics),
            successful_searches=successful,
            failed_searches=failed,
            timestamp=datetime.now()
        )
    
    except Exception as e:
        logger.error(f"Batch search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cache/stats", response_model=CacheStatsResponse)
async def get_cache_stats():
    """Get cache statistics."""
    try:
        async with ResearchAssistant(SERVER_PATH) as assistant:
            stats = await assistant.get_cache_stats()
        
        return CacheStatsResponse(
            stats=stats,
            timestamp=datetime.now()
        )
    
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cache/clear")
async def clear_cache():
    """Clear the cache."""
    try:
        async with ResearchAssistant(SERVER_PATH) as assistant:
            result = await assistant.clear_cache()
        
        return {"message": result, "timestamp": datetime.now()}
    
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        async with ResearchAssistant(SERVER_PATH) as assistant:
            # Try to get cache stats as a simple health check
            await assistant.get_cache_stats()
        
        return {"status": "healthy", "timestamp": datetime.now()}
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


# Background task for cache cleanup
@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("arXiv Research API started")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("arXiv Research API shutdown")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )