#!/usr/bin/env python3
"""Example usage of the arXiv Research MCP Server."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.research_assistant import ResearchAssistant


async def example_basic_search():
    """Example of basic paper search."""
    print("=== Basic Search Example ===")
    
    async with ResearchAssistant("../scripts/run_server.py") as assistant:
        results = await assistant.search_papers(
            query="transformer models",
            max_results=5,
            years_back=2,
            include_full_text=False
        )
        
        print(f"Results:\n{results}")


async def example_full_text_search():
    """Example of search with full text extraction."""
    print("\n=== Full Text Search Example ===")
    
    async with ResearchAssistant("../scripts/run_server.py") as assistant:
        results = await assistant.search_papers(
            query="quantum computing",
            max_results=3,
            years_back=1,
            include_full_text=True
        )
        
        print(f"Results:\n{results}")


async def example_cache_management():
    """Example of cache management."""
    print("\n=== Cache Management Example ===")
    
    async with ResearchAssistant("../scripts/run_server.py") as assistant:
        # Get cache stats
        stats = await assistant.get_cache_stats()
        print(f"Cache Stats:\n{stats}")
        
        # Clear cache
        clear_result = await assistant.clear_cache()
        print(f"\nCache Clear Result:\n{clear_result}")


async def example_multiple_searches():
    """Example of multiple related searches."""
    print("\n=== Multiple Searches Example ===")
    
    topics = [
        "machine learning interpretability",
        "explainable AI",
        "model transparency"
    ]
    
    async with ResearchAssistant("../scripts/run_server.py") as assistant:
        for topic in topics:
            print(f"\nSearching for: {topic}")
            results = await assistant.search_papers(
                query=topic,
                max_results=3,
                years_back=2,
                include_full_text=False
            )
            
            # Extract just the summary for brevity
            lines = results.split('\n')
            summary_lines = [line for line in lines[:10] if line.strip()]
            print('\n'.join(summary_lines))


async def main():
    """Run all examples."""
    try:
        await example_basic_search()
        await example_full_text_search()
        await example_cache_management()
        await example_multiple_searches()
        
        print("\n" + "="*50)
        print("All examples completed successfully!")
        print("="*50)
        
    except Exception as e:
        print(f"Error running examples: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())