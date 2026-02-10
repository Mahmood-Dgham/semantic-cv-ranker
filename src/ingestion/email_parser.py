"""Email parser implementation."""
import logging
from typing import Any

from .base import AttachmentData, EmailData, ProcessingState

logger = logging.getLogger(__name__)


def parse_email(msg: Any) -> EmailData:
    """Parse email message into EmailData object.
    
    Args:
        msg: Email message object from imap-tools
        
    Returns:
        EmailData object
    """
    # Extract basic metadata
    message_id = msg.uid or msg.headers.get("message-id", [""])[0]
    uid = msg.uid
    sender = msg.from_
    subject = msg.subject
    date = msg.date.isoformat() if msg.date else ""
    
    # Extract body
    body_plain = msg.text or None
    body_html = msg.html or None
    
    # Extract attachments
    attachments = []
    inline_images = []
    
    # Process all attachments
    for att in msg.attachments:
        try:
            attachment_data = AttachmentData(
                filename=att.filename or "unnamed",
                content_type=att.content_type or "application/octet-stream",
                payload=att.payload,
                size_bytes=len(att.payload),
            )
            
            # Check if it's an inline image (content-id present or disposition is inline)
            if att.content_disposition == "inline" or hasattr(att, "content_id"):
                inline_images.append(attachment_data)
                logger.debug(f"Found inline image: {attachment_data.filename}")
            else:
                attachments.append(attachment_data)
                logger.debug(f"Found attachment: {attachment_data.filename} ({attachment_data.size_bytes} bytes)")
        except Exception as e:
            logger.error(f"Failed to parse attachment: {e}")
    
    email_data = EmailData(
        message_id=message_id,
        uid=uid,
        sender=sender,
        subject=subject,
        date=date,
        body_plain=body_plain,
        body_html=body_html,
        attachments=attachments,
        inline_images=inline_images,
        state=ProcessingState.UNREAD,
    )
    
    logger.info(
        f"Parsed email: {subject} from {sender} "
        f"({len(attachments)} attachments, {len(inline_images)} inline images)"
    )
    
    return email_data
