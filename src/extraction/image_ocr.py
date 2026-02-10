"""Image OCR text extraction."""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text_from_image(
    image_bytes: bytes, 
    tesseract_path: Optional[str] = None
) -> Optional[str]:
    """Extract text from image using OCR.
    
    Args:
        image_bytes: Image file content as bytes
        tesseract_path: Optional path to tesseract executable
        
    Returns:
        Extracted text or None if extraction failed
    """
    try:
        import io
        from PIL import Image
        import pytesseract
        
        # Set tesseract path if provided
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Open image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Extract text
        text = pytesseract.image_to_string(image)
        
        if text.strip():
            logger.info(f"Extracted {len(text)} characters from image using OCR")
            return text
        
        return None
    except Exception as e:
        logger.error(f"Image OCR extraction failed: {e}")
        return None
