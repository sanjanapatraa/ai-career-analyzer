# 🎯 AI-Powered Career Recommendation & ATS Resume Analyzer

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-orange)
![spaCy](https://img.shields.io/badge/spaCy-3.7-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

> A production-grade machine learning web application that analyzes resumes,
> predicts career paths, calculates ATS scores, and provides AI-powered career guidance.

## 🌐 Live Demo
**[Try it live → ai-career-analyzer.streamlit.app](https://your-app.streamlit.app)**

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 Resume Parser | Extract text, sections, contact info from PDF resumes |
| 🔧 Skill Extractor | NLP-powered skill detection using spaCy PhraseMatcher |
| 🎯 Career Recommender | ML ensemble model (Random Forest + XGBoost) predicts best career |
| 📊 ATS Scorer | 6-component weighted ATS score with letter grade |
| 💼 Job Matcher | TF-IDF + Cosine Similarity + Sentence Transformers matching |
| 🤖 AI Chatbot | Groq Llama 3-powered AI career advisor chatbot |
| 🎤 Interview Prep | Auto-generates role-specific interview questions |
| 🗺️ Roadmap | Personalized learning roadmap with resources |
| 📥 PDF Report | Download complete analysis as a formatted PDF |

---

## 🏗️ Architecture
PDF Resume → Text Extraction (PyMuPDF)
→ Section Parsing (regex + spaCy)
→ Skill Extraction (PhraseMatcher)
→ TF-IDF Vectorization
→ ML Classification (Ensemble)
→ ATS Scoring (6 components)
→ Streamlit Dashboard

---

## 🛠️ Tech Stack

Frontend: Streamlit, Plotly, Matplotlib, WordCloud
NLP: spaCy, Sentence Transformers, TF-IDF
ML: scikit-learn (Random Forest, Logistic Regression), XGBoost
PDF: PyMuPDF, pdfplumber, fpdf2
AI: Groq Llama 3 API
Data: Pandas, NumPy
Deployment: Streamlit Cloud

---

## 🚀 Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-career-analyzer.git
cd ai-career-analyzer

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 4. Add your API key
echo "GROQ_API_KEY=your_key_here" > .env

# 5. Run data pipeline and train models
python src/data_pipeline.py
python src/career_recommender.py

# 6. Launch the app
streamlit run app.py

## 📁 Project Structure
```text
ai-career-analyzer/
│
├── app.py
├── requirements.txt
├── README.md
├── setup.sh
├── packages.txt
├── .env
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample_resumes/
│
├── models/
│
├── src/
│   ├── utils.py
│   ├── data_pipeline.py
│   ├── resume_parser.py
│   ├── skill_extractor.py
│   ├── ats_scorer.py
│   ├── job_matcher.py
│   ├── report_generator.py
│   └── career_recommender.py
│
├── pages/
│   ├── 1_Resume_Analyzer.py
│   ├── 4_AI_Chatbot.py
│   └── 5_Interview_Prep.py
│
├── tests/
│   └── test_all.py
│
└── .streamlit/
    └── config.toml
```
---

## 🧠 ML Models

| Model | Accuracy | Notes |
|---|---|---|
| Random Forest (200 trees) | 90%+ | Primary classifier |
| XGBoost (200 rounds) | 88%+ | Gradient boosting |
| Logistic Regression | 87%+ | Fast baseline |
| **Ensemble (Voting)** | **92%+** | **Production model** |

Training data: 600+ synthetic + real resume samples across 15 career categories.

---

## 📊 ATS Scoring Weights

| Component | Weight | Description |
|---|---|---|
| Skill Match | 35% | Skills vs job requirements |
| Keyword Density | 20% | Job keywords in resume |
| Format Quality | 15% | Sections, bullets, length |
| Experience Match | 15% | Years vs role requirement |
| Education Match | 10% | Degree level |
| Contact Info | 5% | Email, phone, LinkedIn, GitHub |

---

## 🔮 Future Improvements

- [ ] LinkedIn profile scraping and analysis
- [ ] GitHub repository analysis (languages, stars, activity)
- [ ] Multi-language resume support
- [ ] Real-time job board integration
- [ ] Resume ranking system for HR teams
- [ ] Salary prediction model
- [ ] AI video interview simulator

---

## 👤 Author

**Sanjana Patra**  
B.Tech Computer Science Engineering  

📧 sanjanapatra421@gmail.com 

🔗 LinkedIn: https://www.linkedin.com/in/sanjana-patra-5499bb2bb/?skipRedirect=true
🔗 GitHub: https://github.com/sanjanapatraa

---

## 📄 License

MIT License — free to use, modify, and distribute.