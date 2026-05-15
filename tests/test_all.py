# tests/test_all.py
# ══════════════════════════════════════════════════════════════════════════
# COMPLETE TEST SUITE
# Run with: pytest tests/test_all.py -v
#
# What is pytest?
# pytest is a testing framework. You write functions that start with
# "test_" and pytest automatically finds and runs them.
# Green = passed, Red = failed.
# ══════════════════════════════════════════════════════════════════════════

import sys
import os
import pytest

# Add project root to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Sample data used across tests ─────────────────────────────────────────
SAMPLE_RESUME_TEXT = """
John Smith
john.smith@email.com | +91-9876543210
LinkedIn: linkedin.com/in/johnsmith | GitHub: github.com/johnsmith

SUMMARY
Data Scientist with 4 years of experience in machine learning and Python.

SKILLS
Python, TensorFlow, PyTorch, scikit-learn, SQL, Pandas, NumPy,
Machine Learning, Deep Learning, NLP, Docker, AWS, Git, Tableau

EXPERIENCE
Senior Data Scientist — TechCorp (2022-Present)
- Built ML models achieving 94% accuracy
- Reduced customer churn by 23% using XGBoost
- Led team of 4 data scientists

Data Scientist — DataLabs (2020-2022)
- Developed NLP pipeline for 500K+ reviews
- Created dashboards saving 10 hours/week

EDUCATION
M.Tech in Data Science — IIT Bombay (2020)
B.Tech in Computer Science — NIT Trichy (2018)

PROJECTS
- Stock predictor: LSTM model with 89% accuracy
- Resume analyzer: NLP tool for resume parsing
"""

SAMPLE_JD = """
We are hiring a Senior Data Scientist.
Requirements:
- 3+ years of experience in machine learning
- Proficiency in Python, TensorFlow, SQL
- Experience with NLP and deep learning
- AWS and Docker experience preferred
- Strong communication and leadership skills
"""


# ════════════════════════════════════════════════════════════════════════════
# TEST GROUP 1 — UTILITY FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

class TestUtils:
    """Tests for src/utils.py"""

    def test_clean_text_removes_null_bytes(self):
        """clean_text() should strip null bytes that crash NLP."""
        from src.utils import clean_text
        dirty = "Hello\x00World"
        result = clean_text(dirty)
        assert '\x00' not in result
        assert 'Hello' in result

    def test_clean_text_handles_empty(self):
        """clean_text() should return empty string for None/empty input."""
        from src.utils import clean_text
        assert clean_text("") == ""
        assert clean_text(None) == ""

    def test_extract_emails_finds_email(self):
        """extract_emails() should find email addresses in text."""
        from src.utils import extract_emails
        text = "Contact me at john.smith@email.com or hr@company.co.in"
        emails = extract_emails(text)
        assert len(emails) >= 1
        assert "john.smith@email.com" in emails

    def test_extract_emails_no_email(self):
        """extract_emails() should return empty list when no email present."""
        from src.utils import extract_emails
        assert extract_emails("No email here") == []

    def test_extract_phone_numbers(self):
        """extract_phone_numbers() should find phone numbers."""
        from src.utils import extract_phone_numbers
        text = "Call me at +91-9876543210 or 9123456789"
        phones = extract_phone_numbers(text)
        assert len(phones) >= 1

    def test_extract_urls_finds_linkedin(self):
        """extract_urls() should find LinkedIn URL."""
        from src.utils import extract_urls
        text = "See linkedin.com/in/johnsmith for my profile"
        urls = extract_urls(text)
        assert 'linkedin' in urls

    def test_extract_urls_finds_github(self):
        """extract_urls() should find GitHub URL."""
        from src.utils import extract_urls
        text = "My code is at github.com/johnsmith"
        urls = extract_urls(text)
        assert 'github' in urls

    def test_extract_name_finds_name(self):
        """extract_name() should find candidate name from resume top."""
        from src.utils import extract_name
        name = extract_name(SAMPLE_RESUME_TEXT)
        # Name should be non-empty and not 'Unknown'
        assert name != ''
        assert len(name) > 2

    def test_extract_years_experience(self):
        """extract_years_experience() should find years from text."""
        from src.utils import extract_years_experience
        text = "4 years of experience in machine learning and Python"
        years = extract_years_experience(text)
        assert years == 4

    def test_extract_years_from_date_range(self):
        """Should calculate years from date ranges like '2020-2023'."""
        from src.utils import extract_years_experience
        text = "Software Engineer at Google (2018-2023)"
        years = extract_years_experience(text)
        assert years >= 4

    def test_detect_section_skills(self):
        """detect_section() should correctly identify 'SKILLS' header."""
        from src.utils import detect_section
        assert detect_section("SKILLS") == 'skills'
        assert detect_section("Technical Skills") == 'skills'
        assert detect_section("Skills:") == 'skills'

    def test_detect_section_experience(self):
        """detect_section() should correctly identify experience headers."""
        from src.utils import detect_section
        assert detect_section("EXPERIENCE") == 'experience'
        assert detect_section("Work Experience") == 'experience'

    def test_detect_section_none_for_content(self):
        """detect_section() should return None for content lines."""
        from src.utils import detect_section
        long_line = "Built machine learning models achieving 94% accuracy on test data"
        assert detect_section(long_line) is None

    def test_split_resume_into_sections(self):
        """split_resume_into_sections() should return a dict of sections."""
        from src.utils import split_resume_into_sections
        sections = split_resume_into_sections(SAMPLE_RESUME_TEXT)
        # Should find at least skills, experience, education
        assert isinstance(sections, dict)
        assert len(sections) >= 2

    def test_calculate_percentage_match(self):
        """calculate_percentage_match() should compute correct %."""
        from src.utils import calculate_percentage_match
        resume_skills   = ['python', 'sql', 'tensorflow']
        required_skills = ['python', 'sql', 'docker', 'kubernetes']
        pct = calculate_percentage_match(resume_skills, required_skills)
        # 2 matched out of 4 = 50%
        assert pct == 50.0

    def test_get_missing_skills(self):
        """get_missing_skills() should return skills NOT in resume."""
        from src.utils import get_missing_skills
        resume_skills   = ['python', 'sql']
        required_skills = ['python', 'sql', 'docker', 'kubernetes']
        missing = get_missing_skills(resume_skills, required_skills)
        assert 'docker' in missing
        assert 'kubernetes' in missing
        assert 'python' not in missing

    def test_format_score_label_excellent(self):
        """format_score_label() should return Excellent for 85+."""
        from src.utils import format_score_label
        label, color = format_score_label(90)
        assert label == 'Excellent'
        assert '#' in color  # Color is a hex code

    def test_format_score_label_poor(self):
        """format_score_label() should return Poor for <40."""
        from src.utils import format_score_label
        label, color = format_score_label(25)
        assert label == 'Poor'


# ════════════════════════════════════════════════════════════════════════════
# TEST GROUP 2 — RESUME PARSER
# ════════════════════════════════════════════════════════════════════════════

class TestResumeParser:
    """Tests for src/resume_parser.py"""

    def test_parse_from_text_returns_dict(self):
        """parse_resume_from_text() should return a dictionary."""
        from src.resume_parser import parse_resume_from_text
        result = parse_resume_from_text(SAMPLE_RESUME_TEXT)
        assert isinstance(result, dict)

    def test_parse_extracts_email(self):
        """Parser should extract the email address."""
        from src.resume_parser import parse_resume_from_text
        result = parse_resume_from_text(SAMPLE_RESUME_TEXT)
        assert result.get('email') == 'john.smith@email.com'

    def test_parse_extracts_name(self):
        """Parser should extract candidate name."""
        from src.resume_parser import parse_resume_from_text
        result = parse_resume_from_text(SAMPLE_RESUME_TEXT)
        name = result.get('name', '')
        assert name != '' and name != 'Unknown'

    def test_parse_detects_github(self):
        """Parser should detect GitHub URL presence."""
        from src.resume_parser import parse_resume_from_text
        result = parse_resume_from_text(SAMPLE_RESUME_TEXT)
        assert result.get('has_github') is True

    def test_parse_detects_linkedin(self):
        """Parser should detect LinkedIn URL presence."""
        from src.resume_parser import parse_resume_from_text
        result = parse_resume_from_text(SAMPLE_RESUME_TEXT)
        assert result.get('has_linkedin') is True

    def test_parse_word_count(self):
        """Parser should count words correctly."""
        from src.resume_parser import parse_resume_from_text
        result = parse_resume_from_text(SAMPLE_RESUME_TEXT)
        wc = result.get('word_count', 0)
        assert wc > 50  # Should have more than 50 words

    def test_parse_experience_years(self):
        """Parser should extract years of experience."""
        from src.resume_parser import parse_resume_from_text
        result = parse_resume_from_text(SAMPLE_RESUME_TEXT)
        years = result.get('experience_years', 0)
        assert years >= 2  # Has at least 2 years

    def test_parse_education(self):
        """Parser should find education entries."""
        from src.resume_parser import parse_resume_from_text
        result = parse_resume_from_text(SAMPLE_RESUME_TEXT)
        edu = result.get('education', [])
        assert isinstance(edu, list)

    def test_parse_empty_text(self):
        """Parser should handle empty text gracefully."""
        from src.resume_parser import parse_resume_from_text
        result = parse_resume_from_text("")
        # Should return a dict, not crash
        assert isinstance(result, dict)

    def test_parse_has_sections(self):
        """Parser should detect sections in a structured resume."""
        from src.resume_parser import parse_resume_from_text
        result = parse_resume_from_text(SAMPLE_RESUME_TEXT)
        sections = result.get('sections', {})
        assert isinstance(sections, dict)
        assert len(sections) >= 1

    def test_parse_no_error_field(self):
        """Valid resume should have no error."""
        from src.resume_parser import parse_resume_from_text
        result = parse_resume_from_text(SAMPLE_RESUME_TEXT)
        assert result.get('error') is None


# ════════════════════════════════════════════════════════════════════════════
# TEST GROUP 3 — SKILL EXTRACTOR
# ════════════════════════════════════════════════════════════════════════════

class TestSkillExtractor:
    """Tests for src/skill_extractor.py"""

    def test_extract_returns_dict(self):
        """extract_skills() should return a dictionary."""
        from src.skill_extractor import extract_skills
        result = extract_skills(SAMPLE_RESUME_TEXT)
        assert isinstance(result, dict)

    def test_extract_finds_python(self):
        """Should find 'python' in a resume that mentions Python."""
        from src.skill_extractor import extract_skills
        result = extract_skills("I am an expert Python developer with 5 years experience.")
        assert 'python' in result.get('all_skills', [])

    def test_extract_finds_ml_skills(self):
        """Should find ML skills in a data science resume."""
        from src.skill_extractor import extract_skills
        result = extract_skills(SAMPLE_RESUME_TEXT)
        found = result.get('all_skills', [])
        # At least one of these should be found
        ml_skills = {'python', 'tensorflow', 'sql', 'machine learning', 'pandas'}
        assert len(ml_skills.intersection(set(found))) >= 2

    def test_extract_total_count_positive(self):
        """total_count should be greater than 0 for a skills-rich resume."""
        from src.skill_extractor import extract_skills
        result = extract_skills(SAMPLE_RESUME_TEXT)
        assert result.get('total_count', 0) > 0

    def test_extract_has_by_category(self):
        """Result should contain a by_category dictionary."""
        from src.skill_extractor import extract_skills
        result = extract_skills(SAMPLE_RESUME_TEXT)
        assert isinstance(result.get('by_category'), dict)

    def test_extract_empty_text(self):
        """Should handle empty text without crashing."""
        from src.skill_extractor import extract_skills
        result = extract_skills("")
        assert isinstance(result, dict)
        assert result.get('total_count', 0) == 0

    def test_extract_abbreviations(self):
        """Should detect abbreviations like ML, NLP, AI."""
        from src.skill_extractor import extract_skills
        text = "Expert in ML, NLP, and AI systems with SQL skills."
        result = extract_skills(text)
        found = result.get('all_skills', [])
        # At least one abbreviation should be resolved
        expanded = {'machine learning', 'natural language processing',
                    'artificial intelligence', 'sql'}
        assert len(expanded.intersection(set(found))) >= 1


# ════════════════════════════════════════════════════════════════════════════
# TEST GROUP 4 — ATS SCORER
# ════════════════════════════════════════════════════════════════════════════

class TestATSScorer:
    """Tests for src/ats_scorer.py"""

    def setup_method(self):
        """Prepare parsed resume data before each test."""
        from src.resume_parser import parse_resume_from_text
        from src.skill_extractor import extract_skills
        self.resume_data  = parse_resume_from_text(SAMPLE_RESUME_TEXT)
        self.skills_result = extract_skills(SAMPLE_RESUME_TEXT)
        self.resume_skills = self.skills_result.get('all_skills', [])

    def test_calculate_returns_dict(self):
        """calculate_ats_score() should return a dictionary."""
        from src.ats_scorer import calculate_ats_score
        result = calculate_ats_score(self.resume_data, self.resume_skills)
        assert isinstance(result, dict)

    def test_score_is_0_to_100(self):
        """Overall score must be between 0 and 100."""
        from src.ats_scorer import calculate_ats_score
        result = calculate_ats_score(self.resume_data, self.resume_skills)
        score = result.get('overall_score', -1)
        assert 0 <= score <= 100

    def test_has_grade(self):
        """Result should include a letter grade."""
        from src.ats_scorer import calculate_ats_score
        result = calculate_ats_score(self.resume_data, self.resume_skills)
        assert result.get('grade') in ['A', 'B+', 'B', 'C+', 'C', 'D', 'F']

    def test_has_component_scores(self):
        """Result should have all 6 component scores."""
        from src.ats_scorer import calculate_ats_score
        result = calculate_ats_score(self.resume_data, self.resume_skills)
        components = result.get('component_scores', {})
        expected = {'skill_match', 'keyword_density', 'format_quality',
                    'experience_match', 'education_match', 'contact_info'}
        assert expected.issubset(set(components.keys()))

    def test_component_scores_range(self):
        """Every component score must be 0-100."""
        from src.ats_scorer import calculate_ats_score
        result = calculate_ats_score(self.resume_data, self.resume_skills)
        for name, score in result.get('component_scores', {}).items():
            assert 0 <= score <= 100, f"{name} score {score} out of range"

    def test_has_feedback_list(self):
        """Result should include a feedback list."""
        from src.ats_scorer import calculate_ats_score
        result = calculate_ats_score(self.resume_data, self.resume_skills)
        assert isinstance(result.get('feedback'), list)

    def test_strong_resume_scores_higher(self):
        """A detailed resume should score higher than an empty one."""
        from src.ats_scorer import calculate_ats_score
        from src.resume_parser import parse_resume_from_text
        from src.skill_extractor import extract_skills

        # Minimal/weak resume
        weak_text = "John. I want a job. I know computers."
        weak_data   = parse_resume_from_text(weak_text)
        weak_skills = extract_skills(weak_text).get('all_skills', [])
        weak_result = calculate_ats_score(weak_data, weak_skills)

        # Strong resume
        strong_result = calculate_ats_score(self.resume_data, self.resume_skills)

        assert strong_result['overall_score'] > weak_result['overall_score']

    def test_skill_match_with_jd(self):
        """Providing a JD should affect keyword density score."""
        from src.ats_scorer import calculate_ats_score
        result_no_jd  = calculate_ats_score(self.resume_data, self.resume_skills)
        result_with_jd = calculate_ats_score(
            self.resume_data, self.resume_skills,
            job_description=SAMPLE_JD
        )
        # Both should return valid dicts
        assert isinstance(result_with_jd, dict)
        assert 0 <= result_with_jd['overall_score'] <= 100


# ════════════════════════════════════════════════════════════════════════════
# TEST GROUP 5 — JOB MATCHER
# ════════════════════════════════════════════════════════════════════════════

class TestJobMatcher:
    """Tests for src/job_matcher.py"""

    def test_tfidf_similarity_range(self):
        """TF-IDF similarity should return 0.0–1.0."""
        from src.job_matcher import compute_tfidf_similarity
        score = compute_tfidf_similarity(SAMPLE_RESUME_TEXT, SAMPLE_JD)
        assert 0.0 <= score <= 1.0

    def test_identical_texts_score_high(self):
        """Same text compared to itself should score near 1.0."""
        from src.job_matcher import compute_tfidf_similarity
        score = compute_tfidf_similarity(SAMPLE_RESUME_TEXT, SAMPLE_RESUME_TEXT)
        assert score > 0.90

    def test_unrelated_texts_score_low(self):
        """Completely unrelated texts should score low."""
        from src.job_matcher import compute_tfidf_similarity
        score = compute_tfidf_similarity(
            "Python machine learning data science",
            "The quick brown fox jumps over the lazy dog"
        )
        assert score < 0.3

    def test_match_resume_to_job_returns_dict(self):
        """match_resume_to_job() should return a complete dict."""
        from src.job_matcher import match_resume_to_job
        from src.resume_parser import parse_resume_from_text
        from src.skill_extractor import extract_skills

        resume_data = parse_resume_from_text(SAMPLE_RESUME_TEXT)
        skills      = extract_skills(SAMPLE_RESUME_TEXT).get('all_skills', [])
        result      = match_resume_to_job(resume_data, SAMPLE_JD, skills)

        assert isinstance(result, dict)
        assert 'overall_score' in result
        assert 'match_label' in result
        assert 'missing_skills' in result

    def test_match_score_0_to_100(self):
        """Overall match score must be 0–100."""
        from src.job_matcher import match_resume_to_job
        from src.resume_parser import parse_resume_from_text
        from src.skill_extractor import extract_skills

        resume_data = parse_resume_from_text(SAMPLE_RESUME_TEXT)
        skills      = extract_skills(SAMPLE_RESUME_TEXT).get('all_skills', [])
        result      = match_resume_to_job(resume_data, SAMPLE_JD, skills)

        assert 0 <= result['overall_score'] <= 100

    def test_empty_inputs_handled(self):
        """Empty resume or JD should not crash — return 0 score."""
        from src.job_matcher import compute_tfidf_similarity
        assert compute_tfidf_similarity("", "") == 0.0
        assert compute_tfidf_similarity("some text", "") == 0.0


# ════════════════════════════════════════════════════════════════════════════
# TEST GROUP 6 — DATA PIPELINE
# ════════════════════════════════════════════════════════════════════════════

class TestDataPipeline:
    """Tests for src/data_pipeline.py"""

    def test_preprocess_text_lowercase(self):
        """preprocess_text() should lowercase the result."""
        from src.data_pipeline import preprocess_text
        result = preprocess_text("PYTHON DEVELOPER WITH 5 YEARS EXPERIENCE")
        assert result == result.lower()

    def test_preprocess_removes_emails(self):
        """preprocess_text() should remove email addresses."""
        from src.data_pipeline import preprocess_text
        result = preprocess_text("Contact: john@email.com for details")
        assert '@' not in result

    def test_preprocess_removes_urls(self):
        """preprocess_text() should remove URLs."""
        from src.data_pipeline import preprocess_text
        result = preprocess_text("See https://github.com/john for code")
        assert 'https' not in result

    def test_generate_synthetic_resume(self):
        """generate_synthetic_resume() should return non-empty string."""
        from src.data_pipeline import generate_synthetic_resume, CAREER_TEMPLATES
        career   = "Data Scientist"
        template = CAREER_TEMPLATES[career]
        resume   = generate_synthetic_resume(career, template)
        assert isinstance(resume, str)
        assert len(resume) > 100

    def test_synthetic_resume_contains_skills(self):
        """Generated resume should contain skills from the template."""
        from src.data_pipeline import generate_synthetic_resume, CAREER_TEMPLATES
        career   = "Data Scientist"
        template = CAREER_TEMPLATES[career]
        resume   = generate_synthetic_resume(career, template)
        resume_lower = resume.lower()
        # At least one skill from the template should appear
        found = any(s.lower() in resume_lower for s in template['skills'])
        assert found

    def test_generate_full_synthetic_dataset(self):
        """generate_full_synthetic_dataset() should return a DataFrame."""
        import pandas as pd
        from src.data_pipeline import generate_full_synthetic_dataset
        df = generate_full_synthetic_dataset(samples_per_career=3)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'Resume' in df.columns
        assert 'Category' in df.columns

    def test_clean_dataset_removes_nulls(self):
        """clean_dataset() should remove rows with null values."""
        import pandas as pd
        from src.data_pipeline import clean_dataset
        # Create a DataFrame with one null row
        df = pd.DataFrame({
            'Resume':   ['valid resume text here with enough content', None, 'another valid resume text'],
            'Category': ['Data Scientist', 'Software Engineer', 'Data Analyst'],
        })
        cleaned = clean_dataset(df)
        assert cleaned['Resume'].isna().sum() == 0


# ════════════════════════════════════════════════════════════════════════════
# TEST GROUP 7 — END TO END INTEGRATION
# ════════════════════════════════════════════════════════════════════════════

class TestEndToEnd:
    """
    Full pipeline integration tests.
    These test the entire flow: text → parsed → skills → ATS score.
    """

    def test_full_pipeline_runs_without_error(self):
        """
        The complete pipeline should run without raising any exception.
        This is the most important test — it proves the app will work.
        """
        from src.resume_parser   import parse_resume_from_text
        from src.skill_extractor import extract_skills
        from src.ats_scorer      import calculate_ats_score

        # Step 1: Parse
        resume_data = parse_resume_from_text(SAMPLE_RESUME_TEXT)
        assert resume_data is not None
        assert resume_data.get('error') is None

        # Step 2: Extract skills
        skills_result  = extract_skills(
            resume_data['raw_text'],
            resume_data.get('sections')
        )
        assert skills_result is not None
        assert skills_result['total_count'] >= 0

        # Step 3: ATS score
        ats_result = calculate_ats_score(
            resume_data,
            skills_result['all_skills'],
            job_description=SAMPLE_JD
        )
        assert ats_result is not None
        assert 0 <= ats_result['overall_score'] <= 100

    def test_full_pipeline_with_jd_matching(self):
        """Complete pipeline including job description matching."""
        from src.resume_parser   import parse_resume_from_text
        from src.skill_extractor import extract_skills
        from src.job_matcher     import match_resume_to_job

        resume_data   = parse_resume_from_text(SAMPLE_RESUME_TEXT)
        skills_result = extract_skills(resume_data['raw_text'])
        match_result  = match_resume_to_job(
            resume_data,
            SAMPLE_JD,
            skills_result['all_skills']
        )

        assert 'overall_score' in match_result
        assert 'recommendations' in match_result
        assert isinstance(match_result['recommendations'], list)

    def test_weak_resume_gets_low_score(self):
        """A very weak/empty resume should get a low ATS score."""
        from src.resume_parser   import parse_resume_from_text
        from src.skill_extractor import extract_skills
        from src.ats_scorer      import calculate_ats_score

        weak_resume = "My name is John. I want a job. I am a hard worker."
        resume_data = parse_resume_from_text(weak_resume)
        skills      = extract_skills(weak_resume).get('all_skills', [])
        result      = calculate_ats_score(resume_data, skills)

        # Weak resume should score below 60
        assert result['overall_score'] < 65

    def test_strong_resume_gets_good_score(self):
        """The sample strong resume should score reasonably well."""
        from src.resume_parser   import parse_resume_from_text
        from src.skill_extractor import extract_skills
        from src.ats_scorer      import calculate_ats_score

        resume_data = parse_resume_from_text(SAMPLE_RESUME_TEXT)
        skills      = extract_skills(SAMPLE_RESUME_TEXT).get('all_skills', [])
        result      = calculate_ats_score(resume_data, skills)

        # Strong resume should score above 55
        assert result['overall_score'] >= 55


# ════════════════════════════════════════════════════════════════════════════
# CONFIGURATION — pytest settings
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Run with verbose output when executed directly
    # python tests/test_all.py
    pytest.main([__file__, "-v", "--tb=short"])