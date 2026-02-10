"""Base module for ingestion."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ProcessingState(Enum):
    """Email processing state."""
    UNREAD = "unread"
    FETCHED = "fetched"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    DELETED = "deleted"


class ContentType(Enum):
    """Content classification type."""
    CV = "cv"
    COVER_LETTER = "cover_letter"
    CERTIFICATE = "certificate"
    IRRELEVANT = "irrelevant"
    UNKNOWN = "unknown"


@dataclass
class AttachmentData:
    """Attachment data model."""
    filename: str
    content_type: str
    payload: bytes
    size_bytes: int
    extracted_text: Optional[str] = None
    classified_as: ContentType = ContentType.UNKNOWN


@dataclass
class EmailData:
    """Email data model."""
    message_id: str
    uid: str
    sender: str
    subject: str
    date: str
    body_plain: Optional[str] = None
    body_html: Optional[str] = None
    body_text_extracted: Optional[str] = None  # HTML stripped to text
    attachments: list[AttachmentData] = field(default_factory=list)
    inline_images: list[AttachmentData] = field(default_factory=list)
    state: ProcessingState = ProcessingState.UNREAD
    all_extracted_text: Optional[str] = None  # Merged text from all sources
    error: Optional[str] = None


class IngestionSource(ABC):
    """Abstract base class for ingestion sources."""
    
    @abstractmethod
    def connect(self) -> None:
        """Connect to the ingestion source."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the ingestion source."""
        pass
    
    @abstractmethod
    def fetch_emails(self) -> list[EmailData]:
        """Fetch unprocessed emails."""
        pass
    
    @abstractmethod
    def delete_email(self, email: EmailData) -> None:
        """Permanently delete an email."""
        pass
