"""
Resume Parser Service for GOAT AI.
Handles secure extraction and normalization of text from PDF and DOCX documents.
"""

import os
import re
import io
from typing import Tuple, Optional
import pymupdf as fitz
from docx import Document

ALLOWED_EXTENSIONS = {'.pdf', '.docx'}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


class ResumeParserError(Exception):
    """Custom exception raised when resume parsing fails."""
    pass


def is_allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension."""
    if not filename or '.' not in filename:
        return False
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def clean_text(text: str) -> str:
    """Normalize extracted text by stripping excess whitespace and control characters."""
    if not text:
        return ""
    # Replace non-breaking spaces and carriage returns
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = text.replace('\xa0', ' ')
    # Replace multiple spaces with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    # Collapse 3+ newlines into 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def parse_pdf_from_bytes(file_bytes: bytes) -> str:
    """Extract readable text from a PDF file in memory using PyMuPDF (fitz)."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise ResumeParserError(f"Unable to open PDF document. File may be encrypted or corrupted: {str(e)}")

    extracted_pages = []
    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text("text")
            if page_text and page_text.strip():
                extracted_pages.append(page_text.strip())
    finally:
        doc.close()

    full_text = "\n\n".join(extracted_pages)
    cleaned = clean_text(full_text)

    if not cleaned:
        raise ResumeParserError(
            "The PDF document was read, but no readable text was found. "
            "If your resume is a scanned image or photo, please use a text-based PDF or paste your resume text directly."
        )

    return cleaned


def parse_docx_from_bytes(file_bytes: bytes) -> str:
    """Extract text from a Word DOCX document including paragraphs and tables."""
    try:
        file_stream = io.BytesIO(file_bytes)
        doc = Document(file_stream)
    except Exception as e:
        raise ResumeParserError(f"Unable to read Word document. File may be invalid or corrupted: {str(e)}")

    text_parts = []

    # Extract text from standard paragraphs
    for p in doc.paragraphs:
        if p.text and p.text.strip():
            text_parts.append(p.text.strip())

    # Extract text from tables (many resumes format skills/experience in tables)
    for table in doc.tables:
        for row in table.rows:
            row_texts = [cell.text.strip() for cell in row.cells if cell.text and cell.text.strip()]
            if row_texts:
                text_parts.append(" | ".join(row_texts))

    full_text = "\n".join(text_parts)
    cleaned = clean_text(full_text)

    if not cleaned:
        raise ResumeParserError(
            "The Word document contains no readable text. Please check the document content or paste your text directly."
        )

    return cleaned


def extract_resume_text(file_storage=None, raw_text: Optional[str] = None) -> Tuple[str, str]:
    """
    Main entry point for extracting resume text.
    Accepts either a Flask FileStorage object or direct raw text.
    Returns a tuple of (extracted_text, source_type).
    """
    if file_storage and file_storage.filename:
        filename = file_storage.filename
        if not is_allowed_file(filename):
            raise ResumeParserError("Invalid file type. Only PDF (.pdf) and Word (.docx) documents are supported.")

        file_bytes = file_storage.read()
        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            raise ResumeParserError("File exceeds the 5MB size limit. Please upload a smaller file.")

        ext = os.path.splitext(filename)[1].lower()
        if ext == '.pdf':
            return parse_pdf_from_bytes(file_bytes), f"PDF ({filename})"
        elif ext == '.docx':
            return parse_docx_from_bytes(file_bytes), f"DOCX ({filename})"
        else:
            raise ResumeParserError("Unsupported file extension.")

    elif raw_text and raw_text.strip():
        cleaned = clean_text(raw_text)
        if len(cleaned) < 20:
            raise ResumeParserError("The provided resume text is too brief. Please provide your full resume content.")
        return cleaned, "Pasted Text"

    else:
        raise ResumeParserError("Please upload a resume file or enter resume text to analyze.")
