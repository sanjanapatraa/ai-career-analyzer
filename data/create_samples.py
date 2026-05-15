# data/create_samples.py
# ─────────────────────────────────────────────────────────────────────────
# Creates realistic sample resume text files for testing.
# Run this once to populate data/sample_resumes/
# ─────────────────────────────────────────────────────────────────────────

import os

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_DIR  = os.path.join(BASE_DIR, "data", "sample_resumes")
os.makedirs(SAMPLE_DIR, exist_ok=True)

# ── Sample Resume 1: Data Scientist ───────────────────────────────────────
data_scientist_resume = """
JOHN SMITH
Data Scientist | john.smith@email.com | +91-9876543210
LinkedIn: linkedin.com/in/johnsmith | GitHub: github.com/johnsmith

PROFESSIONAL SUMMARY
Results-driven Data Scientist with 4 years of experience building machine learning
models and deriving business insights from complex datasets. Expertise in Python,
TensorFlow, and statistical modeling. Proven track record of reducing costs and
improving business outcomes through data-driven decisions.

TECHNICAL SKILLS
Languages:    Python, R, SQL, Scala
ML/AI:        TensorFlow, PyTorch, scikit-learn, Keras, XGBoost, LightGBM
Data Tools:   Pandas, NumPy, Matplotlib, Seaborn, Plotly
NLP:          NLTK, spaCy, HuggingFace Transformers, BERT
Big Data:     Apache Spark, Hadoop, Hive, Kafka
Cloud:        AWS (S3, EC2, SageMaker), Google BigQuery
Tools:        Jupyter Notebook, Git, Docker, Airflow, MLflow
Visualization: Tableau, Power BI, Streamlit

WORK EXPERIENCE

Senior Data Scientist — TechCorp India Pvt Ltd (2022-Present)
- Built customer churn prediction model (XGBoost) achieving 94% accuracy,
  saving $2M annually in customer retention costs
- Developed NLP pipeline for sentiment analysis of 500K+ customer reviews
  using BERT, improving product ratings by 18%
- Designed and deployed A/B testing framework that increased conversion by 23%
- Led team of 4 junior data scientists, conducted weekly code reviews
- Reduced model inference time by 60% using ONNX model optimization

Data Scientist — DataSolutions LLC (2020-2022)
- Created demand forecasting models using LSTM reducing inventory costs by $500K
- Built recommendation engine for e-commerce platform (collaborative filtering)
  increasing average order value by 15%
- Automated data pipelines processing 10GB+ daily data using Apache Airflow
- Presented insights to C-level executives through Tableau dashboards

EDUCATION
M.Tech in Data Science — IIT Bombay (2020) — CGPA: 9.2/10
B.Tech in Computer Science — NIT Trichy (2018) — CGPA: 8.8/10

CERTIFICATIONS
- AWS Certified Machine Learning Specialty
- Google Professional Data Engineer
- Coursera Deep Learning Specialization (Andrew Ng)

PROJECTS
- Stock Price Predictor: LSTM model with 89% directional accuracy (GitHub)
- Resume Analyzer: NLP tool that parses resumes and suggests improvements
- Movie Recommendation System: Collaborative filtering with 50K+ users dataset

ACHIEVEMENTS
- Published paper on "Transformer Models for Time Series Forecasting" (2023)
- Won 1st place in Kaggle competition "House Price Prediction" (Top 2%)
- Speaker at DataCon India 2022
"""

# ── Sample Resume 2: Software Engineer ────────────────────────────────────
software_engineer_resume = """
PRIYA PATEL
Software Engineer | priya.patel@gmail.com | +91-9123456789
GitHub: github.com/priyapatel | Portfolio: priyapatel.dev

SUMMARY
Full-stack Software Engineer with 3 years of experience building scalable web
applications and microservices. Strong foundation in system design, distributed
systems, and cloud technologies. Passionate about writing clean, testable code.

SKILLS
Languages:    Java, Python, JavaScript, TypeScript, Go, C++
Backend:      Spring Boot, Node.js, FastAPI, Django, gRPC, REST, GraphQL
Frontend:     React.js, Next.js, TypeScript, HTML5, CSS3, Tailwind CSS
Databases:    PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, DynamoDB
Cloud/DevOps: AWS, Docker, Kubernetes, Jenkins, GitHub Actions, Terraform
Testing:      JUnit, Pytest, Jest, Selenium, Postman
Tools:        Git, JIRA, Confluence, IntelliJ, VS Code, Linux/Unix

EXPERIENCE

Software Engineer II — Amazon India (2022-Present)
- Designed and built microservices handling 2M+ requests/day using Java Spring Boot
- Reduced API response time by 40% through database query optimization and caching
- Led backend development of new checkout feature, increasing revenue by $1.5M/quarter
- Implemented distributed tracing using AWS X-Ray for 20+ microservices
- Mentored 3 junior engineers and conducted technical interviews

Software Engineer — Flipkart (2021-2022)
- Built real-time inventory management system using Kafka and Redis
- Developed GraphQL API consumed by mobile and web clients (5M+ users)
- Reduced system downtime from 2% to 0.01% through improved error handling
- Wrote comprehensive unit and integration tests (95% coverage)

EDUCATION
B.Tech in Computer Science — BITS Pilani (2021) — CGPA: 9.1/10

CERTIFICATIONS
- AWS Certified Solutions Architect — Associate
- Oracle Certified Professional Java SE 11

PROJECTS
- Distributed Task Queue: Go-based task queue supporting 100K tasks/second
- E-Commerce Platform: Full-stack app with React + Node.js + PostgreSQL
- Open Source: Contributed to Spring Framework (150+ GitHub stars)

ACHIEVEMENTS
- Best Employee Award — Amazon Q3 2023
- Competitive Programming: Expert on Codeforces (Rating: 1850)
- Google Summer of Code 2020 — Apache Software Foundation
"""

# ── Sample Resume 3: Recent Graduate (Intentionally Weaker) ───────────────
# This tests our ATS feedback for improvement suggestions
fresher_resume = """
Rahul Kumar
rahul.kumar123@gmail.com
9876543210

OBJECTIVE
I am a computer science student looking for a job in software development.
I have knowledge of programming languages and want to learn more.

EDUCATION
B.Tech Computer Science — ABC Engineering College, Pune (2024)
Percentage: 72%

SKILLS
- C, C++, Java, Python (basic)
- HTML, CSS
- MS Office (Word, Excel, PowerPoint)
- Problem Solving
- Communication skills
- Team player

PROJECTS
1. Library Management System — Created a library management system using Java
2. Calculator App — Made a calculator using HTML and CSS

INTERNSHIP
Web Developer Intern — XYZ Company (June 2023 - August 2023)
- Worked on website development
- Learned about web technologies
- Assisted senior developers

HOBBIES
- Playing cricket
- Watching movies
- Listening to music

DECLARATION
I hereby declare that all the information provided above is true and correct.
"""

# Dictionary of all sample resumes with filename → content
samples = {
    "data_scientist_john_smith.txt":        data_scientist_resume,
    "software_engineer_priya_patel.txt":    software_engineer_resume,
    "fresher_rahul_kumar.txt":              fresher_resume,
}

# Save each resume to a text file
for filename, content in samples.items():
    filepath = os.path.join(SAMPLE_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Created: {filepath}")

print(f"\nAll {len(samples)} sample resumes created in: {SAMPLE_DIR}")
print("Use these to test the resume analyzer in the app!")