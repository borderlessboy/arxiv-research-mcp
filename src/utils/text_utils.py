"""Text processing utilities."""

import re
from typing import List


def clean_abstract(abstract: str) -> str:
    """Clean and format paper abstract."""
    # Remove extra whitespace and newlines
    cleaned = re.sub(r'\s+', ' ', abstract)
    
    # Remove common arXiv formatting artifacts
    cleaned = re.sub(r'^\s*Abstract[:\s]*', '', cleaned, flags=re.IGNORECASE)
    
    return cleaned.strip()


def extract_keywords(text: str) -> List[str]:
    """Extract potential keywords from text."""
    # Simple keyword extraction - could be enhanced with NLP libraries
    
    # Remove common stop words and extract meaningful terms
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
        'those', 'we', 'our', 'us', 'they', 'them', 'their', 'it', 'its'
    }
    
    # Extract words that might be keywords
    words = re.findall(r'\b## src/utils/text_utils.py (continued)

```python
"""Text processing utilities."""

import re
from typing import List


def clean_abstract(abstract: str) -> str:
 """Clean and format paper abstract."""
 # Remove extra whitespace and newlines
 cleaned = re.sub(r'\s+', ' ', abstract)
 
 # Remove common arXiv formatting artifacts
 cleaned = re.sub(r'^\s*Abstract[:\s]*', '', cleaned, flags=re.IGNORECASE)
 
 return cleaned.strip()


def extract_keywords(text: str) -> List[str]:
 """Extract potential keywords from text."""
 # Simple keyword extraction - could be enhanced with NLP libraries
 
 # Remove common stop words and extract meaningful terms
 stop_words = {
 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
 'those', 'we', 'our', 'us', 'they', 'them', 'their', 'it', 'its'
 }
 
 # Extract words that might be keywords
 words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
 keywords = [word for word in words if word not in stop_words]
 
 # Return unique keywords
 return list(set(keywords))


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


def extract_citations(text: str) -> List[str]:
 """Extract potential citations from text."""
 # Simple citation extraction patterns
 citation_patterns = [
 r'\[(\d+)\]', # [1], [2], etc.
 r'\(([^)]+\d{4}[^)]*)\)', # (Author 2023)
 r'et al\.\s*\((\d{4})\)', # et al. (2023)
 ]
 
 citations = []
 for pattern in citation_patterns:
 matches = re.findall(pattern, text)
 citations.extend(matches)
 
 return list(set(citations))