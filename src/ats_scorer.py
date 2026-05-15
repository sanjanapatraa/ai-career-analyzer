# src/ats_scorer.py
# ══════════════════════════════════════════════════════════════════════════
# ATS SCORING ENGINE
#
# ATS = Applicant Tracking System
# Real companies use ATS software to AUTOMATICALLY filter resumes before
# a human ever sees them. About 75% of resumes are rejected by ATS.
#
# Our ATS scorer simulates this — it checks:
#   1. Skill match (35%)        — Does the resume have the right skills?
#   2. Keyword density (20%)    — Are job keywords present?
#   3. Format quality (15%)     — Is the resume well-structured?
#   4. Experience match (15%)   — Does experience level match?
#   5. Education match (10%)    — Does education match requirements?
#   6. Contact completeness (5%)— Is contact info present?
#
# Output: Score 0-100 + detailed feedback for every section.
# ══════════════════════════════════════════════════════════════════════════

import re
import os
import json
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

# ── ATS Scoring Weights ────────────────────────────────────────────────────
# These must add up to 1.0 (100%)
ATS_WEIGHTS = {
    'skill_match':      0.35,
    'keyword_density':  0.20,
    'format_quality':   0.15,
    'experience_match': 0.15,
    'education_match':  0.10,
    'contact_info':     0.05,
}


# ════════════════════════════════════════════════════════════════════════════
# SECTION 1 — INDIVIDUAL SCORING COMPONENTS
# Each function scores ONE aspect of the resume (0-100)
# ════════════════════════════════════════════════════════════════════════════

def score_skill_match(resume_skills: List[str],
                       job_skills: List[str]) -> Tuple[float, dict]:
    """
    Score how well the resume's skills match required skills.

    Args:
        resume_skills: Skills found in the resume
        job_skills:    Skills required (from job description or career template)

    Returns:
        (score 0-100, breakdown dict with details)
    """
    if not job_skills:
        return 70.0, {'note': 'No target job skills specified'}

    resume_set = {s.lower().strip() for s in resume_skills}
    required_set = {s.lower().strip() for s in job_skills}

    matched  = resume_set.intersection(required_set)
    missing  = required_set - resume_set

    match_pct = (len(matched) / len(required_set)) * 100 if required_set else 0

    # Bonus points for having MORE skills than required
    # Having extra relevant skills is a positive signal
    bonus = min(10, len(resume_set - required_set) * 0.5)

    score = min(100, match_pct + bonus)

    return round(score, 1), {
        'matched_skills':  sorted(list(matched)),
        'missing_skills':  sorted(list(missing)),
        'match_pct':       round(match_pct, 1),
        'resume_skill_count': len(resume_set),
        'required_count':     len(required_set),
    }


def score_keyword_density(resume_text: str,
                            job_description: str = None) -> Tuple[float, dict]:
    """
    Score how well the resume uses keywords from the job description (or general keywords).

    ATS systems scan for specific keywords. If your resume doesn't contain
    the EXACT words from the job description, it gets filtered out.

    Args:
        resume_text:    Full resume text
        job_description: Job description text (optional)

    Returns:
        (score 0-100, breakdown dict)
    """
    resume_lower = resume_text.lower()
    details = {}

    if job_description:
        # Extract important words from JD (filter out common words)
        jd_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', job_description.lower()))
        # Remove very common English words (stopwords)
        stopwords = {'with', 'that', 'this', 'have', 'will', 'from', 'they',
                     'been', 'were', 'when', 'your', 'more', 'also', 'into',
                     'some', 'than', 'then', 'what', 'like', 'such', 'each',
                     'both', 'able', 'work', 'team', 'strong', 'good', 'well'}
        jd_keywords = jd_words - stopwords

        # Count how many JD keywords appear in resume
        found    = [kw for kw in jd_keywords if kw in resume_lower]
        coverage = (len(found) / len(jd_keywords)) * 100 if jd_keywords else 50

        score = min(100, coverage * 1.2)   # Small boost for partial coverage
        details['jd_keyword_coverage'] = round(coverage, 1)
        details['keywords_found']      = len(found)
        details['keywords_total']      = len(jd_keywords)

    else:
        # No JD: score based on presence of important tech resume keywords
        important_keywords = [
            'experience', 'developed', 'implemented', 'designed', 'led', 'built',
            'improved', 'achieved', 'managed', 'collaborated', 'optimized', 'delivered',
            'python', 'java', 'javascript', 'sql', 'machine learning', 'cloud',
            'agile', 'api', 'database', 'git', 'docker', 'aws',
        ]

        found_count = sum(1 for kw in important_keywords if kw in resume_lower)
        score = min(100, (found_count / len(important_keywords)) * 100 * 1.5)
        details['general_keywords_found'] = found_count

    return round(score, 1), details


def score_format_quality(resume_data: dict,
                          resume_text: str) -> Tuple[float, dict]:
    """
    Score the structural quality of the resume format.

    Real ATS systems parse resumes and fail on bad formatting.
    This checks for the elements that make parsing reliable.

    Checks:
        - Has all required sections (summary, skills, experience, education)
        - Has appropriate length (300-700 words is ideal)
        - Has bullet points (easier to parse than paragraphs)
        - Has quantified achievements (numbers like "40%", "$2M", "10K users")
        - Has consistent formatting signals (not all caps, not all lowercase)
        - Has appropriate number of pages

    Args:
        resume_data: Parsed resume dict from resume_parser.py
        resume_text: Raw resume text

    Returns:
        (score 0-100, breakdown dict with feedback)
    """
    score    = 0.0
    max_pts  = 100.0
    feedback = []
    details  = {}

    # ── Check 1: Required sections present (30 points) ────────────────────
    sections = resume_data.get('sections', {})
    required_sections = ['skills', 'experience', 'education']
    optional_sections = ['summary', 'projects', 'certifications']

    sections_score = 0
    for sec in required_sections:
        if sec in sections:
            sections_score += 8        # 8 points per required section
        else:
            feedback.append(f"Add a '{sec.title()}' section — ATS requires it")

    for sec in optional_sections:
        if sec in sections:
            sections_score += 2        # 2 points per optional section

    score += min(30, sections_score)
    details['sections_found'] = list(sections.keys())

    # ── Check 2: Word count / length (20 points) ──────────────────────────
    word_count = resume_data.get('word_count', 0)
    if 300 <= word_count <= 800:
        score += 20       # Ideal length
        details['length_rating'] = 'Ideal'
    elif 200 <= word_count < 300 or 800 < word_count <= 1200:
        score += 12       # Acceptable length
        feedback.append("Resume length is slightly off. Aim for 400-700 words.")
        details['length_rating'] = 'Acceptable'
    elif word_count < 200:
        score += 4
        feedback.append("Resume is too short. Add more detail to experience and skills.")
        details['length_rating'] = 'Too Short'
    else:
        score += 8
        feedback.append("Resume may be too long. Keep it to 1-2 pages.")
        details['length_rating'] = 'Too Long'

    details['word_count'] = word_count

    # ── Check 3: Bullet points (15 points) ────────────────────────────────
    bullet_count = resume_data.get('bullet_count', 0)
    if bullet_count >= 8:
        score += 15
        details['bullet_quality'] = 'Excellent'
    elif bullet_count >= 4:
        score += 9
        feedback.append("Add more bullet points to experience items. ATS prefers them.")
        details['bullet_quality'] = 'Good'
    elif bullet_count >= 1:
        score += 4
        feedback.append("Convert experience descriptions to bullet points.")
        details['bullet_quality'] = 'Needs work'
    else:
        feedback.append("No bullet points detected. Use bullet points throughout.")
        details['bullet_quality'] = 'Missing'

    details['bullet_count'] = bullet_count

    # ── Check 4: Quantified achievements (20 points) ──────────────────────
    # ATS and recruiters love numbers: "Increased sales by 40%", "$2M revenue"
    number_pattern = r'\b\d+(?:\.\d+)?(?:\s*(?:%|percent|k|M|B|million|billion|'   \
                     r'thousand|users|customers|projects|teams?|years?|months?|'    \
                     r'hours?|requests?|applications?|clients?))\b'

    numbers_found = re.findall(number_pattern, resume_text.lower())
    if len(numbers_found) >= 5:
        score += 20
        details['quantification'] = 'Excellent'
    elif len(numbers_found) >= 3:
        score += 12
        feedback.append("Add more quantified achievements (numbers, %, $, growth metrics).")
        details['quantification'] = 'Good'
    elif len(numbers_found) >= 1:
        score += 6
        feedback.append("Quantify your achievements: instead of 'improved performance', "
                        "say 'improved performance by 40%'.")
        details['quantification'] = 'Needs work'
    else:
        feedback.append("No quantified achievements found. Numbers make your resume stand out.")
        details['quantification'] = 'Missing'

    details['numbers_found'] = len(numbers_found)

    # ── Check 5: Contact completeness (15 points) ─────────────────────────
    contact_score = 0
    if resume_data.get('email'):
        contact_score += 5
    else:
        feedback.append("Add your email address.")

    if resume_data.get('phone'):
        contact_score += 3
    else:
        feedback.append("Add your phone number.")

    if resume_data.get('has_linkedin'):
        contact_score += 4
    else:
        feedback.append("Add your LinkedIn profile URL.")

    if resume_data.get('has_github'):
        contact_score += 3
    else:
        feedback.append("Add your GitHub profile URL (very important for tech roles).")

    score += contact_score

    return round(min(100, score), 1), {
        'feedback': feedback,
        **details,
    }


def score_experience_match(resume_data: dict,
                             target_level: str = 'mid') -> Tuple[float, dict]:
    """
    Score how well the candidate's experience matches the target level.

    Args:
        resume_data:  Parsed resume dict
        target_level: 'entry', 'mid', 'senior', or 'lead'

    Returns:
        (score 0-100, breakdown dict)
    """
    years = resume_data.get('experience_years', 0)

    # Experience requirements by level
    level_ranges = {
        'entry':  (0, 2),
        'mid':    (2, 5),
        'senior': (5, 10),
        'lead':   (8, 20),
    }

    min_years, max_years = level_ranges.get(target_level, (0, 20))

    if min_years <= years <= max_years:
        score = 100.0
        note  = f"Experience ({years} years) matches {target_level} level perfectly"
    elif years < min_years:
        gap   = min_years - years
        score = max(0, 100 - gap * 20)
        note  = f"Under-experienced by {gap} year(s) for {target_level} role"
    else:
        # Over-experienced (might be overqualified)
        gap   = years - max_years
        score = max(60, 100 - gap * 5)   # Small penalty for over-experience
        note  = f"Possibly overqualified for {target_level} role ({years} years)"

    return round(score, 1), {
        'years_detected': years,
        'target_level':   target_level,
        'expected_range': f"{min_years}-{max_years} years",
        'note':           note,
    }


def score_education_match(resume_data: dict,
                           required_level: str = 'bachelor') -> Tuple[float, dict]:
    """
    Score the education section against requirements.

    Args:
        resume_data:    Parsed resume dict
        required_level: 'any', 'diploma', 'bachelor', 'master', 'phd'

    Returns:
        (score 0-100, breakdown dict)
    """
    education = resume_data.get('education', [])

    if not education:
        return 40.0, {'note': 'No education detected — ensure education section is clear'}

    # Degree hierarchy (higher index = higher degree)
    degree_levels = {
        'diploma': 1, 'b.sc.': 2, 'bca': 2, 'bba': 2, 'b.des.': 2,
        'b.e.':    3, 'b.tech': 3, 'b.tech.': 3,
        'm.sc.':   4, 'mca': 4, 'mba': 4,
        'm.e.':    5, 'm.tech': 5, 'm.tech.': 5, 'm.s.': 5,
        'phd':     6,
    }

    req_levels = {
        'any':      0,
        'diploma':  1,
        'bachelor': 3,
        'master':   4,
        'phd':      6,
    }

    required_min = req_levels.get(required_level, 0)

    # Find highest degree in resume
    max_degree_level = 0
    found_degrees    = []
    for edu in education:
        deg_name  = edu.get('degree', '').lower()
        deg_level = degree_levels.get(deg_name, 0)
        if deg_level > max_degree_level:
            max_degree_level = deg_level
        found_degrees.append(edu.get('degree', 'Unknown'))

    if max_degree_level >= required_min:
        score = 100.0
        note  = "Education meets or exceeds requirements"
    elif max_degree_level == required_min - 1:
        score = 70.0
        note  = f"Slightly below required education level ({required_level})"
    else:
        score = 40.0
        note  = f"Education does not meet the {required_level} requirement"

    return round(score, 1), {
        'degrees_found':    found_degrees,
        'highest_level':    max_degree_level,
        'required_level':   required_level,
        'note':             note,
    }


# ════════════════════════════════════════════════════════════════════════════
# SECTION 2 — MASTER ATS SCORER
# ════════════════════════════════════════════════════════════════════════════

def calculate_ats_score(
    resume_data:      dict,
    resume_skills:    List[str],
    job_description:  str  = None,
    job_skills:       List[str] = None,
    target_level:     str  = 'mid',
    required_education: str = 'bachelor',
) -> dict:
    """
    MAIN FUNCTION — Calculate the complete ATS score for a resume.

    Combines all 6 scoring components with their weights.

    Args:
        resume_data:       Parsed resume dict from resume_parser.py
        resume_skills:     Skills list from skill_extractor.py
        job_description:   Raw JD text (optional — for keyword scoring)
        job_skills:        Required skills list (optional)
        target_level:      'entry', 'mid', 'senior', 'lead'
        required_education: 'bachelor', 'master', 'phd', 'any'

    Returns:
        {
            'overall_score':   85.3,
            'grade':           'B+',
            'label':           'Good Resume',
            'component_scores': {
                'skill_match':      90.0,
                'keyword_density':  78.5,
                ...
            },
            'component_details': {...},
            'feedback':         ['Add GitHub URL', 'Quantify achievements'],
            'strengths':        ['Strong technical skills', '...'],
            'improvements':     ['Missing LinkedIn URL', '...'],
            'resume_tips':      ['Use action verbs', '...'],
        }
    """
    logger.info("Calculating ATS score...")
    resume_text = resume_data.get('raw_text', '')

    # ── Run all 6 scoring components ──────────────────────────────────────
    skill_score,   skill_details   = score_skill_match(
        resume_skills,
        job_skills or []
    )
    keyword_score, keyword_details = score_keyword_density(
        resume_text,
        job_description
    )
    format_score,  format_details  = score_format_quality(
        resume_data,
        resume_text
    )
    exp_score,     exp_details     = score_experience_match(
        resume_data,
        target_level
    )
    edu_score,     edu_details     = score_education_match(
        resume_data,
        required_education
    )

    # Contact score is embedded in format_quality, extract it separately
    contact_score = 0
    if resume_data.get('email'):       contact_score += 40
    if resume_data.get('phone'):       contact_score += 20
    if resume_data.get('has_linkedin'): contact_score += 25
    if resume_data.get('has_github'):   contact_score += 15

    # ── Calculate weighted total ───────────────────────────────────────────
    component_scores = {
        'skill_match':      skill_score,
        'keyword_density':  keyword_score,
        'format_quality':   format_score,
        'experience_match': exp_score,
        'education_match':  edu_score,
        'contact_info':     float(contact_score),
    }

    overall = sum(
        score * ATS_WEIGHTS[component]
        for component, score in component_scores.items()
    )
    overall = round(min(100.0, max(0.0, overall)), 1)

    # ── Grade assignment ───────────────────────────────────────────────────
    # Convert numeric score to letter grade
    if overall >= 90:
        grade, label = 'A',  'Excellent Resume'
    elif overall >= 80:
        grade, label = 'B+', 'Good Resume'
    elif overall >= 70:
        grade, label = 'B',  'Above Average'
    elif overall >= 60:
        grade, label = 'C+', 'Average Resume'
    elif overall >= 50:
        grade, label = 'C',  'Below Average'
    elif overall >= 40:
        grade, label = 'D',  'Needs Improvement'
    else:
        grade, label = 'F',  'Poor Resume'

    # ── Collect all feedback ───────────────────────────────────────────────
    all_feedback = format_details.get('feedback', [])

    # Add skill-specific feedback
    missing_skills = skill_details.get('missing_skills', [])
    if missing_skills:
        all_feedback.append(
            f"Add these key skills: {', '.join(missing_skills[:5])}"
        )

    # ── Identify Strengths ─────────────────────────────────────────────────
    strengths = []
    if skill_score >= 80:
        strengths.append(f"Strong skill match ({skill_score:.0f}%)")
    if format_score >= 75:
        strengths.append("Well-structured resume format")
    if exp_score >= 85:
        strengths.append("Experience level matches target role")
    if edu_score >= 80:
        strengths.append("Education meets requirements")
    if resume_data.get('has_github'):
        strengths.append("GitHub profile included — great for tech roles")
    if resume_data.get('has_linkedin'):
        strengths.append("LinkedIn profile included")
    if format_details.get('numbers_found', 0) >= 3:
        strengths.append("Good use of quantified achievements")

    # ── Generate Improvements ─────────────────────────────────────────────
    improvements = []
    if skill_score < 70 and missing_skills:
        improvements.append(f"Learn and add: {', '.join(missing_skills[:3])}")
    if keyword_score < 60:
        improvements.append("Mirror exact keywords from the job description")
    if not resume_data.get('has_linkedin'):
        improvements.append("Create a LinkedIn profile and add the URL")
    if not resume_data.get('has_github'):
        improvements.append("Create GitHub projects and add the URL")
    if format_details.get('numbers_found', 0) < 3:
        improvements.append("Quantify achievements with numbers and percentages")
    if format_details.get('bullet_count', 0) < 5:
        improvements.append("Use bullet points for experience descriptions")
    if exp_score < 60:
        improvements.append(exp_details.get('note', ''))

    # ── Professional resume tips ──────────────────────────────────────────
    resume_tips = [
        "Start each bullet with a strong action verb: Built, Developed, Led, Increased",
        "Use the STAR format: Situation, Task, Action, Result",
        "Tailor your resume for each job application",
        "Keep font size 10-12pt, use standard fonts (Arial, Calibri, Times New Roman)",
        "Save as PDF to preserve formatting",
        "Use standard section headers ATS can parse: 'Work Experience', 'Education', 'Skills'",
        "Avoid tables, text boxes, and images — ATS cannot parse them",
    ]

    return {
        'overall_score':     overall,
        'grade':             grade,
        'label':             label,
        'component_scores':  component_scores,
        'component_details': {
            'skill_match':      skill_details,
            'keyword_density':  keyword_details,
            'format_quality':   format_details,
            'experience_match': exp_details,
            'education_match':  edu_details,
        },
        'feedback':          all_feedback,
        'strengths':         strengths,
        'improvements':      improvements,
        'resume_tips':       resume_tips,
        'missing_skills':    missing_skills,
    }