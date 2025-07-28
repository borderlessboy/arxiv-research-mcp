#!/usr/bin/env python3
"""
Example usage of arXiv Research MCP Server with MCPO
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def example_basic_search():
    """Example of basic paper search using the MCP server directly."""
    print("=== Basic Paper Search Example ===")
    
    try:
        from src.server import call_tool
        
        # Search for papers about transformer models
        result = await call_tool("search_arxiv_papers", {
            "query": "transformer models",
            "max_results": 3,
            "years_back": 1,
            "include_full_text": False
        })
        
        print(f"Found {len(result)} result(s)")
        if result:
            print(f"First result text length: {len(result[0].text)} characters")
            print("Sample of first result:")
            print(result[0].text[:500] + "...")
            
    except Exception as e:
        print(f"Error: {e}")

async def example_cache_management():
    """Example of cache management."""
    print("\n=== Cache Management Example ===")
    
    try:
        from src.server import call_tool
        
        # Get cache statistics
        stats = await call_tool("get_cache_stats", {})
        print("Cache Statistics:")
        print(stats[0].text)
        
        # Optionally clear cache
        # cleared = await call_tool("clear_cache", {})
        # print(f"Cache cleared: {cleared[0].text}")
        
    except Exception as e:
        print(f"Error: {e}")

async def example_research_workflow():
    """Example of a complete research workflow."""
    print("\n=== Research Workflow Example ===")
    
    try:
        from src.server import call_tool
        
        # Step 1: Search for recent papers on a topic
        papers = await call_tool("search_arxiv_papers", {
            "query": "quantum machine learning",
            "max_results": 2,
            "years_back": 1,
            "include_full_text": True
        })
        
        print(f"Found {len(papers)} papers on quantum machine learning")
        
        # Step 2: Get cache stats to see what's cached
        stats = await call_tool("get_cache_stats", {})
        print("Current cache status:")
        print(stats[0].text)
        
        # Step 3: Search for related papers
        related_papers = await call_tool("search_arxiv_papers", {
            "query": "quantum neural networks",
            "max_results": 2,
            "years_back": 1,
            "include_full_text": False
        })
        
        print(f"Found {len(related_papers)} related papers on quantum neural networks")
        
        return papers, related_papers, stats
        
    except Exception as e:
        print(f"Error: {e}")

async def main():
    """Run all examples."""
    print("arXiv Research MCP Server - Usage Examples")
    print("=" * 50)
    
    await example_basic_search()
    await example_cache_management()
    await example_research_workflow()
    
    print("\n✅ All examples completed successfully!")
    print("\nTo use with MCPO:")
    print("1. Start MCPO: mcpo --config mcpo_config.json")
    print("2. Use the server tools through MCPO clients")
    print("3. Check Docs/MCPO_INTEGRATION_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    asyncio.run(main()) 