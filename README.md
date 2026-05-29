# ResumeIQ - AI ATS and Career Platform

ResumeIQ is a production-style Streamlit application for resume analysis, ATS scoring, job matching, career guidance, recruiter analytics, interview preparation, and learning roadmaps. It is designed as a polished final-year project with a modern SaaS dashboard experience.

## Live Demo

Streamlit Cloud deployment:

https://ai-career-analyzer-yxyzgubyzwcnlbued9sxsl.streamlit.app

## Key Features

| Module | Capability |
| --- | --- |
| Resume Analyzer | Upload a PDF resume or use a sample profile and run structured analysis |
| ATS Dashboard | View score breakdowns, recruiter signals, skill gaps, and candidate snapshots |
| Job Match | Compare a resume against a job description using TF-IDF, skill matching, and experience checks |
| Career Match | Display model-backed career recommendations when trained artifacts are available |
| AI Career Coach | Provide contextual coaching from the latest resume analysis |
| Interview Prep | Generate practical role-specific interview focus areas |
| Learning Roadmap | Build a short action plan from missing skills and improvement signals |
| Recruiter Analytics | Present shortlist-ready hiring metrics and candidate review tables |

## Tech Stack

- Python 3.10+
- Streamlit
- Plotly
- pandas and NumPy
- PyMuPDF and pdfplumber
- spaCy with graceful regex fallback
- scikit-learn and XGBoost
- fpdf2

## Local Setup

```bash
git clone https://github.com/sanjanapatraa/ai-career-analyzer.git
cd ai-career-analyzer

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm

streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## Streamlit Cloud Deployment

This repository is ready for Streamlit Cloud.

Deployment settings:

```text
Repository: sanjanapatraa/ai-career-analyzer
Branch: main
Main file path: app.py
Python dependencies: requirements.txt
System packages: packages.txt
```

The app does not require secrets for the core resume analyzer, ATS dashboard, job matching, recruiter analytics, roadmap, or interview-prep screens.

## Project Structure

```text
ai-career-analyzer/
├── app.py
├── ui/
│   ├── analyzer.py
│   ├── career.py
│   ├── charts.py
│   ├── chatbot.py
│   ├── components.py
│   ├── dashboard.py
│   ├── interview.py
│   ├── jobmatch.py
│   ├── landing.py
│   ├── nav.py
│   ├── recruiter.py
│   ├── roadmap.py
│   └── styles.py
├── src/
│   ├── ats_scorer.py
│   ├── career_recommender.py
│   ├── job_matcher.py
│   ├── report_generator.py
│   ├── resume_parser.py
│   ├── skill_extractor.py
│   └── utils.py
├── config/
│   └── skills_db.json
├── data/
│   └── sample_resumes/
├── tests/
│   └── test_all.py
├── .streamlit/
│   └── config.toml
├── packages.txt
└── requirements.txt
```

## Verification

```bash
python -m compileall app.py ui src/skill_extractor.py test_setup.py
python -m pytest -q
```
