"""Data models for research papers."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field


class Author(BaseModel):
    """Author information."""
    name: str
    affiliation: Optional[str] = None


class Paper(BaseModel):
    """Research paper model."""
    
    title: str
    authors: List[str]
    published: datetime
    summary: str
    url: HttpUrl
    pdf_url: HttpUrl
    categories: List[str]
    
    # Enhanced fields
    relevance_score: Optional[float] = None
    full_text: Optional[str] = None
    processed_at: Optional[datetime] = None
    
    # Metadata
    arxiv_id: Optional[str] = None
    doi: Optional[str] = None
    journal: Optional[str] = None
    
    model_config = {
        "json_encoders": {
            datetime: lambda dt: dt.isoformat(),
            HttpUrl: str
        },
        "arbitrary_types_allowed": True
    }


class SearchRequest(BaseModel):
    """Search request model."""
    
    query: str = Field(..., description="Search query string")
    max_results: int = Field(default=10, ge=1, le=50, description="Maximum number of results")
    years_back: int = Field(default=4, ge=1, le=20, description="Years to search back")
    include_full_text: bool = Field(default=True, description="Include full paper text")
    
    
class SearchResponse(BaseModel):
    """Search response model."""
    
    papers: List[Paper]
    total_found: int
    query: str
    search_time_seconds: float
    cached: bool = False