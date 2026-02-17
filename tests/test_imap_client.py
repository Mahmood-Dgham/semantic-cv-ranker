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
        """Test fetching emails with date filtering."""
        from src.ingestion.imap_client import IMAPClient
        from src.ingestion.base import ProcessingState
        from datetime import datetime, timezone
        
        # Mock email message with a future date
        mock_msg = mocker.MagicMock()
        mock_msg.uid = "12345"
        mock_msg.from_ = "sender@example.com"
        mock_msg.subject = "Test Email"
        # Set date to future to ensure it passes the filter
        mock_msg.date = datetime(2050, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
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
    
    def test_fetch_emails_filters_old_emails(self, mocker):
        """Test that old emails are filtered out."""
        from src.ingestion.imap_client import IMAPClient
        from datetime import datetime, timezone
        
        # Mock old and new email messages
        old_msg = mocker.MagicMock()
        old_msg.uid = "11111"
        old_msg.from_ = "old@example.com"
        old_msg.subject = "Old Email"
        old_msg.date = datetime(2020, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        old_msg.text = "Old email body"
        old_msg.html = None
        old_msg.headers.get.return_value = ["<old-msg-id>"]
        old_msg.attachments = []
        
        new_msg = mocker.MagicMock()
        new_msg.uid = "22222"
        new_msg.from_ = "new@example.com"
        new_msg.subject = "New Email"
        new_msg.date = datetime(2050, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        new_msg.text = "New email body"
        new_msg.html = None
        new_msg.headers.get.return_value = ["<new-msg-id>"]
        new_msg.attachments = []
        
        # Mock mailbox
        mock_mailbox = mocker.MagicMock()
        mock_mailbox.fetch.return_value = [old_msg, new_msg]
        
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
        
        # Only the new email should be fetched
        assert len(emails) == 1
        assert emails[0].subject == "New Email"
    
    def test_mark_all_as_read(self, mocker):
        """Test marking all emails as read."""
        from src.ingestion.imap_client import IMAPClient
        
        # Mock email messages
        mock_msg1 = mocker.MagicMock()
        mock_msg1.uid = "11111"
        
        mock_msg2 = mocker.MagicMock()
        mock_msg2.uid = "22222"
        
        mock_msg3 = mocker.MagicMock()
        mock_msg3.uid = "33333"
        
        # Mock mailbox
        mock_mailbox = mocker.MagicMock()
        mock_mailbox.fetch.return_value = [mock_msg1, mock_msg2, mock_msg3]
        
        mock_mailbox_class = mocker.patch("src.ingestion.imap_client.MailBox")
        mock_mailbox_class.return_value = mock_mailbox
        
        client = IMAPClient(
            host="imap.example.com",
            port=993,
            username="user@example.com",
            password="password",
        )
        
        client.connect()
        client.mark_all_as_read()
        
        # Verify that seen was called for each email
        assert mock_mailbox.seen.call_count == 3
        mock_mailbox.seen.assert_any_call(["11111"], True)
        mock_mailbox.seen.assert_any_call(["22222"], True)
        mock_mailbox.seen.assert_any_call(["33333"], True)
    
    def test_mark_all_as_read_not_connected(self):
        """Test marking emails as read when not connected."""
        from src.ingestion.imap_client import IMAPClient
        
        client = IMAPClient(
            host="imap.example.com",
            port=993,
            username="user@example.com",
            password="password",
        )
        
        with pytest.raises(RuntimeError, match="Not connected"):
            client.mark_all_as_read()
