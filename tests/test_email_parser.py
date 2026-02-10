"""Tests for email parser."""
import pytest
from datetime import datetime


class TestEmailParser:
    """Tests for email parsing."""
    
    def test_parse_email_basic(self, mocker):
        """Test basic email parsing."""
        from src.ingestion.email_parser import parse_email
        from src.ingestion.base import ProcessingState
        
        # Mock email message
        mock_msg = mocker.MagicMock()
        mock_msg.uid = "12345"
        mock_msg.from_ = "sender@example.com"
        mock_msg.subject = "Test Subject"
        mock_msg.date = datetime(2024, 1, 1, 12, 0, 0)
        mock_msg.text = "Plain text body"
        mock_msg.html = "<html><body>HTML body</body></html>"
        mock_msg.headers.get.return_value = ["<msg-id-123>"]
        mock_msg.attachments = []
        
        email_data = parse_email(mock_msg)
        
        assert email_data.uid == "12345"
        assert email_data.sender == "sender@example.com"
        assert email_data.subject == "Test Subject"
        assert email_data.body_plain == "Plain text body"
        assert email_data.body_html == "<html><body>HTML body</body></html>"
        assert email_data.state == ProcessingState.UNREAD
        assert len(email_data.attachments) == 0
    
    def test_parse_email_with_attachments(self, mocker):
        """Test email parsing with attachments."""
        from src.ingestion.email_parser import parse_email
        
        # Mock attachment
        mock_att = mocker.MagicMock()
        mock_att.filename = "document.pdf"
        mock_att.content_type = "application/pdf"
        mock_att.payload = b"fake pdf content"
        mock_att.content_disposition = "attachment"
        # Explicitly set content_id to None and remove from hasattr check
        mock_att.content_id = None
        del mock_att.content_id  # Remove the attribute
        
        # Mock email message
        mock_msg = mocker.MagicMock()
        mock_msg.uid = "12345"
        mock_msg.from_ = "sender@example.com"
        mock_msg.subject = "Test with attachment"
        mock_msg.date = datetime(2024, 1, 1, 12, 0, 0)
        mock_msg.text = "See attachment"
        mock_msg.html = None
        mock_msg.headers.get.return_value = ["<msg-id-123>"]
        mock_msg.attachments = [mock_att]
        
        email_data = parse_email(mock_msg)
        
        assert len(email_data.attachments) == 1
        assert email_data.attachments[0].filename == "document.pdf"
        assert email_data.attachments[0].content_type == "application/pdf"
        assert email_data.attachments[0].size_bytes == len(b"fake pdf content")
    
    def test_parse_email_with_inline_images(self, mocker):
        """Test email parsing with inline images."""
        from src.ingestion.email_parser import parse_email
        
        # Mock inline image
        mock_img = mocker.MagicMock()
        mock_img.filename = "image.jpg"
        mock_img.content_type = "image/jpeg"
        mock_img.payload = b"fake image content"
        mock_img.content_disposition = "inline"
        mock_img.content_id = "<image123>"
        
        # Mock email message
        mock_msg = mocker.MagicMock()
        mock_msg.uid = "12345"
        mock_msg.from_ = "sender@example.com"
        mock_msg.subject = "Test with image"
        mock_msg.date = datetime(2024, 1, 1, 12, 0, 0)
        mock_msg.text = "See image"
        mock_msg.html = "<html><img src='cid:image123'/></html>"
        mock_msg.headers.get.return_value = ["<msg-id-123>"]
        mock_msg.attachments = [mock_img]
        
        email_data = parse_email(mock_msg)
        
        assert len(email_data.inline_images) == 1
        assert email_data.inline_images[0].filename == "image.jpg"
        assert len(email_data.attachments) == 0
    
    def test_parse_email_no_date(self, mocker):
        """Test email parsing without date."""
        from src.ingestion.email_parser import parse_email
        
        mock_msg = mocker.MagicMock()
        mock_msg.uid = "12345"
        mock_msg.from_ = "sender@example.com"
        mock_msg.subject = "No date"
        mock_msg.date = None
        mock_msg.text = "Test"
        mock_msg.html = None
        mock_msg.headers.get.return_value = ["<msg-id-123>"]
        mock_msg.attachments = []
        
        email_data = parse_email(mock_msg)
        
        assert email_data.date == ""
    
    def test_parse_email_unnamed_attachment(self, mocker):
        """Test email parsing with unnamed attachment."""
        from src.ingestion.email_parser import parse_email
        
        mock_att = mocker.MagicMock()
        mock_att.filename = None
        mock_att.content_type = "application/octet-stream"
        mock_att.payload = b"data"
        mock_att.content_disposition = "attachment"
        del mock_att.content_id  # Remove content_id attribute
        
        mock_msg = mocker.MagicMock()
        mock_msg.uid = "12345"
        mock_msg.from_ = "sender@example.com"
        mock_msg.subject = "Test"
        mock_msg.date = datetime(2024, 1, 1, 12, 0, 0)
        mock_msg.text = "Test"
        mock_msg.html = None
        mock_msg.headers.get.return_value = ["<msg-id-123>"]
        mock_msg.attachments = [mock_att]
        
        email_data = parse_email(mock_msg)
        
        assert email_data.attachments[0].filename == "unnamed"
