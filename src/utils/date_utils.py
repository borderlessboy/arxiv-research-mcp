"""Date utility functions."""

from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def parse_arxiv_date(date_string: str) -> datetime:
    """Parse arXiv date string to datetime object."""
    
    try:
        # arXiv date format: "2024-01-15T18:30:00Z"
        if 'T' in date_string and date_string.endswith('Z'):
            return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        
        # Alternative format: "2024-01-15"
        elif '-' in date_string and len(date_string) >= 10:
            return datetime.strptime(date_string[:10], "%Y-%m-%d")
        
        # Another possible format
        elif '/' in date_string:
            try:
                return datetime.strptime(date_string, "%m/%d/%Y")
            except ValueError:
                try:
                    return datetime.strptime(date_string, "%d/%m/%Y")
                except ValueError:
                    pass
        
        else:
            # Default to current time if parsing fails
            logger.warning(f"Could not parse date: {date_string}")
            return datetime.now()
            
    except ValueError as e:
        logger.warning(f"Error parsing date {date_string}: {e}")
        return datetime.now()


def format_date_for_display(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%B %d, %Y")


def is_recent_paper(paper_date: datetime, days_threshold: int = 30) -> bool:
    """Check if a paper is considered recent."""
    days_old = (datetime.now() - paper_date).days
    return days_old <= days_threshold