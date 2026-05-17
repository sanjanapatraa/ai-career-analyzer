# api.py
# ══════════════════════════════════════════════════════════════════════════
# FASTAPI BACKEND — The bridge between Python ML and the React frontend
#
# What this file does:
#   - Creates a web server that listens for requests
#   - When React sends a PDF file, this receives it
#   - Passes it through all your existing Python modules
#   - Returns the results as JSON (a structured data format)
#   - React then displays those results in the beautiful dashboard
#
# Think of it like a waiter in a restaurant:
#   React (customer) → api.py (waiter) → Python ML (kitchen)
#   Python ML (kitchen) → api.py (waiter) → React (customer)
# ══════════════════════════════════════════════════════════════════════════

import os
import sys
import json
import logging
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add the project root to Python path so we can import our modules
# This is the same trick used in app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# FastAPI imports
# FastAPI = the web framework
# UploadFile = handles file uploads (PDF)
# File = tells FastAPI to expect a file
# Form = tells FastAPI to expect form data (like text)
# HTTPException = for sending error messages back to the UI
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# ── Import ALL your existing Python modules ────────────────────────────────
# These are the exact files you built in Phases 4, 5, 6
# We are just calling them from a new place (api.py instead of Streamlit)

from src.resume_parser import parse_resume, parse_resume_from_text
from src.skill_extractor import extract_skills
from src.ats_scorer import calculate_ats_score
from src.job_matcher import match_resume_to_job
from src.report_generator import generate_report

# Career recommender — we wrap in try/except because models may not be
# trained yet (user needs to run Phase 5 training first)
try:
    from src.career_recommender import CareerRecommender
    # Load the recommender ONCE when the server starts
    # Loading takes a few seconds, so we do it here not on every request
    recommender = CareerRecommender()
    ML_AVAILABLE = True
    print("✓ ML Career Recommender loaded successfully")
except Exception as e:
    recommender = None
    ML_AVAILABLE = False
    print(f"⚠ ML models not found. Run Phase 5 training first. Error: {e}")

# ── Create the FastAPI application ─────────────────────────────────────────
# This creates our web server application
# The title and description appear in the auto-generated API docs
app = FastAPI(
    title="ResumeIQ API",
    description="AI-powered ATS Resume Analyzer Backend",
    version="1.0.0",
)
# Serve frontend static files

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
# ── CORS Middleware ────────────────────────────────────────────────────────
# CORS = Cross-Origin Resource Sharing
# Without this, the React frontend cannot talk to this Python server
# because they run on different ports (React: 3000, FastAPI: 8000)
# allow_origins=["*"] means "accept requests from any address"
# In production you would limit this to your actual domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve the React frontend ───────────────────────────────────────────────
# This tells FastAPI to serve files from the "frontend" folder
# So when someone opens http://localhost:8000 they see the React app
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

# ── Setup logging ──────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

def make_json_safe(obj):
    """
    Convert Python objects to JSON-safe types.

    Why do we need this?
    Some Python objects (like numpy integers, numpy floats, numpy arrays)
    cannot be directly converted to JSON. This function converts them to
    regular Python types (int, float, list) that JSON understands.

    Example:
        numpy.int64(5)     → 5    (regular Python int)
        numpy.float32(0.7) → 0.7  (regular Python float)
        numpy.array([1,2]) → [1, 2] (regular Python list)
    """
    import numpy as np

    if isinstance(obj, dict):
        # Recursively process every key-value pair in the dictionary
        return {key: make_json_safe(val) for key, val in obj.items()}
    elif isinstance(obj, list):
        # Recursively process every item in the list
        return [make_json_safe(item) for item in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    else:
        return str(obj)


def rule_based_career_prediction(resume_skills: list) -> list:
    """
    Fallback career prediction when ML models are not trained.

    Uses a simple rule: count how many skills from each career's
    typical skill set appear in the resume. The career with the
    most matches wins.

    Args:
        resume_skills: List of skills found in the resume

    Returns:
        List of top 5 career predictions with confidence scores
    """
    skills_lower = {s.lower() for s in resume_skills}

    # Career → typical skills mapping
    career_skills = {
        "Data Scientist":            {"python","machine learning","sql","tensorflow","statistics","pandas","deep learning","numpy","r"},
        "Machine Learning Engineer": {"python","tensorflow","pytorch","mlops","docker","kubernetes","deep learning","mlflow"},
        "Software Engineer":         {"java","python","c++","algorithms","system design","git","rest api","microservices"},
        "Data Analyst":              {"sql","excel","tableau","power bi","python","statistics","r","looker"},
        "Frontend Developer":        {"html","css","javascript","react","typescript","vue","next.js","figma"},
        "Backend Developer":         {"python","java","node.js","django","flask","postgresql","mongodb","redis"},
        "DevOps Engineer":           {"docker","kubernetes","aws","terraform","ci/cd","linux","jenkins","ansible"},
        "Cybersecurity Analyst":     {"network security","penetration testing","linux","python","firewalls","siem"},
        "Cloud Architect":           {"aws","azure","gcp","terraform","kubernetes","cloud","docker"},
        "Full Stack Developer":      {"react","node.js","python","javascript","postgresql","docker","aws"},
    }

    scores = {}
    for career, typical_skills in career_skills.items():
        matched = skills_lower.intersection(typical_skills)
        if typical_skills:
            scores[career] = len(matched) / len(typical_skills)

    # Sort by score descending
    sorted_careers = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Convert to list of dicts with confidence percentage
    total = sum(s for _, s in sorted_careers[:5]) or 1
    results = []
    for rank, (career, score) in enumerate(sorted_careers[:5], 1):
        results.append({
            "rank":       rank,
            "career":     career,
            "confidence": round((score / total) * 100, 1),
        })

    return results


# ════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# Each @app.post or @app.get creates a URL that the React frontend calls
# ════════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """
    Root endpoint — serves the React frontend.
    When you open http://localhost:8000 in a browser, you see the React app.
    """
    if os.path.exists("frontend/index.html"):
        return FileResponse("frontend/index.html")
    return {"message": "ResumeIQ API running. Frontend not found in /frontend folder."}


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    The React app calls this to verify the Python server is running.
    Returns: status, ML availability, and server info.
    """
    return {
        "status":       "healthy",
        "ml_available": ML_AVAILABLE,
        "version":      "1.0.0",
        "message":      "ResumeIQ API is running",
    }


@app.post("/api/analyze")
async def analyze_resume(
    file: UploadFile = File(None),
    text: str        = Form(None),
    jd:   str        = Form(""),
    target_level:    str = Form("mid"),
    education_req:   str = Form("bachelor"),
):
    """
    MAIN ENDPOINT — The most important one.

    The React frontend calls this when a user uploads their resume.
    It runs the complete analysis pipeline and returns all results.

    Parameters:
        file:          The uploaded PDF file (optional)
        text:          Plain text resume (optional, for testing)
        jd:            Job description text (optional)
        target_level:  'entry', 'mid', 'senior', 'lead'
        education_req: 'bachelor', 'master', 'phd', 'any'

    Returns:
        Complete JSON object with all analysis results
    """
    # ── Step 1: Get resume text ────────────────────────────────────────────
    # Either from uploaded PDF or from plain text input
    resume_data = None

    if file and file.filename:
        # User uploaded a PDF file
        logger.info(f"Received PDF: {file.filename}")

        # Read the raw bytes from the uploaded file
        pdf_bytes = await file.read()

        # Check file size (max 5MB)
        if len(pdf_bytes) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 5MB."
            )

        # Parse the PDF using your existing resume_parser.py
        resume_data = parse_resume(pdf_bytes)

    elif text:
        # User provided plain text (used for testing and sample resumes)
        logger.info("Received plain text resume")
        resume_data = parse_resume_from_text(text)

    else:
        raise HTTPException(
            status_code=400,
            detail="Please provide either a PDF file or resume text."
        )

    # ── Step 2: Check for parsing errors ──────────────────────────────────
    if resume_data.get("error"):
        raise HTTPException(
            status_code=422,
            detail=f"Could not parse resume: {resume_data['error']}"
        )

    # ── Step 3: Extract skills ─────────────────────────────────────────────
    logger.info("Extracting skills...")
    skills_result = extract_skills(
        resume_data.get("raw_text", ""),
        resume_data.get("sections")
    )

    # ── Step 4: Calculate ATS score ────────────────────────────────────────
    logger.info("Calculating ATS score...")
    ats_result = calculate_ats_score(
        resume_data    = resume_data,
        resume_skills  = skills_result.get("all_skills", []),
        job_description = jd if jd.strip() else None,
        target_level   = target_level,
        required_education = education_req,
    )

    # ── Step 5: Job matching (only if JD was provided) ─────────────────────
    match_result = {}
    if jd.strip():
        logger.info("Matching against job description...")
        match_result = match_resume_to_job(
            resume_data   = resume_data,
            job_description = jd,
            resume_skills = skills_result.get("all_skills", []),
        )

    # ── Step 6: Career prediction ──────────────────────────────────────────
    logger.info("Predicting career matches...")
    if ML_AVAILABLE and recommender:
        # Use trained ML models (available after Phase 5 training)
        try:
            top_careers = recommender.predict_top_n(
                resume_data.get("raw_text", ""),
                resume_data,
                n=5,
            )
        except Exception as e:
            logger.warning(f"ML prediction failed, using rules: {e}")
            top_careers = rule_based_career_prediction(
                skills_result.get("all_skills", [])
            )
    else:
        # Fallback: rule-based prediction
        top_careers = rule_based_career_prediction(
            skills_result.get("all_skills", [])
        )

    # ── Step 7: Build the response ─────────────────────────────────────────
    # This is the complete data object the React dashboard will display
    response = {
        # Candidate info
        "candidate": {
            "name":             resume_data.get("name", "Unknown"),
            "email":            resume_data.get("email", ""),
            "phone":            resume_data.get("phone", ""),
            "experience_years": resume_data.get("experience_years", 0),
            "word_count":       resume_data.get("word_count", 0),
            "page_count":       resume_data.get("page_count", 1),
            "has_linkedin":     resume_data.get("has_linkedin", False),
            "has_github":       resume_data.get("has_github", False),
            "education":        resume_data.get("education", []),
            "job_titles":       resume_data.get("job_titles", []),
        },

        # ATS scoring results
        "ats": {
            "overall_score":     ats_result.get("overall_score", 0),
            "grade":             ats_result.get("grade", "F"),
            "label":             ats_result.get("label", ""),
            "component_scores":  ats_result.get("component_scores", {}),
            "strengths":         ats_result.get("strengths", []),
            "improvements":      ats_result.get("improvements", []),
            "missing_skills":    ats_result.get("missing_skills", []),
            "resume_tips":       ats_result.get("resume_tips", []),
            "feedback":          ats_result.get("feedback", []),
        },

        # Skills analysis
        "skills": {
            "all_skills":        skills_result.get("all_skills", []),
            "technical_skills":  skills_result.get("technical_skills", []),
            "soft_skills":       skills_result.get("soft_skills", []),
            "total_count":       skills_result.get("total_count", 0),
            "by_category":       skills_result.get("by_category", {}),
        },

        # Career recommendations
        "careers": top_careers,

        # Job description matching (empty if no JD provided)
        "match": {
            "overall_score":    match_result.get("overall_score", 0),
            "match_label":      match_result.get("match_label", ""),
            "matched_skills":   match_result.get("matched_skills", []),
            "missing_skills":   match_result.get("missing_skills", []),
            "tfidf_score":      match_result.get("tfidf_score", 0),
            "semantic_score":   match_result.get("semantic_score", 0),
            "skill_match_score": match_result.get("skill_match_score", 0),
            "recommendations":  match_result.get("recommendations", []),
        } if match_result else {},

        # Status
        "ml_used": ML_AVAILABLE,
    }

    # Convert any numpy types to regular Python types before returning
    return JSONResponse(content=make_json_safe(response))


@app.post("/api/report")
async def download_report(
    file: UploadFile = File(None),
    text: str        = Form(None),
    jd:   str        = Form(""),
):
    """
    Generate and return a PDF analysis report.

    The React frontend calls this when the user clicks
    "Download Report". Returns a PDF file for download.
    """
    # Re-run analysis to get fresh data
    # (In production you would cache this from the /analyze call)
    if file and file.filename:
        pdf_bytes   = await file.read()
        resume_data = parse_resume(pdf_bytes)
    elif text:
        resume_data = parse_resume_from_text(text)
    else:
        raise HTTPException(status_code=400, detail="No resume provided")

    skills_result = extract_skills(
        resume_data.get("raw_text", ""),
        resume_data.get("sections")
    )
    ats_result = calculate_ats_score(
        resume_data,
        skills_result.get("all_skills", []),
        jd if jd.strip() else None,
    )

    # Generate the PDF using your existing report_generator.py
    pdf_bytes_report = generate_report(
        resume_data   = resume_data,
        ats_result    = ats_result,
        match_result  = {},
        career_result = {"career": "See dashboard", "confidence": 0},
        skills_result = skills_result,
    )

    # Save to a temp file and send it
    report_path = "temp_report.pdf"
    with open(report_path, "wb") as f:
        f.write(pdf_bytes_report)

    return FileResponse(
        path         = report_path,
        filename     = f"resume_analysis_{resume_data.get('name','candidate')}.pdf",
        media_type   = "application/pdf",
    )


@app.get("/api/sample/{role}")
async def get_sample_resume(role: str):
    """
    Return a sample resume text for the given role.
    The React frontend uses this for the demo buttons.

    Args:
        role: Career role name (e.g. 'data-scientist', 'software-engineer')
    """
    # Map URL-friendly role names to sample file names
    sample_files = {
        "data-scientist":    "data/sample_resumes/data_scientist_john_smith.txt",
        "software-engineer": "data/sample_resumes/software_engineer_priya_patel.txt",
        "fresher":           "data/sample_resumes/fresher_rahul_kumar.txt",
    }

    filepath = sample_files.get(role.lower())

    if not filepath or not os.path.exists(filepath):
        raise HTTPException(
            status_code=404,
            detail=f"Sample resume not found for role: {role}"
        )

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    return {"role": role, "text": text}


# Serve frontend static files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Serve React frontend homepage
@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/index.html")