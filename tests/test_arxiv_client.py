"""Tests for the arXiv client module."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import httpx

from src.services.arxiv_client import ArxivClient
from src.models.paper import Paper


class TestArxivClient:
    """Test cases for the arXiv client."""
    
    def test_client_initialization(self):
        """Test that the client initializes correctly."""
        client = ArxivClient()
        assert client.base_url == "http://export.arxiv.org/api/query"
        assert client.timeout == 30
        assert client.throttler is not None
    
    def test_build_search_query(self):
        """Test search query building."""
        client = ArxivClient()
        
        # Test simple query
        query = client._build_search_query("transformer models")
        expected = "(ti:transformer OR abs:transformer OR cat:transformer) AND (ti:models OR abs:models OR cat:models)"
        assert query == expected
        
        # Test complex query
        query = client._build_search_query("quantum computing machine learning")
        assert "quantum" in query
        assert "computing" in query
        assert "machine" in query
        assert "learning" in query
    
    def test_filter_by_date(self):
        """Test date filtering functionality."""
        client = ArxivClient()
        
        # Create test papers with different dates
        now = datetime.now()
        old_paper = Mock(spec=Paper)
        old_paper.published = now - timedelta(days=365 * 3)  # 3 years ago
        
        recent_paper = Mock(spec=Paper)
        recent_paper.published = now - timedelta(days=30)  # 30 days ago
        
        papers = [old_paper, recent_paper]
        
        # Filter for papers from last 2 years
        filtered = client._filter_by_date(papers, 2)
        assert len(filtered) == 1
        assert filtered[0] == recent_paper
    
    @pytest.mark.asyncio
    async def test_search_papers_success(self):
        """Test successful paper search."""
        client = ArxivClient()
        
        # Mock response content
        mock_content = b"""<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/1234.5678</id>
                <title>Test Paper Title</title>
                <published>2024-01-15T18:30:00Z</published>
                <summary>This is a test paper abstract.</summary>
                <link href="http://arxiv.org/abs/1234.5678"/>
                <author><name>Test Author</name></author>
                <category term="cs.AI"/>
            </entry>
        </feed>"""
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = Mock()
            mock_response.content = mock_content
            mock_response.raise_for_status = Mock()
            mock_client.get.return_value = mock_response
            
            # Mock cache miss
            with patch.object(client, '_parse_arxiv_response') as mock_parse:
                mock_papers = [Mock(spec=Paper)]
                mock_parse.return_value = mock_papers
                
                with patch.object(client, '_filter_by_date') as mock_filter:
                    mock_filter.return_value = mock_papers
                    
                    result = await client.search_papers("test query", max_results=5, years_back=2)
                    
                    assert len(result) == 1
                    mock_client.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_papers_http_error(self):
        """Test paper search with HTTP error."""
        client = ArxivClient()
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "404 Not Found", request=Mock(), response=Mock()
            )
            mock_client.get.return_value = mock_response
            
            with pytest.raises(httpx.HTTPStatusError):
                await client.search_papers("test query")
    
    def test_parse_arxiv_response(self):
        """Test parsing arXiv API response."""
        client = ArxivClient()
        
        # Mock feedparser response
        mock_entry = Mock()
        mock_entry.id = "http://arxiv.org/abs/1234.5678"
        mock_entry.title = "Test Paper"
        mock_entry.published = "2024-01-15T18:30:00Z"
        mock_entry.summary = "Test abstract"
        mock_entry.link = "http://arxiv.org/abs/1234.5678"
        mock_entry.authors = [Mock(name="Test Author")]
        mock_entry.tags = [Mock(term="cs.AI")]
        
        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        
        with patch('feedparser.parse') as mock_parse:
            mock_parse.return_value = mock_feed
            
            with patch('src.services.arxiv_client.parse_arxiv_date') as mock_date:
                mock_date.return_value = datetime.now()
                
                result = client._parse_arxiv_response(b"mock content")
                
                assert len(result) == 1
                assert result[0].title == "Test Paper"
                assert result[0].arxiv_id == "1234.5678"
    
    def test_parse_arxiv_response_invalid_entry(self):
        """Test parsing with invalid entry."""
        client = ArxivClient()
        
        # Mock feedparser response with invalid entry
        mock_entry = Mock()
        mock_entry.id = "invalid_id"  # Missing required fields
        mock_entry.title = None
        
        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        
        with patch('feedparser.parse') as mock_parse:
            mock_parse.return_value = mock_feed
            
            result = client._parse_arxiv_response(b"mock content")
            
            # Should handle invalid entry gracefully
            assert len(result) == 0


if __name__ == "__main__":
    pytest.main([__file__])
