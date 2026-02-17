"""IMAP client implementation."""
import datetime
import logging
from typing import Optional

from imap_tools import MailBox, AND

from .base import EmailData, IngestionSource, ProcessingState
from .email_parser import parse_email

logger = logging.getLogger(__name__)


class IMAPClient(IngestionSource):
    """IMAP client for email ingestion."""
    
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        folder: str = "INBOX",
        use_ssl: bool = True,
    ):
        """Initialize IMAP client.
        
        Args:
            host: IMAP server host
            port: IMAP server port
            username: IMAP username
            password: IMAP password
            folder: IMAP folder to monitor
            use_ssl: Whether to use SSL connection
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.folder = folder
        self.use_ssl = use_ssl
        self._mailbox: Optional[MailBox] = None
        # Record the time we start monitoring (only set once, not on reconnects)
        self._start_time: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
    
    def connect(self) -> None:
        """Connect to IMAP server."""
        try:
            if self.use_ssl:
                self._mailbox = MailBox(self.host, self.port)
            else:
                # For non-SSL connections (use with caution)
                from imap_tools import MailBoxUnencrypted
                self._mailbox = MailBoxUnencrypted(self.host, self.port)
            
            self._mailbox.login(self.username, self.password)
            self._mailbox.folder.set(self.folder)
            
            logger.info(f"Connected to IMAP server {self.host}:{self.port}, folder: {self.folder}")
            logger.info(f"Will only process emails received after {self._start_time}")
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {e}")
            raise
    
    def disconnect(self) -> None:
        """Disconnect from IMAP server."""
        if self._mailbox:
            try:
                self._mailbox.logout()
                logger.info("Disconnected from IMAP server")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
            finally:
                self._mailbox = None
    
    def fetch_emails(self) -> list[EmailData]:
        """Fetch unseen emails received after the system started.
        
        Returns:
            List of EmailData objects
        """
        if not self._mailbox:
            raise RuntimeError("Not connected to IMAP server")
        
        try:
            # Only fetch unseen emails received after the system started
            start_date = self._start_time.date()
            
            # Fetch unseen emails from start_date onwards
            emails = []
            for msg in self._mailbox.fetch(AND(seen=False, date_gte=start_date)):
                # Additionally check the exact datetime since IMAP date filter is date-only (no time)
                if msg.date:
                    # Make msg.date timezone-aware if needed for comparison
                    msg_date = msg.date
                    if msg_date.tzinfo is None:
                        msg_date = msg_date.replace(tzinfo=datetime.timezone.utc)
                    
                    if msg_date < self._start_time:
                        logger.debug(f"Skipping old email: {msg.subject} (received {msg_date})")
                        continue
                
                try:
                    email_data = parse_email(msg)
                    email_data.state = ProcessingState.FETCHED
                    emails.append(email_data)
                    logger.info(f"Fetched email: {email_data.subject} from {email_data.sender}")
                except Exception as e:
                    logger.error(f"Failed to parse email: {e}")
            
            logger.info(f"Fetched {len(emails)} unseen emails")
            return emails
        except Exception as e:
            logger.error(f"Failed to fetch emails: {e}")
            return []
    
    def delete_email(self, email: EmailData) -> None:
        """Permanently delete an email.
        
        Args:
            email: Email to delete
        """
        if not self._mailbox:
            raise RuntimeError("Not connected to IMAP server")
        
        try:
            # Delete by UID and expunge
            self._mailbox.delete([email.uid])
            self._mailbox.expunge()
            email.state = ProcessingState.DELETED
            logger.info(f"Deleted email: {email.subject} (UID: {email.uid})")
        except Exception as e:
            logger.error(f"Failed to delete email {email.uid}: {e}")
            raise
    
    def mark_all_as_read(self) -> None:
        """Mark all existing emails as read. Call once on first setup."""
        if not self._mailbox:
            raise RuntimeError("Not connected to IMAP server")
        
        try:
            count = 0
            for msg in self._mailbox.fetch(AND(seen=False)):
                self._mailbox.seen([msg.uid], True)
                count += 1
            logger.info(f"Marked {count} existing emails as read")
        except Exception as e:
            logger.error(f"Failed to mark emails as read: {e}")
            raise
