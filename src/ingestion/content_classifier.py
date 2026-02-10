"""Content classification for CVs, cover letters, etc."""
import logging
import re
from typing import Optional

from .base import ContentType

logger = logging.getLogger(__name__)

# Keywords for CV/Resume detection
CV_KEYWORDS = [
    "curriculum vitae", "resume", "cv", "work experience", "employment history",
    "professional experience", "education", "qualifications", "skills", 
    "references", "work history", "career objective", "professional summary",
    "technical skills", "certifications", "languages spoken", "achievements",
]

# Keywords for cover letter detection
COVER_LETTER_KEYWORDS = [
    "dear hiring manager", "dear sir/madam", "to whom it may concern",
    "i am writing to apply", "i am interested in", "i would like to apply",
    "i am applying for", "position of", "job opening", "application for",
    "enclosed is my resume", "attached is my cv",
]

# Keywords for certificate detection
CERTIFICATE_KEYWORDS = [
    "certificate", "certification", "certified", "license", "accreditation",
    "diploma", "degree", "completion", "achievement", "award",
]

# Filename patterns for CV detection
CV_FILENAME_PATTERNS = [
    r"cv[\._-]", r"resume[\._-]", r"curriculum[\._-]", 
    r"[\._-]cv[\._\.]", r"[\._-]resume[\._\.]",
]


def classify_content(
    text: Optional[str],
    filename: Optional[str] = None,
) -> ContentType:
    """Classify content as CV, cover letter, certificate, or unknown.
    
    Uses heuristic-based classification with keywords and filename patterns.
    
    Args:
        text: Extracted text content
        filename: Optional filename
        
    Returns:
        ContentType classification
    """
    if not text and not filename:
        return ContentType.UNKNOWN
    
    # Normalize text for keyword matching
    text_lower = text.lower() if text else ""
    filename_lower = filename.lower() if filename else ""
    
    # Check filename patterns first
    if filename_lower:
        for pattern in CV_FILENAME_PATTERNS:
            if re.search(pattern, filename_lower):
                logger.debug(f"Classified as CV by filename pattern: {filename}")
                return ContentType.CV
    
    # Count keyword matches
    cv_score = sum(1 for keyword in CV_KEYWORDS if keyword in text_lower)
    cover_letter_score = sum(1 for keyword in COVER_LETTER_KEYWORDS if keyword in text_lower)
    certificate_score = sum(1 for keyword in CERTIFICATE_KEYWORDS if keyword in text_lower)
    
    # Classify based on highest score with thresholds
    if cv_score >= 3:
        logger.debug(f"Classified as CV (score: {cv_score})")
        return ContentType.CV
    elif cover_letter_score >= 2:
        logger.debug(f"Classified as COVER_LETTER (score: {cover_letter_score})")
        return ContentType.COVER_LETTER
    elif certificate_score >= 2:
        logger.debug(f"Classified as CERTIFICATE (score: {certificate_score})")
        return ContentType.CERTIFICATE
    
    # If filename suggests CV but low text score, still classify as CV
    if filename_lower and any(term in filename_lower for term in ["cv", "resume", "curriculum"]):
        if cv_score > 0:
            logger.debug(f"Classified as CV by filename and partial text match")
            return ContentType.CV
    
    # Default to UNKNOWN if uncertain (never discard)
    logger.debug("Classified as UNKNOWN")
    return ContentType.UNKNOWN
