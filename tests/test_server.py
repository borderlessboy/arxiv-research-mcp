"""Tests for the MCP server module."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from mcp import types

from src.server import app, search_arxiv_papers_tool, clear_cache_tool, get_cache_stats_tool


class TestServer:
    """Test cases for the MCP server."""
    
    def test_server_initialization(self):
        """Test that the server initializes correctly."""
        assert app is not None
        assert hasattr(app, 'list_tools')
        assert hasattr(app, 'call_tool')
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test that list_tools returns the expected tools."""
        tools = await app.list_tools()
        
        assert isinstance(tools, list)
        assert len(tools) == 3
        
        tool_names = [tool.name for tool in tools]
        assert "search_arxiv_papers" in tool_names
        assert "clear_cache" in tool_names
        assert "get_cache_stats" in tool_names
    
    @pytest.mark.asyncio
    async def test_search_arxiv_papers_tool_success(self):
        """Test successful paper search."""
        with patch('src.server.arxiv_client.search_papers') as mock_search, \
             patch('src.server.cache_manager.get_cached_results') as mock_cache, \
             patch('src.server.relevance_ranker.rank_papers') as mock_rank, \
             patch('src.server.relevance_ranker.select_top_papers') as mock_select:
            
            # Mock cache miss
            mock_cache.return_value = None
            
            # Mock search results
            mock_papers = [Mock(title="Test Paper", authors=["Test Author"])]
            mock_search.return_value = mock_papers
            
            # Mock ranking
            mock_rank.return_value = mock_papers
            mock_select.return_value = mock_papers
            
            arguments = {
                "query": "test query",
                "max_results": 5,
                "years_back": 2,
                "include_full_text": False
            }
            
            result = await search_arxiv_papers_tool(arguments)
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Test Paper" in result[0].text
    
    @pytest.mark.asyncio
    async def test_search_arxiv_papers_tool_cache_hit(self):
        """Test paper search with cache hit."""
        with patch('src.server.cache_manager.get_cached_results') as mock_cache, \
             patch('src.server.relevance_ranker.rank_papers') as mock_rank, \
             patch('src.server.relevance_ranker.select_top_papers') as mock_select:
            
            # Mock cache hit
            mock_papers = [Mock(title="Cached Paper", authors=["Cached Author"])]
            mock_cache.return_value = mock_papers
            
            # Mock ranking
            mock_rank.return_value = mock_papers
            mock_select.return_value = mock_papers
            
            arguments = {
                "query": "cached query",
                "max_results": 3,
                "years_back": 1,
                "include_full_text": False
            }
            
            result = await search_arxiv_papers_tool(arguments)
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Cached Paper" in result[0].text
    
    @pytest.mark.asyncio
    async def test_search_arxiv_papers_tool_no_results(self):
        """Test paper search with no results."""
        with patch('src.server.arxiv_client.search_papers') as mock_search, \
             patch('src.server.cache_manager.get_cached_results') as mock_cache:
            
            # Mock cache miss and no search results
            mock_cache.return_value = None
            mock_search.return_value = []
            
            arguments = {
                "query": "nonexistent query",
                "max_results": 10,
                "years_back": 1,
                "include_full_text": False
            }
            
            result = await search_arxiv_papers_tool(arguments)
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].type == "text"
            assert "No papers found" in result[0].text
    
    @pytest.mark.asyncio
    async def test_clear_cache_tool_success(self):
        """Test successful cache clearing."""
        with patch('src.server.cache_manager.clear_cache') as mock_clear:
            mock_clear.return_value = 5
            
            result = await clear_cache_tool()
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Cache cleared successfully" in result[0].text
            assert "5" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_cache_stats_tool_success(self):
        """Test successful cache stats retrieval."""
        with patch('src.server.cache_manager.get_cache_stats') as mock_stats:
            mock_stats.return_value = {
                "enabled": True,
                "total_entries": 10,
                "total_size_mb": 2.5,
                "cache_dir": "/cache",
                "ttl_hours": 24
            }
            
            result = await get_cache_stats_tool()
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Cache Statistics" in result[0].text
            assert "10" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_cache_stats_tool_disabled(self):
        """Test cache stats when cache is disabled."""
        with patch('src.server.cache_manager.get_cache_stats') as mock_stats:
            mock_stats.return_value = {"enabled": False}
            
            result = await get_cache_stats_tool()
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Cache is disabled" in result[0].text


if __name__ == "__main__":
    pytest.main([__file__])
