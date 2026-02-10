"""PDF text extraction."""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_bytes: bytes) -> Optional[str]:
    """Extract text from PDF using pdfplumber with PyMuPDF as fallback.
    
    Args:
        pdf_bytes: PDF file content as bytes
        
    Returns:
        Extracted text or None if extraction failed
    """
    # Try pdfplumber first
    try:
        import io
        import pdfplumber
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            text_parts = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            text = "\n".join(text_parts)
            if text.strip():
                logger.info(f"Extracted {len(text)} characters from PDF using pdfplumber")
                return text
    except Exception as e:
        logger.warning(f"pdfplumber extraction failed: {e}, trying PyMuPDF")
    
    # Fallback to PyMuPDF
    try:
        import io
        import fitz  # PyMuPDF
        
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        
        text = "\n".join(text_parts)
        if text.strip():
            logger.info(f"Extracted {len(text)} characters from PDF using PyMuPDF")
            return text
    except Exception as e:
        logger.error(f"PyMuPDF extraction failed: {e}")
    
    return None
