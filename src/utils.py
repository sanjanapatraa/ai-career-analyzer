# src/utils.py
# ══════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS — used by every other module in the project
#
# Why a utils file?
# Many functions are needed in multiple places. Instead of copy-pasting
# the same code into 5 files, we write it once here and import it.
# This is called the DRY principle: Don't Repeat Yourself.
# ══════════════════════════════════════════════════════════════════════════

import os           # File and folder operations
import re           # Regular expressions for text pattern matching
import json         # Reading and writing JSON files
import logging      # Structured log messages
import time         # Time measurement (for performance tracking)
from functools import wraps   # Used to build the timing decorator
from typing import List, Dict, Optional, Tuple  # Type hints for clarity

import numpy as np            # Numerical operations
import pandas as pd           # DataFrame operations

# ── Logger setup ──────────────────────────────────────────────────────────
# Every module gets its own logger so we know which file printed what
logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 1 — DECORATORS
# A decorator wraps a function to add extra behavior without changing it.
# ════════════════════════════════════════════════════════════════════════════

def timer(func):
    """
    Decorator that measures and prints how long a function takes to run.

    Usage:
        @timer
        def my_slow_function():
            ...

    This is called a decorator — it wraps any function with timing code.
    The @timer syntax is Python shorthand for: my_function = timer(my_function)
    """
    @wraps(func)   # Preserves the original function's name and docstring
    def wrapper(*args, **kwargs):
        start = time.perf_counter()          # Record start time
        result = func(*args, **kwargs)       # Run the actual function
        end = time.perf_counter()            # Record end time
        elapsed = end - start
        logger.debug(f"{func.__name__} took {elapsed:.2f}s")
        return result
    return wrapper


# ════════════════════════════════════════════════════════════════════════════
# SECTION 2 — TEXT UTILITIES
# Functions for cleaning and working with text strings
# ════════════════════════════════════════════════════════════════════════════

def clean_text(text: str) -> str:
    """
    Basic text cleaning — removes noise while preserving meaning.

    Args:
        text: Any raw string (resume text, job description, etc.)

    Returns:
        Cleaned string, ready for NLP processing

    Why clean text?
    Raw text from PDFs is messy — it has weird spacing, broken words,
    special characters from encoding issues, etc.
    Cleaning makes NLP work more accurately.
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    # Remove null bytes — these sometimes appear in PDF-extracted text
    # and cause crashes in NLP libraries
    text = text.replace('\x00', ' ')

    # Remove form feed characters (page breaks in PDFs become \f)
    text = text.replace('\f', '\n')

    # Replace multiple newlines with a double newline (paragraph break)
    # This preserves section structure
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Replace multiple spaces with a single space
    text = re.sub(r' {2,}', ' ', text)

    # Remove control characters except newlines and tabs
    # These cause invisible bugs in text processing
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    return text.strip()


def normalize_whitespace(text: str) -> str:
    """
    Collapse all whitespace (spaces, tabs, newlines) into single spaces.

    Used when you need one clean line of text from a multi-line block.
    Example: "  hello   world\n\n" → "hello world"
    """
    if not isinstance(text, str):
        return ""
    return ' '.join(text.split())


def extract_emails(text: str) -> List[str]:
    """
    Find all email addresses in a block of text.

    Args:
        text: Any string (usually a resume)

    Returns:
        List of email addresses found, e.g. ['john@example.com']

    How it works:
    The regex pattern r'[\w\.-]+@[\w\.-]+\.\w+' matches:
        [\w\.-]+  = username (letters, digits, dots, hyphens)
        @         = the @ symbol
        [\w\.-]+  = domain (letters, digits, dots, hyphens)
        \.        = the dot before extension
        \w+       = extension (com, org, in, etc.)
    """
    if not isinstance(text, str):
        return []

    pattern = r'[\w\.-]+@[\w\.-]+\.\w+'

    # re.findall() returns ALL matches as a list
    emails = re.findall(pattern, text.lower())

    # Remove duplicates while preserving order using dict.fromkeys()
    # dict.fromkeys() removes duplicates because dict keys must be unique
    return list(dict.fromkeys(emails))


def extract_phone_numbers(text: str) -> List[str]:
    """
    Find phone numbers in resume text.

    Matches many formats:
        +91 9876543210
        (123) 456-7890
        9876-543-210
        +1-800-555-0123

    Args:
        text: Resume text

    Returns:
        List of phone number strings found
    """
    if not isinstance(text, str):
        return []

    # This pattern matches international and local phone number formats
    # [\+\(]?    = optional + or (
    # [1-9]      = first digit (not 0)
    # [0-9 .\-\(\)]{7,} = 7+ more digits/spaces/dashes/parens
    # [0-9]      = must end with a digit
    pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{7,}[0-9]'
    phones = re.findall(pattern, text)

    # Clean each phone number: remove extra spaces
    cleaned = [re.sub(r'\s+', '', p).strip() for p in phones]

    # Keep only phone numbers between 10 and 15 characters
    # (shorter = not a phone, longer = not a phone)
    return [p for p in cleaned if 10 <= len(p) <= 15]


def extract_urls(text: str) -> Dict[str, str]:
    """
    Find LinkedIn, GitHub, and portfolio URLs in resume text.

    Args:
        text: Resume text

    Returns:
        Dictionary like:
        {
            'linkedin': 'linkedin.com/in/johnsmith',
            'github': 'github.com/johnsmith',
            'portfolio': 'johnsmith.dev'
        }
    """
    if not isinstance(text, str):
        return {}

    urls = {}
    text_lower = text.lower()

    # Pattern to capture a URL starting with linkedin.com, github.com, etc.
    # The URL ends at whitespace or end of string
    url_pattern = r'(?:https?://)?(?:www\.)?({domain}[\w\-./]*)'

    # Check for LinkedIn
    if 'linkedin.com' in text_lower:
        match = re.search(
            r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+', text,
            re.IGNORECASE
        )
        if match:
            urls['linkedin'] = match.group(0)

    # Check for GitHub
    if 'github.com' in text_lower:
        match = re.search(
            r'(?:https?://)?(?:www\.)?github\.com/[\w\-]+', text,
            re.IGNORECASE
        )
        if match:
            urls['github'] = match.group(0)

    # Check for Kaggle
    if 'kaggle.com' in text_lower:
        match = re.search(
            r'(?:https?://)?(?:www\.)?kaggle\.com/[\w\-]+', text,
            re.IGNORECASE
        )
        if match:
            urls['kaggle'] = match.group(0)

    return urls


# ════════════════════════════════════════════════════════════════════════════
# SECTION 3 — RESUME SECTION DETECTION
# Detect which part of the resume each line belongs to
# ════════════════════════════════════════════════════════════════════════════

# These are the section headers we look for in resumes
# We use lowercase for comparison
SECTION_HEADERS = {
    'summary': [
        'summary', 'objective', 'profile', 'about me', 'professional summary',
        'career objective', 'professional profile', 'overview'
    ],
    'experience': [
        'experience', 'work experience', 'employment history', 'work history',
        'professional experience', 'career history', 'internship', 'internships',
        'positions held', 'employment'
    ],
    'education': [
        'education', 'academic background', 'qualifications', 'academic qualifications',
        'educational background', 'degrees', 'academic history'
    ],
    'skills': [
        'skills', 'technical skills', 'core competencies', 'competencies',
        'technologies', 'tools', 'tech stack', 'expertise', 'proficiencies',
        'key skills', 'programming languages', 'frameworks'
    ],
    'projects': [
        'projects', 'personal projects', 'academic projects', 'key projects',
        'notable projects', 'portfolio', 'side projects', 'open source'
    ],
    'certifications': [
        'certifications', 'certificates', 'achievements', 'awards',
        'accomplishments', 'licenses', 'credentials'
    ],
    'contact': [
        'contact', 'contact information', 'personal information', 'personal details'
    ],
}


def detect_section(line: str) -> Optional[str]:
    """
    Determine which resume section a line of text belongs to.

    Args:
        line: A single line from the resume

    Returns:
        Section name (e.g., 'skills', 'experience') or None if not a header

    How it works:
    We strip and lowercase the line, then check if it matches
    any known section header keyword. We also check if the line
    is short (section headers are rarely more than 4 words).
    """
    if not line or not isinstance(line, str):
        return None

    stripped = line.strip().lower()

    # Section headers are typically short (1-4 words)
    # and often end with ':' or are ALL CAPS
    # Skip very long lines (they're content, not headers)
    if len(stripped.split()) > 5:
        return None

    # Remove trailing colon (common in headers like "Skills:")
    stripped = stripped.rstrip(':').strip()

    # Check against every known section keyword
    for section_name, keywords in SECTION_HEADERS.items():
        if stripped in keywords:
            return section_name

        # Also check if any keyword is contained in the line
        # Handles cases like "Technical Skills & Tools"
        for keyword in keywords:
            if keyword in stripped and len(stripped) < 30:
                return section_name

    return None  # Not a recognizable section header


def split_resume_into_sections(text: str) -> Dict[str, str]:
    """
    Split the full resume text into named sections.

    Args:
        text: Complete resume text

    Returns:
        Dictionary mapping section name → section text content
        Example:
        {
            'skills': 'Python, Java, SQL, TensorFlow...',
            'experience': 'Software Engineer at Google...',
            'education': 'B.Tech in CS from IIT...'
        }

    Why split sections?
    Knowing WHICH section a skill appears in helps us:
    - Distinguish between "skills" section skills and incidental mentions
    - Extract education from the right place
    - Calculate experience years from the experience section only
    """
    sections = {}                # Output dictionary
    current_section = 'header'  # We start in the "header" (name/contact area)
    current_content  = []       # Lines collected so far for current section

    lines = text.split('\n')    # Split the entire text into lines

    for line in lines:
        # Check if this line is a section header
        detected = detect_section(line)

        if detected:
            # Save the previous section's content
            if current_content:
                # Join lines and add to our output dict
                existing = sections.get(current_section, '')
                sections[current_section] = existing + '\n'.join(current_content)

            # Start a new section
            current_section = detected
            current_content = []   # Reset content collector
        else:
            # This line is content (not a header) — add to current section
            if line.strip():   # Only add non-empty lines
                current_content.append(line)

    # Don't forget to save the last section
    if current_content:
        existing = sections.get(current_section, '')
        sections[current_section] = existing + '\n'.join(current_content)

    return sections


# ════════════════════════════════════════════════════════════════════════════
# SECTION 4 — EXPERIENCE PARSING
# Extract years of experience and job titles from resume text
# ════════════════════════════════════════════════════════════════════════════

def extract_years_experience(text: str) -> int:
    """
    Find the most likely total years of experience from resume text.

    Strategy:
    1. Look for explicit "X years experience" phrases
    2. Look for date ranges like "2020-2023" and calculate duration
    3. Return the maximum found (most likely reflects total experience)

    Args:
        text: Resume text (usually just the experience section)

    Returns:
        Integer years of experience (0 if not found)
    """
    if not isinstance(text, str):
        return 0

    years_found = []

    # Strategy 1: Explicit phrases like "5 years", "3+ years", "2-3 years"
    explicit_pattern = r'(\d+)\+?\s*(?:to\s*\d+\s*)?years?\s*(?:of\s*)?(?:experience|exp)?'
    matches = re.findall(explicit_pattern, text.lower())
    for m in matches:
        val = int(m)
        if 0 < val <= 30:    # Sanity check: 0-30 years is reasonable
            years_found.append(val)

    # Strategy 2: Date ranges like "Jan 2019 - Dec 2022" or "2018-2021"
    # This pattern finds years in ranges like "2019 - 2023" or "2020–Present"
    date_range_pattern = r'(20\d{2}|19\d{2})\s*[-–—to]+\s*(20\d{2}|present|current|now)'
    date_matches = re.findall(date_range_pattern, text.lower())

    import datetime
    current_year = datetime.datetime.now().year

    for start_year, end_year_str in date_matches:
        start = int(start_year)
        # Handle "present", "current", "now" → use current year
        if end_year_str in ('present', 'current', 'now'):
            end = current_year
        else:
            end = int(end_year_str)

        duration = end - start
        if 0 < duration <= 20:   # Reasonable duration
            years_found.append(duration)

    if years_found:
        return max(years_found)  # Return the highest value found
    return 0


def extract_job_titles(text: str) -> List[str]:
    """
    Find job titles mentioned in the resume experience section.

    Args:
        text: Resume experience section text

    Returns:
        List of job titles found, e.g. ['Software Engineer', 'Senior Developer']
    """
    # Common job title patterns — these often precede company names or dates
    title_patterns = [
        r'(Senior|Junior|Lead|Principal|Staff|Associate|Chief|Head of)\s+'
        r'(Software|Data|ML|AI|Cloud|DevOps|Full[- ]Stack|Backend|Frontend|'
        r'Network|Database|Security|Product|Business|UX|UI|Web)\s+'
        r'(Engineer|Developer|Scientist|Analyst|Architect|Designer|Manager|Administrator)',

        r'(Software|Data|ML|AI|Cloud|DevOps|Full[- ]Stack|Backend|Frontend|'
        r'Web)\s+(Engineer|Developer|Scientist|Analyst|Architect)',

        r'(Data|Business|Systems|Financial)\s+(Analyst|Scientist|Engineer)',
        r'(Product|Project|Program)\s+Manager',
        r'(UI|UX|UX/UI|UI/UX)\s+Designer',
        r'(Database|Network|Security|Cloud)\s+(Administrator|Engineer|Architect)',
        r'(DevOps|MLOps|DataOps)\s+Engineer',
        r'(Intern|Trainee|Fresher)',
    ]

    titles_found = []
    for pattern in title_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # match is a tuple of captured groups — join them
            if isinstance(match, tuple):
                title = ' '.join(m for m in match if m).strip()
            else:
                title = match.strip()
            if title and title not in titles_found:
                titles_found.append(title)

    return titles_found[:5]   # Return at most 5 titles (avoid false positives)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 5 — EDUCATION PARSING
# ════════════════════════════════════════════════════════════════════════════

# Map abbreviations to full degree names
DEGREE_PATTERNS = {
    r'\bphd\b|\bdoctorate\b|\bd\.phil\b':
        'PhD',
    r'\bm\.?tech\b|\bmaster of technology\b':
        'M.Tech',
    r'\bm\.?e\b|\bmaster of engineering\b':
        'M.E.',
    r'\bmba\b|\bmaster of business\b':
        'MBA',
    r'\bm\.?sc\b|\bmaster of science\b':
        'M.Sc.',
    r'\bm\.?s\b|\bmaster of science\b':
        'M.S.',
    r'\bm\.?c\.?a\b|\bmaster of computer applications\b':
        'MCA',
    r'\bb\.?tech\b|\bbachelor of technology\b':
        'B.Tech',
    r'\bb\.?e\b|\bbachelor of engineering\b':
        'B.E.',
    r'\bb\.?sc\b|\bbachelor of science\b':
        'B.Sc.',
    r'\bb\.?c\.?a\b|\bbachelor of computer applications\b':
        'BCA',
    r'\bbba\b|\bbachelor of business\b':
        'BBA',
    r'\bb\.?des\b|\bbachelor of design\b':
        'B.Des.',
    r'\bdiploma\b':
        'Diploma',
}


def extract_education(text: str) -> List[Dict]:
    """
    Parse education information from resume text.

    Args:
        text: Resume text (ideally the education section)

    Returns:
        List of education dicts:
        [
            {
                'degree': 'B.Tech',
                'field': 'Computer Science',
                'institution': 'IIT Bombay',
                'year': '2020',
                'gpa': '9.2'
            }
        ]
    """
    if not isinstance(text, str):
        return []

    education_list = []
    text_lower = text.lower()

    for pattern_str, degree_name in DEGREE_PATTERNS.items():
        if re.search(pattern_str, text_lower):
            edu_entry = {'degree': degree_name}

            # Try to find the graduation year (4-digit number 1980-2030)
            year_match = re.search(r'\b(19[8-9]\d|20[0-3]\d)\b', text)
            if year_match:
                edu_entry['year'] = year_match.group(1)

            # Try to find CGPA or percentage
            # Matches "CGPA: 8.5", "GPA 3.9", "9.1/10", "72%"
            gpa_match = re.search(
                r'(?:cgpa|gpa|grade|score|percentage|%)\s*[:\-]?\s*([\d\.]+)',
                text_lower
            )
            if gpa_match:
                edu_entry['gpa'] = gpa_match.group(1)

            # Try to find field of study
            fields = [
                'computer science', 'information technology', 'data science',
                'software engineering', 'electronics', 'electrical engineering',
                'mechanical engineering', 'civil engineering', 'mathematics',
                'statistics', 'physics', 'business administration',
                'artificial intelligence', 'machine learning', 'cybersecurity'
            ]
            for field in fields:
                if field in text_lower:
                    edu_entry['field'] = field.title()
                    break

            if edu_entry not in education_list:
                education_list.append(edu_entry)

    return education_list


# ════════════════════════════════════════════════════════════════════════════
# SECTION 6 — NAME EXTRACTION
# ════════════════════════════════════════════════════════════════════════════

def extract_name(text: str) -> str:
    """
    Extract the candidate's name from the top of their resume.

    Strategy:
    The name is usually on the first 1-3 lines of a resume.
    It's typically:
    - 2-4 words
    - Title case (John Smith, Priya Patel)
    - No numbers or special characters
    - NOT a section header

    Args:
        text: Full resume text

    Returns:
        Candidate name string or 'Unknown' if not found
    """
    if not isinstance(text, str):
        return 'Unknown'

    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]

    # Look at the first 5 lines only — names are at the top
    for line in lines[:5]:
        # Skip lines that are email addresses, phone numbers, or URLs
        if '@' in line or 'http' in line or 'www.' in line:
            continue

        # Skip lines with digits (phone numbers, addresses)
        if re.search(r'\d{4,}', line):
            continue

        # Skip known section headers
        if detect_section(line):
            continue

        # A name should be 2-4 words, each capitalized
        words = line.split()
        if 2 <= len(words) <= 4:
            # Check each word starts with a capital letter
            if all(w[0].isupper() for w in words if w and w[0].isalpha()):
                # Make sure it doesn't contain job title keywords
                title_keywords = {
                    'engineer', 'developer', 'scientist', 'analyst',
                    'manager', 'designer', 'architect', 'consultant'
                }
                if not any(kw in line.lower() for kw in title_keywords):
                    return line.strip()

    return 'Unknown'


# ════════════════════════════════════════════════════════════════════════════
# SECTION 7 — SCORING HELPERS
# ════════════════════════════════════════════════════════════════════════════

def calculate_percentage_match(resume_skills: List[str],
                               required_skills: List[str]) -> float:
    """
    Calculate what percentage of required skills the resume has.

    Args:
        resume_skills:   Skills found in the resume
        required_skills: Skills required by the job description

    Returns:
        Float between 0.0 and 100.0

    Example:
        resume_skills   = ['python', 'sql', 'pandas']
        required_skills = ['python', 'sql', 'tensorflow', 'docker']
        → 2 matches out of 4 → 50.0%
    """
    if not required_skills:
        return 0.0

    # Convert everything to lowercase for fair comparison
    resume_lower   = {s.lower().strip() for s in resume_skills}
    required_lower = {s.lower().strip() for s in required_skills}

    # Find skills that appear in BOTH sets (intersection)
    matched = resume_lower.intersection(required_lower)

    # Calculate percentage
    percentage = (len(matched) / len(required_lower)) * 100
    return round(percentage, 1)


def get_missing_skills(resume_skills: List[str],
                       required_skills: List[str]) -> List[str]:
    """
    Find which required skills are MISSING from the resume.

    Args:
        resume_skills:   Skills found in the resume
        required_skills: Skills required by the job

    Returns:
        List of skills the resume is missing

    Example:
        resume_skills   = ['python', 'sql']
        required_skills = ['python', 'sql', 'docker', 'kubernetes']
        → ['docker', 'kubernetes']
    """
    resume_lower   = {s.lower().strip() for s in resume_skills}
    required_lower = [s.lower().strip() for s in required_skills]

    # List comprehension: keep skills NOT in the resume set
    missing = [skill for skill in required_lower if skill not in resume_lower]

    return missing


def format_score_label(score: float) -> Tuple[str, str]:
    """
    Convert a numeric ATS score to a label and color.

    Args:
        score: Number between 0 and 100

    Returns:
        Tuple of (label, color_hex)
        Example: (80, ...) → ('Excellent', '#2ecc71')
    """
    if score >= 85:
        return ('Excellent', '#2ecc71')    # Green
    elif score >= 70:
        return ('Good', '#3498db')         # Blue
    elif score >= 55:
        return ('Average', '#f39c12')      # Orange
    elif score >= 40:
        return ('Below Average', '#e67e22') # Dark orange
    else:
        return ('Poor', '#e74c3c')          # Red


# ════════════════════════════════════════════════════════════════════════════
# SECTION 8 — FILE UTILITIES
# ════════════════════════════════════════════════════════════════════════════

def load_json_config(filepath: str) -> dict:
    """
    Safely load a JSON configuration file.

    Args:
        filepath: Path to the JSON file

    Returns:
        Dictionary of config values, or empty dict if file not found
    """
    if not os.path.exists(filepath):
        logger.warning(f"Config file not found: {filepath}")
        return {}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
        return {}


def ensure_dir(path: str):
    """Create a directory (and all parent directories) if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def get_file_size_mb(filepath: str) -> float:
    """Return the size of a file in megabytes."""
    if not os.path.exists(filepath):
        return 0.0
    size_bytes = os.path.getsize(filepath)
    return round(size_bytes / (1024 * 1024), 2)   # Convert bytes → MB