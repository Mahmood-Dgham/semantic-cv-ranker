"""Attachment handling and routing."""
import io
import logging
import zipfile
from typing import Optional

from .base import AttachmentData, ContentType
from .content_classifier import classify_content
from ..extraction.pdf_extractor import extract_text_from_pdf
from ..extraction.docx_extractor import extract_text_from_docx
from ..extraction.html_stripper import strip_html_to_text
from ..extraction.image_ocr import extract_text_from_image

logger = logging.getLogger(__name__)


class AttachmentHandler:
    """Handle attachment extraction and classification."""
    
    def __init__(
        self,
        max_size_mb: int = 25,
        tesseract_path: Optional[str] = None,
    ):
        """Initialize attachment handler.
        
        Args:
            max_size_mb: Maximum attachment size in MB
            tesseract_path: Optional path to tesseract executable
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.tesseract_path = tesseract_path
    
    def process_attachment(self, attachment: AttachmentData) -> None:
        """Process a single attachment: extract text and classify.
        
        Args:
            attachment: AttachmentData object to process (modified in place)
        """
        # Check size limit
        if attachment.size_bytes > self.max_size_bytes:
            logger.warning(
                f"Attachment {attachment.filename} exceeds size limit "
                f"({attachment.size_bytes / 1024 / 1024:.2f}MB > "
                f"{self.max_size_bytes / 1024 / 1024:.2f}MB), skipping"
            )
            attachment.classified_as = ContentType.IRRELEVANT
            return
        
        # Route by MIME type
        content_type = attachment.content_type.lower()
        text = None
        
        try:
            if "application/pdf" in content_type:
                text = self._extract_pdf(attachment)
            elif "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in content_type:
                text = self._extract_docx(attachment)
            elif "application/msword" in content_type:
                text = self._extract_docx(attachment)
            elif "text/html" in content_type:
                text = self._extract_html(attachment)
            elif "text/plain" in content_type:
                text = self._extract_plain_text(attachment)
            elif any(img_type in content_type for img_type in ["image/jpeg", "image/png", "image/tiff", "image/jpg"]):
                text = self._extract_image(attachment)
            elif "application/zip" in content_type or "application/x-zip-compressed" in content_type:
                text = self._extract_zip(attachment)
            else:
                logger.warning(f"Unsupported content type: {content_type} for {attachment.filename}")
                attachment.classified_as = ContentType.UNKNOWN
                return
            
            attachment.extracted_text = text
            
            # Classify content
            attachment.classified_as = classify_content(text, attachment.filename)
            
            logger.info(
                f"Processed attachment {attachment.filename}: "
                f"extracted {len(text) if text else 0} chars, "
                f"classified as {attachment.classified_as.value}"
            )
        except Exception as e:
            logger.error(f"Failed to process attachment {attachment.filename}: {e}")
            attachment.classified_as = ContentType.UNKNOWN
    
    def _extract_pdf(self, attachment: AttachmentData) -> Optional[str]:
        """Extract text from PDF."""
        return extract_text_from_pdf(attachment.payload)
    
    def _extract_docx(self, attachment: AttachmentData) -> Optional[str]:
        """Extract text from DOCX."""
        return extract_text_from_docx(attachment.payload)
    
    def _extract_html(self, attachment: AttachmentData) -> Optional[str]:
        """Extract text from HTML."""
        html_content = attachment.payload.decode("utf-8", errors="ignore")
        return strip_html_to_text(html_content)
    
    def _extract_plain_text(self, attachment: AttachmentData) -> Optional[str]:
        """Extract plain text."""
        try:
            return attachment.payload.decode("utf-8", errors="ignore")
        except Exception as e:
            logger.error(f"Failed to decode plain text: {e}")
            return None
    
    def _extract_image(self, attachment: AttachmentData) -> Optional[str]:
        """Extract text from image using OCR."""
        return extract_text_from_image(attachment.payload, self.tesseract_path)
    
    def _extract_zip(self, attachment: AttachmentData) -> Optional[str]:
        """Extract and process contents of ZIP archive.
        
        Returns combined text from all files in the archive.
        """
        try:
            with zipfile.ZipFile(io.BytesIO(attachment.payload)) as zf:
                all_text = []
                for filename in zf.namelist():
                    # Skip directories and hidden files
                    if filename.endswith("/") or filename.startswith("."):
                        continue
                    
                    try:
                        file_data = zf.read(filename)
                        file_size = len(file_data)
                        
                        # Check size limit
                        if file_size > self.max_size_bytes:
                            logger.warning(f"File {filename} in ZIP exceeds size limit, skipping")
                            continue
                        
                        # Detect content type by extension
                        file_lower = filename.lower()
                        text = None
                        
                        if file_lower.endswith(".pdf"):
                            text = extract_text_from_pdf(file_data)
                        elif file_lower.endswith((".docx", ".doc")):
                            text = extract_text_from_docx(file_data)
                        elif file_lower.endswith(".html"):
                            html_content = file_data.decode("utf-8", errors="ignore")
                            text = strip_html_to_text(html_content)
                        elif file_lower.endswith(".txt"):
                            text = file_data.decode("utf-8", errors="ignore")
                        elif file_lower.endswith((".jpg", ".jpeg", ".png", ".tiff")):
                            text = extract_text_from_image(file_data, self.tesseract_path)
                        else:
                            logger.debug(f"Unsupported file type in ZIP: {filename}")
                            continue
                        
                        if text:
                            all_text.append(f"--- {filename} ---\n{text}")
                            logger.debug(f"Extracted {len(text)} chars from {filename} in ZIP")
                    except Exception as e:
                        logger.error(f"Failed to extract {filename} from ZIP: {e}")
                
                if all_text:
                    return "\n\n".join(all_text)
                return None
        except Exception as e:
            logger.error(f"Failed to process ZIP archive: {e}")
            return None
