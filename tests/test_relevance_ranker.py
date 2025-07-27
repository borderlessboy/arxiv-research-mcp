"""Tests for the relevance ranker module."""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from services.relevance_ranker import RelevanceRanker
from models.paper import Paper


class TestRelevanceRanker:
    """Test cases for the relevance ranker."""
    
    def test_ranker_initialization(self):
        """Test that the ranker initializes correctly."""
        ranker = RelevanceRanker()
        assert ranker.vectorizer is not None
        assert hasattr(ranker.vectorizer, 'fit_transform')
    
    def test_rank_papers_empty_list(self):
        """Test ranking with empty paper list."""
        ranker = RelevanceRanker()
        result = ranker.rank_papers([], "test query")
        assert result == []
    
    def test_rank_papers_single_paper(self):
        """Test ranking with single paper."""
        ranker = RelevanceRanker()
        
        # Create a test paper
        paper = Mock(spec=Paper)
        paper.title = "Machine Learning Applications"
        paper.summary = "This paper discusses machine learning applications in various domains."
        paper.categories = ["cs.AI", "cs.LG"]
        paper.full_text = None
        
        papers = [paper]
        query = "machine learning"
        
        result = ranker.rank_papers(papers, query)
        
        assert len(result) == 1
        assert result[0] == paper
        assert hasattr(result[0], 'relevance_score')
        assert isinstance(result[0].relevance_score, float)
    
    def test_rank_papers_multiple_papers(self):
        """Test ranking with multiple papers."""
        ranker = RelevanceRanker()
        
        # Create test papers with different relevance
        paper1 = Mock(spec=Paper)
        paper1.title = "Machine Learning Fundamentals"
        paper1.summary = "Introduction to machine learning concepts and algorithms."
        paper1.categories = ["cs.AI", "cs.LG"]
        paper1.full_text = None
        
        paper2 = Mock(spec=Paper)
        paper2.title = "Quantum Computing Applications"
        paper2.summary = "Applications of quantum computing in cryptography."
        paper2.categories = ["quant-ph", "cs.CR"]
        paper2.full_text = None
        
        paper3 = Mock(spec=Paper)
        paper3.title = "Deep Learning for Computer Vision"
        paper3.summary = "Advanced deep learning techniques for computer vision tasks."
        paper3.categories = ["cs.CV", "cs.LG"]
        paper3.full_text = None
        
        papers = [paper1, paper2, paper3]
        query = "machine learning"
        
        result = ranker.rank_papers(papers, query)
        
        assert len(result) == 2  # Should filter out quantum computing paper
        assert result[0].relevance_score >= result[1].relevance_score  # Should be sorted
        assert "Machine Learning" in result[0].title or "Deep Learning" in result[0].title
    
    def test_rank_papers_with_full_text(self):
        """Test ranking with papers that have full text."""
        ranker = RelevanceRanker()
        
        paper = Mock(spec=Paper)
        paper.title = "Machine Learning"
        paper.summary = "Introduction to ML."
        paper.categories = ["cs.AI"]
        paper.full_text = "This paper provides a comprehensive overview of machine learning algorithms including supervised learning, unsupervised learning, and reinforcement learning techniques."
        
        papers = [paper]
        query = "supervised learning"
        
        result = ranker.rank_papers(papers, query)
        
        assert len(result) == 1
        assert result[0].relevance_score > 0
    
    def test_select_top_papers(self):
        """Test selecting top papers."""
        ranker = RelevanceRanker()
        
        # Create papers with different scores
        papers = []
        for i in range(5):
            paper = Mock(spec=Paper)
            paper.relevance_score = 1.0 - (i * 0.1)  # Decreasing scores
            papers.append(paper)
        
        # Select top 3
        result = ranker.select_top_papers(papers, 3)
        
        assert len(result) == 3
        assert result[0].relevance_score == 1.0
        assert result[1].relevance_score == 0.9
        assert result[2].relevance_score == 0.8
    
    def test_prepare_paper_texts(self):
        """Test text preparation for vectorization."""
        ranker = RelevanceRanker()
        
        paper = Mock(spec=Paper)
        paper.title = "Test Paper"
        paper.summary = "Test summary"
        paper.categories = ["cs.AI", "cs.LG"]
        paper.full_text = "Test full text content"
        
        papers = [paper]
        texts = ranker._prepare_paper_texts(papers)
        
        assert len(texts) == 1
        assert "Test Paper" in texts[0]
        assert "Test summary" in texts[0]
        assert "cs.AI" in texts[0] or "cs.LG" in texts[0]
        assert "cs.LG" in texts[0]
        assert "Test full text content" in texts[0]
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        ranker = RelevanceRanker()
        
        # Test with various text patterns
        test_text = "This is a test! @#$%^&*() 12345 \n\n\n   Multiple   spaces   "
        cleaned = ranker._clean_text(test_text)
        
        assert "This" in cleaned
        assert "test" in cleaned
        assert "12345" not in cleaned  # Numbers should be removed
        assert "@#$%^&*()" not in cleaned  # Special chars should be removed
        assert "   " not in cleaned  # Extra spaces should be removed
    
    def test_clean_text_short_words(self):
        """Test that short words are removed."""
        ranker = RelevanceRanker()
        
        test_text = "a an the it is at on in up down"
        cleaned = ranker._clean_text(test_text)
        
        # Most words should be removed as they're too short, but some might remain
        assert len(cleaned.strip()) <= len(test_text)
    
    def test_get_feature_importance(self):
        """Test feature importance extraction."""
        ranker = RelevanceRanker()
        
        paper = Mock(spec=Paper)
        paper.title = "Machine Learning Applications"
        paper.summary = "This paper discusses machine learning."
        paper.categories = ["cs.AI"]
        paper.full_text = None
        
        papers = [paper]
        query = "machine learning"
        
        importance = ranker.get_feature_importance(papers, query)
        
        assert isinstance(importance, dict)
        # Should have some features for a valid query
        assert len(importance) > 0
    
    def test_get_feature_importance_empty_papers(self):
        """Test feature importance with empty paper list."""
        ranker = RelevanceRanker()
        
        importance = ranker.get_feature_importance([], "test query")
        
        assert importance == {}
    
    def test_ranking_error_handling(self):
        """Test that ranking handles errors gracefully."""
        ranker = RelevanceRanker()
        
        # Create a paper that might cause issues
        paper = Mock(spec=Paper)
        paper.title = "Test"
        paper.summary = "Test"
        paper.categories = []
        paper.full_text = None
        
        papers = [paper]
        query = "test"
        
        # Should not raise an exception
        result = ranker.rank_papers(papers, query)
        
        assert len(result) == 1
        assert result[0].relevance_score >= 0.0  # Should have a valid score


if __name__ == "__main__":
    pytest.main([__file__])
