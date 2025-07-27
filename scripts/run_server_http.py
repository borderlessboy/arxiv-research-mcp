#!/usr/bin/env python3
"""
HTTP API wrapper for the arXiv Research MCP Server
This provides a REST API interface to the MCP server
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel

from config.settings import settings
from src.server import call_tool

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="arXiv Research MCP Server API",
    description="HTTP API wrapper for the arXiv Research MCP Server",
    version=settings.SERVER_VERSION
)

# Pydantic models for request/response
class SearchRequest(BaseModel):
    query: str
    max_results: int = 10
    years_back: int = 2
    include_full_text: bool = True

class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any] = {}

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "arXiv Research MCP Server API",
        "version": settings.SERVER_VERSION,
        "endpoints": {
            "/search": "Search for arXiv papers",
            "/tools": "List available tools",
            "/cache/stats": "Get cache statistics",
            "/cache/clear": "Clear cache"
        }
    }

@app.get("/tools")
async def list_tools():
    """List available tools."""
    try:
        from src.server import list_tools
        tools = await list_tools()
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in tools
            ]
        }
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_papers(request: SearchRequest):
    """Search for arXiv papers."""
    try:
        result = await call_tool("search_arxiv_papers", {
            "query": request.query,
            "max_results": request.max_results,
            "years_back": request.years_back,
            "include_full_text": request.include_full_text
        })
        
        return {
            "query": request.query,
            "results": [item.text for item in result],
            "count": len(result)
        }
    except Exception as e:
        logger.error(f"Error searching papers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/call")
async def call_tool_endpoint(request: ToolCallRequest):
    """Call a specific tool."""
    try:
        result = await call_tool(request.name, request.arguments)
        return {
            "tool": request.name,
            "results": [item.text for item in result],
            "count": len(result)
        }
    except Exception as e:
        logger.error(f"Error calling tool {request.name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics."""
    try:
        result = await call_tool("get_cache_stats", {})
        return {"stats": result[0].text if result else "No stats available"}
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cache/clear")
async def clear_cache():
    """Clear the cache."""
    try:
        result = await call_tool("clear_cache", {})
        return {"message": result[0].text if result else "Cache cleared"}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "server": settings.SERVER_NAME}

def main():
    """Run the HTTP API server."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run arXiv Research MCP Server HTTP API')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    logger.info(f"Starting {settings.SERVER_NAME} HTTP API on {args.host}:{args.port}")
    
    try:
        uvicorn.run(
            "scripts.run_server_http:app",
            host=args.host,
            port=args.port,
            reload=args.debug,
            log_level="debug" if args.debug else "info"
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 