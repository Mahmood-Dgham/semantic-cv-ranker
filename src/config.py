"""Configuration management."""
import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class MailConfig:
    """Mail server configuration."""
    host: str
    port: int
    username: str
    password: str
    folder: str
    use_ssl: bool
    
    @classmethod
    def from_env(cls) -> "MailConfig":
        """Create configuration from environment variables."""
        return cls(
            host=os.getenv("IMAP_HOST", "imap.gmail.com"),
            port=int(os.getenv("IMAP_PORT", "993")),
            username=os.getenv("IMAP_USERNAME", ""),
            password=os.getenv("IMAP_PASSWORD", ""),
            folder=os.getenv("IMAP_FOLDER", "INBOX"),
            use_ssl=os.getenv("IMAP_USE_SSL", "true").lower() == "true",
        )


@dataclass
class SchedulerConfig:
    """Scheduler configuration."""
    poll_interval_minutes: int
    
    @classmethod
    def from_env(cls) -> "SchedulerConfig":
        """Create configuration from environment variables."""
        return cls(
            poll_interval_minutes=int(os.getenv("SCHEDULER_POLL_INTERVAL_MINUTES", "2")),
        )


@dataclass
class ExtractionConfig:
    """Extraction configuration."""
    max_attachment_size_mb: int
    tesseract_path: Optional[str]
    
    @classmethod
    def from_env(cls) -> "ExtractionConfig":
        """Create configuration from environment variables."""
        tesseract_path = os.getenv("TESSERACT_PATH", "")
        return cls(
            max_attachment_size_mb=int(os.getenv("MAX_ATTACHMENT_SIZE_MB", "25")),
            tesseract_path=tesseract_path if tesseract_path else None,
        )


@dataclass
class AppConfig:
    """Application configuration."""
    mail: MailConfig
    scheduler: SchedulerConfig
    extraction: ExtractionConfig
    log_level: str
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables."""
        return cls(
            mail=MailConfig.from_env(),
            scheduler=SchedulerConfig.from_env(),
            extraction=ExtractionConfig.from_env(),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
