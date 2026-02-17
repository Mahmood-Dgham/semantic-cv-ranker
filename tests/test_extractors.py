"""Tests for text extractors."""
import pytest


class TestHTMLStripper:
    """Tests for HTML text extraction."""
    
    def test_strip_html_to_text_success(self):
        """Test HTML stripping."""
        from src.extraction.html_stripper import strip_html_to_text
        
        html = "<html><body><h1>Title</h1><p>Paragraph text</p></body></html>"
        result = strip_html_to_text(html)
        
        assert "Title" in result
        assert "Paragraph text" in result
        assert "<html>" not in result
    
    def test_strip_html_removes_scripts(self):
        """Test that script tags are removed."""
        from src.extraction.html_stripper import strip_html_to_text
        
        html = "<html><body><script>alert('test')</script><p>Visible text</p></body></html>"
        result = strip_html_to_text(html)
        
        assert "Visible text" in result
        assert "alert" not in result
    
    def test_strip_html_failure(self):
        """Test HTML stripping with invalid input."""
        from src.extraction.html_stripper import strip_html_to_text
        
        result = strip_html_to_text(None)
        assert result is None
    
    def test_strip_html_cleans_whitespace(self):
        """Test that HTML stripping cleans extra whitespace."""
        from src.extraction.html_stripper import strip_html_to_text
        
        html = "<html><body><p>   Multiple   spaces   </p><p>New  paragraph</p></body></html>"
        result = strip_html_to_text(html)
        
        assert "Multiple" in result
        assert "spaces" in result
        assert "New" in result


class TestContentClassifier:
    """Tests for content classification."""
    
    def test_classify_as_cv_by_keywords(self):
        """Test CV classification by keywords."""
        from src.ingestion.content_classifier import classify_content
        from src.ingestion.base import ContentType
        
        text = "Professional experience in software development. Education: BS Computer Science. Skills: Python, Java."
        result = classify_content(text)
        
        assert result == ContentType.CV
    
    def test_classify_as_cv_by_filename(self):
        """Test CV classification by filename."""
        from src.ingestion.content_classifier import classify_content
        from src.ingestion.base import ContentType
        
        text = "Some work experience"
        result = classify_content(text, filename="john_doe_cv.pdf")
        
        assert result == ContentType.CV
    
    def test_classify_as_cover_letter(self):
        """Test cover letter classification."""
        from src.ingestion.content_classifier import classify_content
        from src.ingestion.base import ContentType
        
        text = "Dear Hiring Manager, I am writing to apply for the position of Software Engineer. I am interested in joining your team."
        result = classify_content(text)
        
        assert result == ContentType.COVER_LETTER
    
    def test_classify_as_certificate(self):
        """Test certificate classification."""
        from src.ingestion.content_classifier import classify_content
        from src.ingestion.base import ContentType
        
        text = "Certificate of completion for Advanced Python Programming. This certifies that John Doe has successfully completed the course."
        result = classify_content(text)
        
        assert result == ContentType.CERTIFICATE
    
    def test_classify_as_unknown(self):
        """Test unknown classification."""
        from src.ingestion.content_classifier import classify_content
        from src.ingestion.base import ContentType
        
        text = "Random text without specific keywords"
        result = classify_content(text)
        
        assert result == ContentType.UNKNOWN
    
    def test_classify_empty_content(self):
        """Test classification with empty content."""
        from src.ingestion.content_classifier import classify_content
        from src.ingestion.base import ContentType
        
        result = classify_content(None, None)
        
        assert result == ContentType.UNKNOWN
    
    def test_classify_resume_filename(self):
        """Test classification with resume filename."""
        from src.ingestion.content_classifier import classify_content
        from src.ingestion.base import ContentType
        
        result = classify_content("Work at company", filename="my_resume.pdf")
        
        assert result == ContentType.CV

