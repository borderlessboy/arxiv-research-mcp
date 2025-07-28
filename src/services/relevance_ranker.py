"""Relevance ranking service using TF-IDF and cosine similarity."""

import logging
import re
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.models.paper import Paper
from config.settings import settings

logger = logging.getLogger(__name__)


class RelevanceRanker:
    """Service for ranking papers by relevance to a query."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=settings.TFIDF_MAX_FEATURES,
            ngram_range=settings.TFIDF_NGRAM_RANGE,
            lowercase=True,
            token_pattern=r"\b[a-zA-Z][a-zA-Z0-9]*\b",
        )

    def rank_papers(self, papers: List[Paper], query: str) -> List[Paper]:
        """Rank papers by relevance to the query."""

        if not papers:
            return papers

        logger.info(f"Ranking {len(papers)} papers for relevance to: {query}")

        try:
            # Prepare text data for vectorization
            paper_texts = self._prepare_paper_texts(papers)

            # Create corpus with papers and query
            all_texts = paper_texts + [self._clean_text(query)]

            # Vectorize all texts
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)

            # Calculate similarities
            query_vector = tfidf_matrix[-1]  # Last item is the query
            paper_vectors = tfidf_matrix[:-1]

            similarities = cosine_similarity(query_vector, paper_vectors).flatten()

            # Add relevance scores to papers
            for i, paper in enumerate(papers):
                paper.relevance_score = float(similarities[i])

            # Filter out papers with very low relevance
            # Use a more lenient threshold for real-world papers
            effective_min_score = 0.001  # Very low threshold to include most papers
            logger.info(
                f"Effective minimum relevance score threshold: {effective_min_score}"
            )

            filtered_papers = [
                paper
                for paper in papers
                if paper.relevance_score >= effective_min_score
            ]

            logger.info(f"Papers before filtering: {len(papers)}")
            logger.info(f"Papers after filtering: {len(filtered_papers)}")

            # Log some sample scores for debugging
            if papers:
                sample_scores = [paper.relevance_score for paper in papers[:5]]
                logger.info(f"Sample relevance scores: {sample_scores}")

            # Sort by relevance score (descending)
            ranked_papers = sorted(
                filtered_papers, key=lambda x: x.relevance_score, reverse=True
            )

            if ranked_papers:
                logger.info(
                    f"Ranked papers, scores range: {ranked_papers[0].relevance_score:.3f} to {ranked_papers[-1].relevance_score:.3f}"
                )
            else:
                logger.info("No papers remained after relevance filtering")

            return ranked_papers

        except Exception as e:
            logger.error(f"Error ranking papers: {e}")
            # Return papers without ranking if there's an error
            for paper in papers:
                paper.relevance_score = 0.0
            return papers

    def select_top_papers(self, papers: List[Paper], count: int) -> List[Paper]:
        """Select the top N most relevant papers."""
        return papers[:count]

    def _prepare_paper_texts(self, papers: List[Paper]) -> List[str]:
        """Prepare paper texts for vectorization."""
        texts = []

        for paper in papers:
            # Combine title, summary, and categories for relevance scoring
            text_parts = [paper.title, paper.summary, " ".join(paper.categories)]

            # Include full text if available (with weight adjustment)
            if paper.full_text:
                # Give less weight to full text to avoid overwhelming title/abstract
                full_text_sample = paper.full_text[:2000]  # First 2000 chars
                text_parts.append(full_text_sample)

            combined_text = " ".join(text_parts)
            cleaned_text = self._clean_text(combined_text)
            texts.append(cleaned_text)

        return texts

    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text for better vectorization."""
        # Remove extra whitespace and newlines
        text = re.sub(r"\s+", " ", text)

        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r"[^\w\s]", " ", text)

        # Remove numbers (often not useful for relevance)
        text = re.sub(r"\b\d+\b", "", text)

        # Remove very short words
        text = " ".join([word for word in text.split() if len(word) > 2])

        return text.strip()
