"""Configuration settings for the arXiv Research MCP Server."""

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Server Configuration
    SERVER_NAME: str = "arxiv-research-server"
    SERVER_VERSION: str = "1.0.0"

    # arXiv API Configuration
    ARXIV_API_BASE_URL: str = "http://export.arxiv.org/api/query"
    ARXIV_REQUEST_TIMEOUT: int = 30
    ARXIV_MAX_RETRIES: int = 3
    ARXIV_RETRY_DELAY: float = 1.0

    # Rate Limiting
    MAX_CONCURRENT_DOWNLOADS: int = 3
    REQUEST_RATE_LIMIT: float = 1.0  # seconds between requests

    # Content Processing
    MAX_FULL_TEXT_LENGTH: int = 50000
    PDF_TIMEOUT: int = 30
    DEFAULT_MAX_RESULTS: int = 10
    DEFAULT_YEARS_BACK: int = 4

    # Relevance Ranking
    TFIDF_MAX_FEATURES: int = 1000
    TFIDF_NGRAM_RANGE: tuple = (1, 2)
    MIN_RELEVANCE_SCORE: float = 0.1

    # Caching
    CACHE_ENABLED: bool = True
    CACHE_DIR: str = "cache"
    CACHE_TTL_HOURS: int = 24
    REDIS_URL: Optional[str] = None  # If using Redis

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
