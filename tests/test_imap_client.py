"""Tests for IMAP client."""
import pytest


class TestIMAPClient:
    """Tests for IMAP client."""
    
    def test_connect_success(self, mocker):
        """Test successful IMAP connection."""
        from src.ingestion.imap_client import IMAPClient
        
        # Mock MailBox
        mock_mailbox = mocker.MagicMock()
        mock_mailbox_class = mocker.patch("src.ingestion.imap_client.MailBox")
        mock_mailbox_class.return_value = mock_mailbox
        
        client = IMAPClient(
            host="imap.example.com",
            port=993,
            username="user@example.com",
            password="password",
            folder="INBOX",
            use_ssl=True,
        )
        
        client.connect()
        
        mock_mailbox_class.assert_called_once_with("imap.example.com", 993)
        mock_mailbox.login.assert_called_once_with("user@example.com", "password")
        mock_mailbox.folder.set.assert_called_once_with("INBOX")
    
    def test_disconnect(self, mocker):
        """Test IMAP disconnection."""
        from src.ingestion.imap_client import IMAPClient
        
        mock_mailbox = mocker.MagicMock()
        mock_mailbox_class = mocker.patch("src.ingestion.imap_client.MailBox")
        mock_mailbox_class.return_value = mock_mailbox
        
        client = IMAPClient(
            host="imap.example.com",
            port=993,
            username="user@example.com",
            password="password",
        )
        
        client.connect()
        client.disconnect()
        
        mock_mailbox.logout.assert_called_once()
    
    def test_fetch_emails(self, mocker):
        """Test fetching emails."""
        from src.ingestion.imap_client import IMAPClient
        from src.ingestion.base import ProcessingState
        from datetime import datetime
        
        # Mock email message
        mock_msg = mocker.MagicMock()
        mock_msg.uid = "12345"
        mock_msg.from_ = "sender@example.com"
        mock_msg.subject = "Test Email"
        mock_msg.date = datetime(2024, 1, 1, 12, 0, 0)
        mock_msg.text = "Email body"
        mock_msg.html = None
        mock_msg.headers.get.return_value = ["<msg-id>"]
        mock_msg.attachments = []
        
        # Mock mailbox
        mock_mailbox = mocker.MagicMock()
        mock_mailbox.fetch.return_value = [mock_msg]
        
        mock_mailbox_class = mocker.patch("src.ingestion.imap_client.MailBox")
        mock_mailbox_class.return_value = mock_mailbox
        
        client = IMAPClient(
            host="imap.example.com",
            port=993,
            username="user@example.com",
            password="password",
        )
        
        client.connect()
        emails = client.fetch_emails()
        
        assert len(emails) == 1
        assert emails[0].subject == "Test Email"
        assert emails[0].state == ProcessingState.FETCHED
    
    def test_delete_email(self, mocker):
        """Test deleting email."""
        from src.ingestion.imap_client import IMAPClient
        from src.ingestion.base import EmailData, ProcessingState
        
        mock_mailbox = mocker.MagicMock()
        mock_mailbox_class = mocker.patch("src.ingestion.imap_client.MailBox")
        mock_mailbox_class.return_value = mock_mailbox
        
        client = IMAPClient(
            host="imap.example.com",
            port=993,
            username="user@example.com",
            password="password",
        )
        
        client.connect()
        
        email = EmailData(
            message_id="msg-123",
            uid="12345",
            sender="sender@example.com",
            subject="Test",
            date="2024-01-01",
        )
        
        client.delete_email(email)
        
        mock_mailbox.delete.assert_called_once_with(["12345"])
        mock_mailbox.expunge.assert_called_once()
        assert email.state == ProcessingState.DELETED
    
    def test_fetch_emails_not_connected(self):
        """Test fetching emails when not connected."""
        from src.ingestion.imap_client import IMAPClient
        
        client = IMAPClient(
            host="imap.example.com",
            port=993,
            username="user@example.com",
            password="password",
        )
        
        with pytest.raises(RuntimeError, match="Not connected"):
            client.fetch_emails()
    
    def test_delete_email_not_connected(self):
        """Test deleting email when not connected."""
        from src.ingestion.imap_client import IMAPClient
        from src.ingestion.base import EmailData
        
        client = IMAPClient(
            host="imap.example.com",
            port=993,
            username="user@example.com",
            password="password",
        )
        
        email = EmailData(
            message_id="msg-123",
            uid="12345",
            sender="sender@example.com",
            subject="Test",
            date="2024-01-01",
        )
        
        with pytest.raises(RuntimeError, match="Not connected"):
            client.delete_email(email)
