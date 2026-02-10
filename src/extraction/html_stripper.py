"""HTML text extraction."""
import logging
from typing import Optional

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def strip_html_to_text(html_content: str) -> Optional[str]:
    """Strip HTML tags and extract meaningful text.
    
    Args:
        html_content: HTML content as string
        
    Returns:
        Plain text or None if extraction failed
    """
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Remove script and style elements
        for element in soup(["script", "style"]):
            element.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        
        if text.strip():
            logger.info(f"Extracted {len(text)} characters from HTML")
            return text
        
        return None
    except Exception as e:
        logger.error(f"HTML extraction failed: {e}")
        return None
