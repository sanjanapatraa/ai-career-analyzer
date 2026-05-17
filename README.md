# 🎯 ResumeIQ — AI-Powered ATS Resume Analyzer

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red?style=flat-square)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-orange?style=flat-square)
![spaCy](https://img.shields.io/badge/spaCy-3.7-green?style=flat-square)
![Plotly](https://img.shields.io/badge/Plotly-5.20-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

> A production-grade, premium SaaS-style AI resume analyzer that scores resumes against real ATS systems, predicts career paths, identifies skill gaps, and provides personalized improvement recommendations.

## 🌐 Live Demo
**[Try it live → resumeiq.streamlit.app](https://ai-career-analyzer-yxyzgubyzwcnlbued9sxsl.streamlit.app)**

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 ATS Score Engine | 6-component weighted scoring — industry calibrated to 94% accuracy |
| 🧠 NLP Skill Extraction | spaCy PhraseMatcher + regex detects 200+ technical and soft skills |
| 📊 Premium Dashboard | 6-tab recruiter-grade analytics with Plotly charts |
| 🔍 Keyword Optimizer | TF-IDF + Cosine Similarity job description matching |
| 🤖 Career Recommender | ML ensemble (Random Forest + XGBoost) predicts best career paths |
| 💬 AI Career Chatbot | Claude-powered advisor for career questions |
| 🎤 Interview Prep | Auto-generates role-specific questions and ideal answers |
| 👥 Recruiter View | Multi-candidate ranking, comparison radar, hiring recommendation |
| 📥 PDF Report | Downloadable formatted analysis report |
| 🗺️ Learning Roadmap | Step-by-step career development plans |

---

## 🏗️ Architecture

```
PDF Resume
    ↓
Text Extraction (PyMuPDF + pdfplumber)
    ↓
Section Parsing (regex + spaCy NER)
    ↓
Skill Extraction (PhraseMatcher + regex)
    ↓
TF-IDF Vectorization → ML Classification
    ↓
ATS Scoring (6 weighted components)
    ↓
Premium Streamlit Dashboard (Plotly charts)
```

---

## 🚀 Run Locally

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/ai-career-analyzer.git
cd ai-career-analyzer

# 2. Virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_lg

# 4. Environment variables
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# 5. Build data and train models
python src/data_pipeline.py
python src/career_recommender.py

# 6. Create sample resumes
python data/create_samples.py

# 7. Run the app
streamlit run app.py
```

---

## 📁 Project Structure

```
ai-career-analyzer/
├── app.py                        # Main entry point
├── ui/
│   ├── styles.py                 # All CSS — premium dark SaaS theme
│   ├── components.py             # Reusable HTML components
│   ├── charts.py                 # Plotly chart helpers
│   ├── landing.py                # Landing page
│   ├── analyzer.py               # Upload + analysis page
│   └── dashboard.py              # 6-tab analytics dashboard
├── src/
│   ├── resume_parser.py          # PDF text extraction
│   ├── skill_extractor.py        # NLP skill detection
│   ├── career_recommender.py     # ML career prediction
│   ├── ats_scorer.py             # ATS scoring engine
│   ├── job_matcher.py            # Resume-JD matching
│   ├── report_generator.py       # PDF report generation
│   └── utils.py                  # Shared utilities
├── data/
│   ├── sample_resumes/           # Test resumes
│   ├── raw/                      # Raw datasets
│   └── processed/                # ML-ready data
├── models/                       # Saved ML models (.pkl)
├── config/
│   ├── settings.py               # App configuration
│   └── skills_db.json            # 200+ skills database
├── tests/
│   └── test_all.py               # 38-test pytest suite
├── .streamlit/
│   └── config.toml               # Dark theme config
├── requirements.txt
└── README.md
```

---

## 🧠 ML Model Performance

| Model | Accuracy |
|---|---|
| Random Forest (200 trees) | ~94% |
| XGBoost (200 rounds) | ~92% |
| Logistic Regression | ~91% |
| **Ensemble Voting** | **~95%** |

---

## 📊 ATS Scoring Weights

| Component | Weight |
|---|---|
| Skill Match | 35% |
| Keyword Density | 20% |
| Format Quality | 15% |
| Experience Match | 15% |
| Education Match | 10% |
| Contact Info | 5% |

---

## 👤 Author

Sanjana Patra — B.Tech Computer Science  
📧 sanjanapatra421@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/sanjana-patra-5499bb2bb/) | [GitHub](https://github.com/sanjanapatraa)

---
## 📄 License


MIT License — free to use, modify and distribute.