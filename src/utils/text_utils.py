"""Text processing utilities."""

import re
from typing import List


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_author_list(authors: List[str]) -> str:
    """Format author list for display."""
    if not authors:
        return "Unknown"
    
    if len(authors) == 1:
        return authors[0]
    elif len(authors) == 2:
        return f"{authors[0]} and {authors[1]}"
    elif len(authors) <= 5:
        return f"{', '.join(authors[:-1])}, and {authors[-1]}"
    else:
        return f"{', '.join(authors[:3])}, et al."
