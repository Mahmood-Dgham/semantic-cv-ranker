# Semantic CV Ranker

An intelligent system for automated CV/resume ingestion, processing, and ranking using semantic analysis.

## Phase 0: Email Ingestion Pipeline

This phase implements an automated email ingestion pipeline that:
- Polls a mailbox at regular intervals (default: every 2 minutes)
- Downloads and parses emails with all content (body, attachments, inline images)
- Extracts text from multiple formats (PDF, DOCX, HTML, images via OCR)
- Classifies content (CV, cover letter, certificate, etc.)
- Permanently deletes processed emails
- Provides comprehensive logging

## Features

### ✅ Pluggable Architecture
- Abstract `IngestionSource` base class for easy integration with other sources (SharePoint, Microsoft Graph API, etc.)
- Modular design with clear separation of concerns

### ✅ Email Processing
- IMAP client with SSL support
- Fetch unread/unseen emails
- Parse email body (plain text and HTML)
- Extract all attachments and inline images
- Delete emails permanently after successful processing

### ✅ Text Extraction
- **PDF**: Extract text using `pdfplumber` with `PyMuPDF` fallback
- **DOCX**: Extract text and tables using `python-docx`
- **HTML**: Strip HTML tags and extract meaningful text using `BeautifulSoup`
- **Images**: OCR text extraction using `pytesseract` (JPG, PNG, TIFF)
- **ZIP Archives**: Extract and process all files inside

### ✅ Content Classification
- Heuristic-based CV/resume detection
- Cover letter detection
- Certificate/reference detection
- Filename pattern matching
- Classifies as UNKNOWN if uncertain (never discards)

### ✅ Robust Error Handling
- Email state machine: UNREAD → FETCHED → PROCESSING → PROCESSED → DELETED
- Failed emails are logged but not automatically retried
- Continues processing remaining emails on individual failures
- Never deletes emails before successful processing

## Project Structure

```
semantic-cv-ranker/
├── src/
│   ├── main.py                      # Main entry point
│   ├── config.py                    # Configuration management
│   ├── ingestion/
│   │   ├── base.py                  # Data models and abstract base class
│   │   ├── imap_client.py           # IMAP client implementation
│   │   ├── email_parser.py          # Email parsing logic
│   │   ├── attachment_handler.py    # Attachment processing and routing
│   │   ├── content_classifier.py    # Content classification heuristics
│   │   └── scheduler.py             # Polling scheduler
│   └── extraction/
│       ├── pdf_extractor.py         # PDF text extraction
│       ├── docx_extractor.py        # DOCX text extraction
│       ├── html_stripper.py         # HTML text extraction
│       └── image_ocr.py             # Image OCR extraction
├── tests/
│   ├── test_extractors.py
│   ├── test_email_parser.py
│   ├── test_attachment_handler.py
│   └── test_imap_client.py
├── .env.example                      # Environment variables template
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites

- Python 3.10 or higher
- Tesseract OCR (for image text extraction)

#### Install Tesseract

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your IMAP credentials and preferences:

```bash
# IMAP Server Configuration
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=your-email@gmail.com
IMAP_PASSWORD=your-app-password
IMAP_FOLDER=INBOX
IMAP_USE_SSL=true

# Scheduler Configuration
SCHEDULER_POLL_INTERVAL_MINUTES=2

# Extraction Configuration
MAX_ATTACHMENT_SIZE_MB=25
TESSERACT_PATH=/usr/bin/tesseract

# Logging Configuration
LOG_LEVEL=INFO
```

### Gmail Setup

For Gmail, you need to:
1. Enable 2-factor authentication
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the App Password in `IMAP_PASSWORD`

## Usage

### Start the Email Ingestion Pipeline

```bash
python -m src.main
```

The system will:
1. Connect to your IMAP mailbox
2. Poll for new emails every 2 minutes (configurable)
3. Process each email:
   - Extract text from body (plain and HTML)
   - Process all attachments (PDF, DOCX, images, ZIP archives)
   - Classify content (CV, cover letter, certificate, etc.)
   - Merge all text into unified output
   - Log processing details
   - Delete email permanently
4. Continue polling until interrupted (Ctrl+C)

### Logs

The system provides detailed logging:
- Email fetching and parsing
- Attachment processing
- Text extraction results
- Classification results
- Error details
- Processing statistics

Example log output:
```
2024-01-01 12:00:00 - INFO - Starting Semantic CV Ranker - Phase 0
2024-01-01 12:00:01 - INFO - Connected to IMAP server imap.gmail.com:993
2024-01-01 12:00:02 - INFO - Poll cycle: found 3 emails to process
2024-01-01 12:00:03 - INFO - Processing email: Job Application from john.doe@example.com
2024-01-01 12:00:04 - INFO - Extracted 2500 characters from PDF using pdfplumber
2024-01-01 12:00:05 - INFO - Processed attachment resume.pdf: classified as cv
2024-01-01 12:00:06 - INFO - Successfully processed email (extracted 3200 total chars)
2024-01-01 12:00:07 - INFO - Deleted email: Job Application (UID: 12345)
2024-01-01 12:00:10 - INFO - Poll cycle complete: 3 processed, 0 failed
```

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=src --cov-report=html
```

Run specific test file:

```bash
pytest tests/test_extractors.py
```

## Architecture

### Email Processing Flow

```
1. Scheduler triggers polling job (every 2 minutes)
   ↓
2. IMAP Client fetches unseen emails
   ↓
3. Email Parser extracts body, attachments, inline images
   ↓
4. For each attachment:
   - Attachment Handler routes by MIME type
   - Text Extractor extracts text
   - Content Classifier classifies content
   ↓
5. Merge all extracted text into unified output
   ↓
6. Log processing details
   ↓
7. Delete email permanently (IMAP delete + expunge)
   ↓
8. Continue with next email
```

### State Machine

```
UNREAD → FETCHED → PROCESSING → PROCESSED → DELETED
                        ↓
                    FAILED (logged, not retried)
```

### Content Classification

The system uses heuristic-based classification:

**CV/Resume Detection:**
- Keywords: experience, education, skills, qualifications, etc.
- Filename patterns: cv_, resume_, curriculum

**Cover Letter Detection:**
- Keywords: "dear hiring manager", "applying for", etc.

**Certificate Detection:**
- Keywords: certificate, certification, diploma, degree

**Classification never discards content** - uncertain content is marked as UNKNOWN.

## Data Models

### EmailData
```python
@dataclass
class EmailData:
    message_id: str
    uid: str
    sender: str
    subject: str
    date: str
    body_plain: Optional[str]
    body_html: Optional[str]
    body_text_extracted: Optional[str]
    attachments: list[AttachmentData]
    inline_images: list[AttachmentData]
    state: ProcessingState
    all_extracted_text: Optional[str]
    error: Optional[str]
```

### AttachmentData
```python
@dataclass
class AttachmentData:
    filename: str
    content_type: str
    payload: bytes
    size_bytes: int
    extracted_text: Optional[str]
    classified_as: ContentType
```

## Supported File Formats

- **PDF**: `.pdf`
- **DOCX**: `.docx`, `.doc`
- **HTML**: `.html`, `.htm`
- **Plain Text**: `.txt`
- **Images**: `.jpg`, `.jpeg`, `.png`, `.tiff`
- **Archives**: `.zip` (recursively processes contents)

## Limitations

- Maximum attachment size: 25MB (configurable)
- Designed for <50 emails/day (simple polling, no task queue)
- OCR accuracy depends on image quality
- No automatic retry for failed emails

## Future Phases

- **Phase 1**: Vector embeddings and storage
- **Phase 2**: Semantic similarity and ranking
- **Phase 3**: API and web interface
- **Phase 4**: Advanced ML models and fine-tuning

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Submit a pull request

## License

MIT License - see LICENSE file for details