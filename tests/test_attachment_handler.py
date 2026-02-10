"""Tests for attachment handler."""
import pytest


class TestAttachmentHandler:
    """Tests for attachment handling."""
    
    def test_process_attachment_pdf(self, mocker):
        """Test processing PDF attachment."""
        from src.ingestion.attachment_handler import AttachmentHandler
        from src.ingestion.base import AttachmentData, ContentType
        
        # Mock PDF extractor
        mock_extract = mocker.patch(
            "src.ingestion.attachment_handler.extract_text_from_pdf",
            return_value="CV text with experience and education"
        )
        
        handler = AttachmentHandler(max_size_mb=25)
        
        attachment = AttachmentData(
            filename="resume.pdf",
            content_type="application/pdf",
            payload=b"fake pdf",
            size_bytes=1024,
        )
        
        handler.process_attachment(attachment)
        
        assert attachment.extracted_text == "CV text with experience and education"
        assert attachment.classified_as == ContentType.CV
        mock_extract.assert_called_once()
    
    def test_process_attachment_docx(self, mocker):
        """Test processing DOCX attachment."""
        from src.ingestion.attachment_handler import AttachmentHandler
        from src.ingestion.base import AttachmentData
        
        mock_extract = mocker.patch(
            "src.ingestion.attachment_handler.extract_text_from_docx",
            return_value="Cover letter text"
        )
        
        handler = AttachmentHandler(max_size_mb=25)
        
        attachment = AttachmentData(
            filename="cover_letter.docx",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            payload=b"fake docx",
            size_bytes=2048,
        )
        
        handler.process_attachment(attachment)
        
        assert attachment.extracted_text == "Cover letter text"
        mock_extract.assert_called_once()
    
    def test_process_attachment_image(self, mocker):
        """Test processing image attachment with OCR."""
        from src.ingestion.attachment_handler import AttachmentHandler
        from src.ingestion.base import AttachmentData
        
        mock_extract = mocker.patch(
            "src.ingestion.attachment_handler.extract_text_from_image",
            return_value="Text from image"
        )
        
        handler = AttachmentHandler(max_size_mb=25, tesseract_path="/usr/bin/tesseract")
        
        attachment = AttachmentData(
            filename="scan.jpg",
            content_type="image/jpeg",
            payload=b"fake image",
            size_bytes=512,
        )
        
        handler.process_attachment(attachment)
        
        assert attachment.extracted_text == "Text from image"
        mock_extract.assert_called_once_with(b"fake image", "/usr/bin/tesseract")
    
    def test_process_attachment_html(self, mocker):
        """Test processing HTML attachment."""
        from src.ingestion.attachment_handler import AttachmentHandler
        from src.ingestion.base import AttachmentData
        
        mock_extract = mocker.patch(
            "src.ingestion.attachment_handler.strip_html_to_text",
            return_value="Plain text from HTML"
        )
        
        handler = AttachmentHandler(max_size_mb=25)
        
        attachment = AttachmentData(
            filename="document.html",
            content_type="text/html",
            payload=b"<html><body>Text</body></html>",
            size_bytes=256,
        )
        
        handler.process_attachment(attachment)
        
        assert attachment.extracted_text == "Plain text from HTML"
        mock_extract.assert_called_once()
    
    def test_process_attachment_plain_text(self, mocker):
        """Test processing plain text attachment."""
        from src.ingestion.attachment_handler import AttachmentHandler
        from src.ingestion.base import AttachmentData
        
        handler = AttachmentHandler(max_size_mb=25)
        
        attachment = AttachmentData(
            filename="notes.txt",
            content_type="text/plain",
            payload=b"Plain text content",
            size_bytes=128,
        )
        
        handler.process_attachment(attachment)
        
        assert attachment.extracted_text == "Plain text content"
    
    def test_process_attachment_size_limit(self, mocker):
        """Test attachment size limit enforcement."""
        from src.ingestion.attachment_handler import AttachmentHandler
        from src.ingestion.base import AttachmentData, ContentType
        
        handler = AttachmentHandler(max_size_mb=1)  # 1MB limit
        
        attachment = AttachmentData(
            filename="large.pdf",
            content_type="application/pdf",
            payload=b"x" * (2 * 1024 * 1024),  # 2MB
            size_bytes=2 * 1024 * 1024,
        )
        
        handler.process_attachment(attachment)
        
        assert attachment.classified_as == ContentType.IRRELEVANT
        assert attachment.extracted_text is None
    
    def test_process_attachment_unsupported_type(self, mocker):
        """Test handling unsupported file type."""
        from src.ingestion.attachment_handler import AttachmentHandler
        from src.ingestion.base import AttachmentData, ContentType
        
        handler = AttachmentHandler(max_size_mb=25)
        
        attachment = AttachmentData(
            filename="video.mp4",
            content_type="video/mp4",
            payload=b"fake video",
            size_bytes=1024,
        )
        
        handler.process_attachment(attachment)
        
        assert attachment.classified_as == ContentType.UNKNOWN
    
    def test_process_attachment_zip(self, mocker):
        """Test processing ZIP archive."""
        from src.ingestion.attachment_handler import AttachmentHandler
        from src.ingestion.base import AttachmentData
        import io
        import zipfile
        
        # Create a fake ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr("resume.txt", "Text content with experience and education")
        zip_bytes = zip_buffer.getvalue()
        
        # Mock text extraction
        mocker.patch(
            "src.ingestion.attachment_handler.extract_text_from_pdf",
            return_value=None
        )
        
        handler = AttachmentHandler(max_size_mb=25)
        
        attachment = AttachmentData(
            filename="documents.zip",
            content_type="application/zip",
            payload=zip_bytes,
            size_bytes=len(zip_bytes),
        )
        
        handler.process_attachment(attachment)
        
        assert attachment.extracted_text is not None
        assert "resume.txt" in attachment.extracted_text
        assert "experience" in attachment.extracted_text
