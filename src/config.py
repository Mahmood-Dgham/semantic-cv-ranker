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
    mark_existing_as_read: bool
    
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
            mark_existing_as_read=os.getenv("MARK_EXISTING_AS_READ", "false").lower() == "true",
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
    mail: MailConfig
    scheduler: SchedulerConfig
    extraction: ExtractionConfig
    database: DatabaseConfig
    log_level: str

#class AppConfig:
    #"""Application configuration."""
    #mail: MailConfig
    #scheduler: SchedulerConfig
    #extraction: ExtractionConfig
    #log_level: str
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables."""

        return cls(
            mail=MailConfig.from_env(),
            scheduler=SchedulerConfig.from_env(),
            extraction=ExtractionConfig.from_env(),
            database=DatabaseConfig.from_env(),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str
    port: int
    user: str
    password: str
    database: str

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        return cls(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", "semantic_cv_ranker"),
        )