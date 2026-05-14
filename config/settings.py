# config/settings.py
# ─────────────────────────────────────────────────────────
# This file holds all the SETTINGS for our project.
# Think of it like the control panel — change values here
# and they change everywhere in the project.
# ─────────────────────────────────────────────────────────

import os  # os lets us work with file paths and folders

# ── Project Paths ────────────────────────────────────────
# os.path.dirname(__file__) = the folder THIS file is in (config/)
# os.path.dirname(...) again = the PARENT folder (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Build paths to all important folders using BASE_DIR
DATA_DIR        = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR    = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR   = os.path.join(DATA_DIR, "processed")
MODELS_DIR      = os.path.join(BASE_DIR, "models")
SAMPLE_DIR      = os.path.join(DATA_DIR, "sample_resumes")

# ── Model Settings ───────────────────────────────────────
# The Sentence Transformer model name (pre-trained AI from HuggingFace)
# This model converts text into numbers (vectors) so we can compare them
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Name of the spaCy model we downloaded
SPACY_MODEL     = "en_core_web_sm"

# ── ATS Scoring Weights ──────────────────────────────────
# These control HOW MUCH each factor matters in the ATS score.
# All weights must add up to 1.0 (100%)
ATS_WEIGHTS = {
    "skill_match":       0.35,   # 35% — Do your skills match the job?
    "keyword_density":   0.20,   # 20% — Are job keywords in your resume?
    "format_quality":    0.15,   # 15% — Is the resume well formatted?
    "experience_match":  0.15,   # 15% — Does experience level match?
    "education_match":   0.10,   # 10% — Does education match?
    "contact_info":      0.05,   # 5%  — Is contact info present?
}

# ── App Config ───────────────────────────────────────────
APP_NAME    = "AI Career Analyzer"        # Name shown in the UI
APP_VERSION = "1.0.0"                     # Version number
MAX_FILE_SIZE_MB = 5                      # Max resume file size (in MB)

# ── Supported Career Categories ─────────────────────────
# These are the job roles our ML model can predict
CAREER_CATEGORIES = [
    "Data Scientist",
    "Software Engineer",
    "Machine Learning Engineer",
    "Data Analyst",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "DevOps Engineer",
    "Cybersecurity Analyst",
    "Cloud Architect",
    "Product Manager",
    "Business Analyst",
    "UI/UX Designer",
    "Database Administrator",
    "Network Engineer",
]