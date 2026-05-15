# src/resume_parser.py
# ══════════════════════════════════════════════════════════════════════════
# RESUME PARSER — extracts and structures text from PDF resumes
#
# This is the ENTRY POINT for every resume uploaded to our app.
# It does the following:
#   1. Read bytes from a PDF file
#   2. Extract raw text using PyMuPDF (primary) and pdfplumber (fallback)
#   3. Split text into named sections (skills, experience, education...)
#   4. Extract contact information (name, email, phone, URLs)
#   5. Extract education history
#   6. Extract years of experience
#   7. Return a clean, structured Python dictionary
#
# Output structure (the "resume_data" dict used throughout the whole app):
# {
#   'raw_text':     str,           # Complete resume text
#   'name':         str,           # Candidate name
#   'email':        str,           # Email address
#   'phone':        str,           # Phone number
#   'links':        dict,          # LinkedIn, GitHub, etc.
#   'sections':     dict,          # Each section's text
#   'education':    list,          # Parsed education entries
#   'experience_years': int,       # Years of experience
#   'job_titles':   list,          # Past job titles found
#   'word_count':   int,           # Total word count
#   'page_count':   int,           # Number of PDF pages
# }
# ══════════════════════════════════════════════════════════════════════════

import io           # For handling file bytes in memory (no temp files needed)
import re
import logging
from typing import Dict, List, Optional, Union, Tuple

# PyMuPDF is the primary PDF reader. It's fast and handles most PDFs well.
# We import it as 'fitz' because that's its internal library name.
try:
    import fitz           # PyMuPDF — pip install PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logging.warning("PyMuPDF not available. Install with: pip install PyMuPDF")

# pdfplumber is our fallback PDF reader.
# It's better at PDFs with tables and complex layouts.
try:
    import pdfplumber      # pip install pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logging.warning("pdfplumber not available. Install with: pip install pdfplumber")

# Import our utility functions
from src.utils import (
    clean_text,
    extract_emails,
    extract_phone_numbers,
    extract_urls,
    extract_name,
    extract_years_experience,
    extract_job_titles,
    extract_education,
    split_resume_into_sections,
    timer,
)

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 1 — PDF TEXT EXTRACTION
# ════════════════════════════════════════════════════════════════════════════

def extract_text_pymupdf(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF bytes using PyMuPDF (primary method).

    PyMuPDF is fast and handles most standard PDFs well.
    It reads each page and returns the text content.

    Args:
        pdf_bytes: Raw bytes of the PDF file
                   (this is what you get from file.read() or st.file_uploader)

    Returns:
        Extracted text as a single string, or empty string if failed

    What are "bytes"?
    When you open a PDF on your computer, it's stored as binary data (0s and 1s).
    "bytes" is Python's way of representing that raw binary data.
    We work with bytes so we never need to save a temp file to disk.
    """
    if not PYMUPDF_AVAILABLE:
        return ""

    try:
        # fitz.open() can open from bytes using stream parameter
        # This reads the PDF entirely in memory (no temp files!)
        doc = fitz.open(
            stream=pdf_bytes,   # The raw bytes
            filetype="pdf"      # Tell fitz this is a PDF
        )

        all_text = []    # Collect text from all pages

        # Iterate through each page (page numbers start at 0)
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)   # Load the page object

            # get_text() extracts text from the page
            # "text" mode returns plain text
            # "blocks" mode returns structured blocks (we use plain here)
            page_text = page.get_text("text")

            if page_text.strip():   # Only add non-empty pages
                all_text.append(page_text)

        doc.close()   # Always close the document to free memory

        # Join all pages with a page separator
        full_text = '\n'.join(all_text)
        logger.info(f"PyMuPDF extracted {len(full_text)} characters, "
                    f"{doc.page_count} pages")
        return full_text

    except Exception as e:
        # If PyMuPDF fails (e.g., encrypted PDF, corrupted file), log and return empty
        logger.warning(f"PyMuPDF extraction failed: {e}")
        return ""


def extract_text_pdfplumber(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF bytes using pdfplumber (fallback method).

    pdfplumber is better than PyMuPDF for:
    - PDFs with tables
    - PDFs with complex multi-column layouts
    - Scanned PDFs with text layers

    Args:
        pdf_bytes: Raw bytes of the PDF file

    Returns:
        Extracted text string
    """
    if not PDFPLUMBER_AVAILABLE:
        return ""

    try:
        # io.BytesIO wraps bytes in a file-like object
        # pdfplumber.open() needs a file-like object, not raw bytes
        pdf_file = io.BytesIO(pdf_bytes)

        all_text = []
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                # extract_text() returns text from this page
                page_text = page.extract_text()
                if page_text:
                    all_text.append(page_text)

        full_text = '\n'.join(all_text)
        logger.info(f"pdfplumber extracted {len(full_text)} characters")
        return full_text

    except Exception as e:
        logger.warning(f"pdfplumber extraction failed: {e}")
        return ""


@timer   # This decorator measures how long this function takes
def extract_text_from_pdf(pdf_bytes: bytes) -> Tuple[str, int]:
    """
    Master text extraction — tries PyMuPDF first, falls back to pdfplumber.

    This is the ONLY function the rest of the app calls for PDF text.
    It hides all the complexity of which library to use.

    Args:
        pdf_bytes: Raw PDF file bytes

    Returns:
        Tuple: (extracted_text: str, page_count: int)

    Strategy:
    1. Try PyMuPDF — fastest, works for most PDFs
    2. If PyMuPDF returns empty/fails → try pdfplumber
    3. If both fail → return empty string (show error in app)
    """
    page_count = 0

    # ── Attempt 1: PyMuPDF ────────────────────────────────────────────────
    if PYMUPDF_AVAILABLE:
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page_count = doc.page_count
            doc.close()
        except Exception:
            pass

        text = extract_text_pymupdf(pdf_bytes)

        # If we got at least 100 characters, consider it successful
        if len(text.strip()) >= 100:
            logger.info("Using PyMuPDF extraction result")
            return clean_text(text), page_count

    # ── Attempt 2: pdfplumber fallback ────────────────────────────────────
    if PDFPLUMBER_AVAILABLE:
        logger.info("Falling back to pdfplumber...")
        text = extract_text_pdfplumber(pdf_bytes)

        if len(text.strip()) >= 100:
            logger.info("Using pdfplumber extraction result")
            return clean_text(text), page_count

    # ── Both failed ───────────────────────────────────────────────────────
    logger.error("Both PDF extraction methods failed or returned empty text")
    return "", page_count


# Type alias so our return type is clear
# In Python, Tuple[str, int] means a tuple containing (string, integer)
from typing import Tuple
Tuple_text_pages = Tuple[str, int]


# ════════════════════════════════════════════════════════════════════════════
# SECTION 2 — RESUME STRUCTURE PARSER
# ════════════════════════════════════════════════════════════════════════════

@timer
def parse_resume(pdf_bytes: bytes) -> Dict:
    """
    MAIN FUNCTION — Parse a PDF resume into a structured dictionary.

    This is the function called by the Streamlit app when a user
    uploads their resume. It orchestrates all the extraction steps.

    Args:
        pdf_bytes: Raw bytes from st.file_uploader or open(file, 'rb').read()

    Returns:
        Dictionary with all extracted resume information.
        See module docstring for the full structure.

    Step-by-step process:
    1. Extract raw text from the PDF
    2. Split into sections
    3. Extract contact info
    4. Extract education
    5. Extract experience info
    6. Calculate statistics
    7. Return everything as a structured dict
    """
    logger.info("Starting resume parsing...")

    # ── Step 1: Extract raw text ─────────────────────────────────────────
    raw_text, page_count = extract_text_from_pdf(pdf_bytes)

    if not raw_text:
        logger.error("No text could be extracted from the PDF")
        return {
            'error': 'Could not extract text from PDF. '
                     'Please ensure the PDF is not scanned or image-based.',
            'raw_text': '',
            'name': 'Unknown',
        }

    logger.info(f"Extracted {len(raw_text)} characters from {page_count} pages")

    # ── Step 2: Split into named sections ────────────────────────────────
    sections = split_resume_into_sections(raw_text)
    logger.info(f"Detected sections: {list(sections.keys())}")

    # ── Step 3: Extract contact information ──────────────────────────────
    # Extract from the beginning of the resume (header area)
    # Most contact info is in the first 20 lines
    header_text = '\n'.join(raw_text.split('\n')[:20])

    name   = extract_name(raw_text)
    emails = extract_emails(raw_text)
    phones = extract_phone_numbers(header_text)
    links  = extract_urls(raw_text)

    email = emails[0] if emails else ''
    phone = phones[0] if phones else ''

    logger.info(f"Extracted: name='{name}', email='{email}', phone='{phone}'")

    # ── Step 4: Extract education ─────────────────────────────────────────
    # Use education section if found, otherwise use full text
    edu_text = sections.get('education', raw_text)
    education = extract_education(edu_text)

    # ── Step 5: Extract experience info ──────────────────────────────────
    exp_text     = sections.get('experience', raw_text)
    years_exp    = extract_years_experience(exp_text)
    job_titles   = extract_job_titles(exp_text)

    # ── Step 6: Calculate text statistics ────────────────────────────────
    words = raw_text.split()
    word_count  = len(words)
    char_count  = len(raw_text)
    # Count bullet points (lines starting with •, -, *, or numbers)
    bullet_count = len(re.findall(r'^\s*[•\-\*\d]\s+', raw_text, re.MULTILINE))

    # ── Step 7: Assemble the output dictionary ───────────────────────────
    resume_data = {
        # Raw content
        'raw_text':        raw_text,
        'page_count':      page_count,

        # Contact information
        'name':            name,
        'email':           email,
        'phone':           phone,
        'links':           links,

        # Structured sections
        'sections':        sections,

        # Education
        'education':       education,

        # Experience
        'experience_years': years_exp,
        'job_titles':      job_titles,

        # Statistics
        'word_count':      word_count,
        'char_count':      char_count,
        'bullet_count':    bullet_count,

        # Status flags
        'has_linkedin':    'linkedin' in links,
        'has_github':      'github'   in links,
        'has_education':   len(education) > 0,
        'has_experience':  'experience' in sections,
        'has_skills':      'skills' in sections,
        'has_projects':    'projects' in sections,
        'has_certifications': 'certifications' in sections,

        # Error flag (None means success)
        'error': None,
    }

    logger.info("Resume parsing complete!")
    logger.info(f"  Name: {name}")
    logger.info(f"  Experience: {years_exp} years")
    logger.info(f"  Education entries: {len(education)}")
    logger.info(f"  Sections: {list(sections.keys())}")

    return resume_data


def parse_resume_from_text(text: str) -> Dict:
    """
    Parse a resume from raw text (not PDF).
    Used for testing and for pre-loaded sample resumes.

    Args:
        text: Plain text of the resume

    Returns:
        Same structured dict as parse_resume()
    """
    # Same logic, but skip the PDF extraction step
    raw_text = clean_text(text)
    page_count = 1   # Assume 1 page for text input

    sections  = split_resume_into_sections(raw_text)
    emails    = extract_emails(raw_text)
    phones    = extract_phone_numbers(raw_text[:500])   # Check first 500 chars
    links     = extract_urls(raw_text)
    name      = extract_name(raw_text)
    education = extract_education(sections.get('education', raw_text))
    years_exp = extract_years_experience(sections.get('experience', raw_text))
    job_titles = extract_job_titles(sections.get('experience', raw_text))

    words = raw_text.split()

    return {
        'raw_text':        raw_text,
        'page_count':      page_count,
        'name':            name,
        'email':           emails[0] if emails else '',
        'phone':           phones[0] if phones else '',
        'links':           links,
        'sections':        sections,
        'education':       education,
        'experience_years': years_exp,
        'job_titles':      job_titles,
        'word_count':      len(words),
        'char_count':      len(raw_text),
        'bullet_count':    len(re.findall(r'^\s*[•\-\*\d]\s+', raw_text, re.MULTILINE)),
        'has_linkedin':    'linkedin' in links,
        'has_github':      'github' in links,
        'has_education':   len(education) > 0,
        'has_experience':  'experience' in sections,
        'has_skills':      'skills' in sections,
        'has_projects':    'projects' in sections,
        'has_certifications': 'certifications' in sections,
        'error':           None,
    }


# ── Quick test (run this file directly to test) ────────────────────────────
if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Test with a sample text resume
    sample_text = open(
        "data/sample_resumes/data_scientist_john_smith.txt",
        encoding='utf-8'
    ).read()

    result = parse_resume_from_text(sample_text)

    print("\n" + "=" * 60)
    print("RESUME PARSING TEST RESULT")
    print("=" * 60)
    print(f"Name:             {result['name']}")
    print(f"Email:            {result['email']}")
    print(f"Phone:            {result['phone']}")
    print(f"Links:            {result['links']}")
    print(f"Experience years: {result['experience_years']}")
    print(f"Education:        {result['education']}")
    print(f"Job titles:       {result['job_titles']}")
    print(f"Word count:       {result['word_count']}")
    print(f"Sections found:   {list(result['sections'].keys())}")
    print(f"Has GitHub:       {result['has_github']}")
    print(f"Has LinkedIn:     {result['has_linkedin']}")