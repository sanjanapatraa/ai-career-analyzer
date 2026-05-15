# src/job_matcher.py
# ══════════════════════════════════════════════════════════════════════════
# JOB MATCHER — compares a resume to a job description
#
# Two core techniques:
#
# 1. TF-IDF + Cosine Similarity
#    → Convert both resume and job description to TF-IDF vectors
#    → Measure the angle between those vectors (cosine similarity)
#    → Score from 0.0 (no match) to 1.0 (perfect match)
#
# 2. Skill-based matching
#    → Extract skills from both resume and job description
#    → Calculate what % of required skills the resume has
#    → List which skills are missing
#
# COSINE SIMILARITY EXPLAINED (simple version):
# Imagine every word is an axis in space.
# "Python developer with 5 years experience" becomes a point in that space.
# "Senior Python engineer, 5+ years" becomes another point.
# Cosine similarity measures how close those two points are (0=far, 1=same).
# ══════════════════════════════════════════════════════════════════════════

import re
import os
import logging
from typing import Dict, List, Optional, Tuple

import numpy as np

# sklearn gives us TF-IDF and cosine similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# sentence_transformers gives us semantic similarity
# (understands MEANING, not just word overlap)
SENTENCE_TRANSFORMERS_AVAILABLE = False

import joblib

from src.utils import (
    clean_text,
    calculate_percentage_match,
    get_missing_skills,
    timer,
)

logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')


# ════════════════════════════════════════════════════════════════════════════
# SECTION 1 — TEXT PREPROCESSING FOR MATCHING
# ════════════════════════════════════════════════════════════════════════════

def preprocess_for_matching(text: str) -> str:
    """
    Light preprocessing specifically for job matching.

    We keep more words than during training preprocessing because
    for matching, CONTEXT matters — we don't want to lose too much.

    Args:
        text: Raw text (resume or job description)

    Returns:
        Cleaned text suitable for TF-IDF vectorization
    """
    if not isinstance(text, str):
        return ""

    text = text.lower()                          # Lowercase
    text = re.sub(r'http\S+|www\S+', ' ', text) # Remove URLs
    text = re.sub(r'\S+@\S+', ' ', text)         # Remove emails
    text = re.sub(r'[^a-zA-Z\s\+\#\.]', ' ', text)  # Keep +, #, . for C++, C#, .NET
    text = re.sub(r'\s+', ' ', text)             # Normalize whitespace
    return text.strip()


# ════════════════════════════════════════════════════════════════════════════
# SECTION 2 — TF-IDF COSINE SIMILARITY MATCHING
# ════════════════════════════════════════════════════════════════════════════

@timer
def compute_tfidf_similarity(resume_text: str,
                              job_description: str) -> float:
    """
    Compute cosine similarity between resume and job description
    using TF-IDF vectors.

    Args:
        resume_text:      Full resume text
        job_description:  Job description text

    Returns:
        Float between 0.0 and 1.0 (1.0 = perfect match)

    STEP-BY-STEP EXPLANATION:

    Step 1 — Build vocabulary
        We look at ALL words in both texts combined.
        e.g., vocabulary = ['python', 'developer', 'experience', 'aws', ...]

    Step 2 — Create TF-IDF vector for RESUME
        A vector is just a list of numbers.
        Each position = one word from the vocabulary.
        The number = how important that word is in the resume.
        e.g., resume_vector = [0.4, 0.0, 0.3, 0.2, ...]
                               ^python  ^developer  ^experience  ^aws

    Step 3 — Create TF-IDF vector for JOB DESCRIPTION
        Same process, different text.
        e.g., job_vector = [0.5, 0.1, 0.4, 0.3, ...]

    Step 4 — Calculate cosine similarity
        cos(θ) = (A · B) / (|A| × |B|)
        Where:
            A · B = dot product (sum of A[i] × B[i] for all i)
            |A|   = magnitude of vector A (sqrt of sum of squares)
            |B|   = magnitude of vector B

        Result: number between -1 and 1
        For TF-IDF (all positive values): result is between 0 and 1

        0.0 = completely different (no shared words)
        1.0 = identical (same words with same frequencies)
        0.7 = good match
        0.4 = weak match
    """
    if not resume_text or not job_description:
        return 0.0

    # Preprocess both texts
    processed_resume = preprocess_for_matching(resume_text)
    processed_jd     = preprocess_for_matching(job_description)

    # Create a fresh TF-IDF vectorizer for just these two documents
    # We use a fresh one (not the trained one) so it adapts to both texts
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),    # Unigrams + bigrams (single words + 2-word phrases)
        min_df=1,              # Keep all words (only 2 docs, can't filter)
        max_df=1.0,            # Keep all words
        sublinear_tf=True,     # Log-scale term frequency
        stop_words='english',  # Remove English stop words (the, is, at, ...)
    )

    try:
        # Fit and transform BOTH texts at once
        # tfidf_matrix shape: (2, vocab_size)
        # Row 0 = resume vector, Row 1 = job description vector
        tfidf_matrix = vectorizer.fit_transform(
            [processed_resume, processed_jd]
        )

        # cosine_similarity() takes a matrix and computes pairwise similarities
        # Result shape: (2, 2) matrix
        # result[0][1] = similarity between doc 0 (resume) and doc 1 (job desc)
        similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

        # Extract the single similarity score
        score = float(similarity_matrix[0][0])

        logger.info(f"TF-IDF cosine similarity: {score:.3f}")
        return round(score, 4)

    except Exception as e:
        logger.error(f"TF-IDF similarity computation failed: {e}")
        return 0.0


# ════════════════════════════════════════════════════════════════════════════
# SECTION 3 — SEMANTIC SIMILARITY (SENTENCE TRANSFORMERS)
# ════════════════════════════════════════════════════════════════════════════

# Module-level cache for the model — load once, reuse many times
_sentence_model = None


def get_sentence_model():
    """
    Load the Sentence Transformer model (cached after first load).

    Sentence Transformers understand MEANING, not just word overlap.
    Example:
        "I have experience with Python"
        "Proficient in Python programming"
    These are semantically similar but share few exact words.
    TF-IDF would score this low; Sentence Transformers score it HIGH.

    Model: 'all-MiniLM-L6-v2'
    - Small and fast (22MB)
    - Good accuracy for sentence similarity
    - First load downloads from HuggingFace (needs internet once)
    """
    global _sentence_model

    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        return None

    if _sentence_model is None:
        logger.info("Loading Sentence Transformer model (first time only)...")
        try:
            # This downloads the model on first run (~22MB)
            # Subsequent runs use the cached version
            _sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Sentence Transformer model loaded!")
        except Exception as e:
            logger.warning(f"Could not load Sentence Transformer: {e}")
            return None

    return _sentence_model


@timer
def compute_semantic_similarity(resume_text: str,
                                 job_description: str) -> float:
    """
    Compute semantic similarity between resume and job description.

    Uses Sentence Transformers to understand MEANING, not just words.
    Much more accurate than TF-IDF but slower.

    Args:
        resume_text:     Full resume text
        job_description: Job description text

    Returns:
        Float between 0.0 and 1.0

    How it works:
    1. Send both texts through a neural network (BERT-based)
    2. The network outputs a 384-dimensional vector for each text
    3. These vectors encode the MEANING of the text
    4. We compute cosine similarity between the two meaning vectors
    """
    model = get_sentence_model()
    if model is None:
        logger.warning("Sentence model unavailable. Skipping semantic similarity.")
        return 0.0

    try:
        # Limit text length to avoid memory issues
        # BERT has a 512 token limit; we use first 1000 chars as proxy
        resume_short = resume_text[:2000]
        jd_short     = job_description[:2000]

        # encode() converts text → 384-dimensional meaning vector
        # These vectors capture semantics — similar meanings → similar vectors
        resume_embedding = model.encode([resume_short])   # Shape: (1, 384)
        jd_embedding     = model.encode([jd_short])       # Shape: (1, 384)

        # Compute cosine similarity between the two meaning vectors
        score = float(cosine_similarity(resume_embedding, jd_embedding)[0][0])

        logger.info(f"Semantic similarity: {score:.3f}")
        return round(max(0.0, min(1.0, score)), 4)  # Clamp to [0, 1]

    except Exception as e:
        logger.error(f"Semantic similarity computation failed: {e}")
        return 0.0


# ════════════════════════════════════════════════════════════════════════════
# SECTION 4 — JOB DESCRIPTION SKILL EXTRACTION
# ════════════════════════════════════════════════════════════════════════════

def extract_required_skills_from_jd(jd_text: str) -> List[str]:
    """
    Extract the skills that a job description requires.

    We re-use our skill extractor but on the JD text instead of a resume.
    This gives us the "required skills" list for comparison.

    Args:
        jd_text: Job description text

    Returns:
        List of required skill strings (lowercase)
    """
    # Import here to avoid circular imports
    from src.skill_extractor import extract_skills

    result = extract_skills(jd_text)
    return result.get('all_skills', [])


def extract_required_experience(jd_text: str) -> Optional[int]:
    """
    Find the minimum years of experience required in the job description.

    Args:
        jd_text: Job description text

    Returns:
        Integer years required, or None if not mentioned
    """
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
        r'minimum\s+(\d+)\s+years?',
        r'at\s+least\s+(\d+)\s+years?',
        r'(\d+)\s*-\s*\d+\s*years?\s*(?:of\s*)?(?:experience|exp)',
    ]

    for pattern in patterns:
        match = re.search(pattern, jd_text.lower())
        if match:
            years = int(match.group(1))
            if 0 < years <= 20:
                return years
    return None


# ════════════════════════════════════════════════════════════════════════════
# SECTION 5 — COMBINED MATCHING ENGINE
# ════════════════════════════════════════════════════════════════════════════

@timer
def match_resume_to_job(resume_data: Dict,
                         job_description: str,
                         resume_skills: List[str]) -> Dict:
    """
    MAIN FUNCTION — Comprehensive resume-to-job matching.

    Combines TF-IDF similarity, semantic similarity, and skill matching
    into a single weighted score with detailed breakdown.

    Args:
        resume_data:    Parsed resume dict from resume_parser.parse_resume()
        job_description: Raw job description text
        resume_skills:  List of skills extracted from the resume

    Returns:
        Comprehensive matching dictionary:
        {
            'overall_score':      float,   # 0-100 weighted combined score
            'tfidf_score':        float,   # 0-100 TF-IDF cosine similarity
            'semantic_score':     float,   # 0-100 semantic similarity
            'skill_match_score':  float,   # 0-100 % of required skills present
            'experience_match':   bool,    # Does candidate meet exp requirement?
            'matched_skills':     list,    # Skills found in both
            'missing_skills':     list,    # Required skills not in resume
            'required_skills':    list,    # All skills required by the JD
            'required_experience': int,    # Years required (None if not stated)
            'match_label':        str,     # 'Excellent', 'Good', 'Poor', etc.
            'recommendations':    list,    # Specific improvement suggestions
        }
    """
    logger.info("Starting resume-to-job matching...")

    resume_text = resume_data.get('raw_text', '')

    if not resume_text or not job_description:
        return {'error': 'Missing resume or job description text'}

    # ── Score 1: TF-IDF Cosine Similarity ─────────────────────────────────
    # Measures word overlap between resume and JD
    tfidf_raw   = compute_tfidf_similarity(resume_text, job_description)
    tfidf_score = tfidf_raw * 100   # Convert 0-1 → 0-100

    # ── Score 2: Semantic Similarity ──────────────────────────────────────
    # Measures MEANING similarity (slower but smarter)
    semantic_raw   = compute_semantic_similarity(resume_text, job_description)
    semantic_score = semantic_raw * 100   # Convert 0-1 → 0-100

    # ── Score 3: Skill Match Score ────────────────────────────────────────
    required_skills = extract_required_skills_from_jd(job_description)

    skill_match_pct = calculate_percentage_match(resume_skills, required_skills)
    missing_skills  = get_missing_skills(resume_skills, required_skills)

    # Skills that appear in BOTH resume and JD
    resume_lower   = {s.lower() for s in resume_skills}
    required_lower = {s.lower() for s in required_skills}
    matched_skills = sorted(list(resume_lower.intersection(required_lower)))

    # ── Score 4: Experience Match ─────────────────────────────────────────
    required_exp = extract_required_experience(job_description)
    candidate_exp = resume_data.get('experience_years', 0)

    experience_match = True   # Default to True if not specified
    if required_exp is not None:
        experience_match = candidate_exp >= required_exp

    # ── Combined Weighted Score ───────────────────────────────────────────
    # We combine all scores with different weights.
    # Skill match is the most important (40%), then semantic (30%), then TF-IDF (20%)
    # Experience match gives a bonus or penalty

    weights = {
        'skill_match': 0.40,    # 40% — skills are the most direct measure
        'semantic':    0.30,    # 30% — meaning/context match
        'tfidf':       0.20,    # 20% — keyword overlap
        'experience':  0.10,    # 10% — experience level match
    }

    experience_score = 100.0 if experience_match else 50.0

    overall_score = (
        skill_match_pct  * weights['skill_match'] +
        semantic_score   * weights['semantic']    +
        tfidf_score      * weights['tfidf']       +
        experience_score * weights['experience']
    )
    overall_score = round(min(100.0, max(0.0, overall_score)), 1)

    # ── Match Label ────────────────────────────────────────────────────────
    if overall_score >= 80:
        match_label = 'Excellent Match'
    elif overall_score >= 65:
        match_label = 'Good Match'
    elif overall_score >= 50:
        match_label = 'Moderate Match'
    elif overall_score >= 35:
        match_label = 'Weak Match'
    else:
        match_label = 'Poor Match'

    # ── Specific Recommendations ───────────────────────────────────────────
    recommendations = _generate_match_recommendations(
        overall_score, missing_skills, experience_match,
        required_exp, candidate_exp, tfidf_score
    )

    result = {
        'overall_score':       overall_score,
        'tfidf_score':         round(tfidf_score, 1),
        'semantic_score':      round(semantic_score, 1),
        'skill_match_score':   round(skill_match_pct, 1),
        'experience_match':    experience_match,
        'matched_skills':      matched_skills,
        'missing_skills':      missing_skills[:15],  # Top 15 missing skills
        'required_skills':     sorted(list(required_lower)),
        'required_experience': required_exp,
        'candidate_experience': candidate_exp,
        'match_label':         match_label,
        'recommendations':     recommendations,
    }

    logger.info(f"Match result: {overall_score:.1f}% ({match_label})")
    return result


def _generate_match_recommendations(
    score: float,
    missing_skills: List[str],
    exp_match: bool,
    required_exp: Optional[int],
    candidate_exp: int,
    tfidf_score: float,
) -> List[str]:
    """
    Generate specific, actionable improvement recommendations.

    Args:
        score:         Overall match score (0-100)
        missing_skills: Skills the resume lacks
        exp_match:     Whether experience requirement is met
        required_exp:  Years required by the job
        candidate_exp: Years the candidate has
        tfidf_score:   Keyword overlap score

    Returns:
        List of recommendation strings
    """
    recs = []

    # Skill gap recommendation
    if missing_skills:
        top_missing = missing_skills[:5]
        recs.append(
            f"Add these missing skills to your resume: "
            f"{', '.join(top_missing)}"
        )

        if len(missing_skills) > 5:
            recs.append(
                f"You are also missing {len(missing_skills) - 5} more skills "
                f"from this job description. Consider upskilling."
            )

    # Experience gap
    if not exp_match and required_exp:
        gap = required_exp - candidate_exp
        recs.append(
            f"This role requires {required_exp} years of experience. "
            f"You have {candidate_exp} years (gap: {gap} years). "
            f"Consider applying to junior/mid-level positions first."
        )

    # Keyword optimization
    if tfidf_score < 40:
        recs.append(
            "Your resume uses very different language than the job description. "
            "Mirror the exact keywords and phrases from the job posting."
        )
    elif tfidf_score < 60:
        recs.append(
            "Add more keywords from the job description into your resume "
            "summary and experience bullet points."
        )

    # Overall score recommendations
    if score >= 80:
        recs.append("Strong match! Tailor your cover letter to highlight your top skills.")
    elif score >= 65:
        recs.append("Good match! Focus on the missing skills to increase your score.")
    elif score >= 50:
        recs.append("Moderate match. Significant skill additions needed before applying.")
    else:
        recs.append(
            "Low match score. This role may not be the best fit right now. "
            "Consider building more relevant skills before applying."
        )

    return recs


# ── Quick test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    resume_text = open(
        "data/sample_resumes/data_scientist_john_smith.txt",
        encoding="utf-8"
    ).read()

    jd = """
    Senior Data Scientist — TechCorp
    Requirements:
    - 4+ years of experience in machine learning and data science
    - Strong Python skills (TensorFlow, PyTorch, scikit-learn)
    - Experience with NLP and computer vision
    - SQL and cloud experience (AWS or GCP)
    - Experience with A/B testing and statistical analysis
    - Excellent communication and leadership skills
    """

    from src.resume_parser import parse_resume_from_text
    from src.skill_extractor import extract_skills

    resume_data   = parse_resume_from_text(resume_text)
    skill_result  = extract_skills(resume_text, resume_data.get('sections'))
    resume_skills = skill_result['all_skills']

    result = match_resume_to_job(resume_data, jd, resume_skills)

    print("\n" + "=" * 60)
    print("JOB MATCHING TEST RESULT")
    print("=" * 60)
    print(f"Overall Score:     {result['overall_score']}%")
    print(f"Match Label:       {result['match_label']}")
    print(f"TF-IDF Score:      {result['tfidf_score']}%")
    print(f"Semantic Score:    {result['semantic_score']}%")
    print(f"Skill Match:       {result['skill_match_score']}%")
    print(f"Experience Match:  {result['experience_match']}")
    print(f"Matched Skills:    {result['matched_skills'][:8]}")
    print(f"Missing Skills:    {result['missing_skills'][:8]}")
    print(f"\nRecommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"  {i}. {rec}")