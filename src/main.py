"""Main entry point for the email ingestion pipeline."""
import logging
import sys

from .config import AppConfig
from .ingestion.imap_client import IMAPClient
from .ingestion.attachment_handler import AttachmentHandler
from .ingestion.scheduler import EmailScheduler
from .ingestion.base import ProcessingState
from .extraction.html_stripper import strip_html_to_text

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def merge_all_text(email, body_text_extracted):
    """Merge all extracted text from email into one block.
    
    Args:
        email: EmailData object
        body_text_extracted: Extracted text from HTML body
        
    Returns:
        Merged text string
    """
    text_parts = []
    
    # Add email body (plain text preferred, then HTML-extracted)
    if email.body_plain:
        text_parts.append("=== EMAIL BODY (PLAIN) ===")
        text_parts.append(email.body_plain)
    elif body_text_extracted:
        text_parts.append("=== EMAIL BODY (HTML) ===")
        text_parts.append(body_text_extracted)
    
    # Add attachment texts
    for att in email.attachments:
        if att.extracted_text:
            text_parts.append(f"\n=== ATTACHMENT: {att.filename} ===")
            text_parts.append(att.extracted_text)
    
    # Add inline image texts
    for img in email.inline_images:
        if img.extracted_text:
            text_parts.append(f"\n=== INLINE IMAGE: {img.filename} ===")
            text_parts.append(img.extracted_text)
    
    return "\n".join(text_parts) if text_parts else None


def process_emails():
    """Main email processing function."""
    config = AppConfig.from_env()
    
    # Validate configuration
    if not config.mail.username or not config.mail.password:
        logger.error("IMAP credentials not configured. Please set IMAP_USERNAME and IMAP_PASSWORD")
        return
    
    # Create IMAP client
    client = IMAPClient(
        host=config.mail.host,
        port=config.mail.port,
        username=config.mail.username,
        password=config.mail.password,
        folder=config.mail.folder,
        use_ssl=config.mail.use_ssl,
    )
    
    # Create attachment handler
    handler = AttachmentHandler(
        max_size_mb=config.extraction.max_attachment_size_mb,
        tesseract_path=config.extraction.tesseract_path,
    )
    
    try:
        # Connect to IMAP
        client.connect()
        
        # Mark all existing emails as read if configured
        if config.mail.mark_existing_as_read:
            logger.info("MARK_EXISTING_AS_READ is enabled - marking all existing emails as read")
            try:
                client.mark_all_as_read()
                logger.info("Ignoring all existing emails, only processing new emails from now on")
            except Exception as e:
                logger.error(f"Failed to mark existing emails as read: {e}")
        
        # Fetch emails
        emails = client.fetch_emails()
        logger.info(f"Poll cycle: found {len(emails)} emails to process")
        
        processed_count = 0
        failed_count = 0
        
        # Process each email
        for email in emails:
            try:
                email.state = ProcessingState.PROCESSING
                logger.info(f"Processing email: {email.subject} from {email.sender}")
                
                # Extract text from HTML body if present
                body_text_extracted = None
                if email.body_html:
                    body_text_extracted = strip_html_to_text(email.body_html)
                    email.body_text_extracted = body_text_extracted
                
                # Process attachments
                for attachment in email.attachments:
                    handler.process_attachment(attachment)
                
                # Process inline images
                for inline_image in email.inline_images:
                    handler.process_attachment(inline_image)
                
                # Merge all extracted text
                email.all_extracted_text = merge_all_text(email, body_text_extracted)
                
                # Mark as processed
                email.state = ProcessingState.PROCESSED
                
                # Log summary
                total_text_length = len(email.all_extracted_text) if email.all_extracted_text else 0
                logger.info(
                    f"Successfully processed email: {email.subject} "
                    f"(extracted {total_text_length} total chars)"
                )
                
                # Delete email permanently
                client.delete_email(email)
                processed_count += 1
                
            except Exception as e:
                email.state = ProcessingState.FAILED
                email.error = str(e)
                logger.error(
                    f"Failed to process email {email.subject} (UID: {email.uid}): {e}",
                    exc_info=True
                )
                failed_count += 1
                # Continue with next email
        
        logger.info(
            f"Poll cycle complete: {processed_count} processed, {failed_count} failed"
        )
        
    except Exception as e:
        logger.error(f"Error during email processing: {e}", exc_info=True)
    finally:
        # Disconnect
        client.disconnect()


def main():
    """Main entry point."""
    logger.info("Starting Semantic CV Ranker - Phase 0: Email Ingestion Pipeline")
    
    # Load configuration
    config = AppConfig.from_env()
    
    # Set log level from config
    logging.getLogger().setLevel(config.log_level)
    
    # Create and start scheduler
    scheduler = EmailScheduler(
        poll_interval_minutes=config.scheduler.poll_interval_minutes
    )
    
    logger.info(f"Configuration loaded: polling every {config.scheduler.poll_interval_minutes} minutes")
    
    # Start scheduler (this blocks until shutdown signal)
    scheduler.start(process_emails)


if __name__ == "__main__":
    main()
