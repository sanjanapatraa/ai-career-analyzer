# src/data_pipeline.py
# ══════════════════════════════════════════════════════════════════════════
# PHASE 3 — Complete Data Pipeline
# This file does EVERYTHING with data:
#   1. Load the raw Kaggle dataset
#   2. Generate synthetic resume samples (so we have more training data)
#   3. Clean all the messy text
#   4. Preprocess (make text machine-friendly)
#   5. Engineer features (extract patterns ML can learn from)
#   6. Save clean data for ML training
# ══════════════════════════════════════════════════════════════════════════

# ── Standard library imports ──────────────────────────────────────────────
import os           # Working with file paths and folders
import re           # Regular expressions — for finding/removing text patterns
import json         # Reading/writing JSON files
import logging      # Printing progress messages in a structured way
import warnings     # Suppressing unnecessary warning messages
warnings.filterwarnings('ignore')  # Hide warnings so output is cleaner

# ── Third-party library imports ───────────────────────────────────────────
import pandas as pd         # DataFrames — like Excel tables in Python
import numpy as np          # Number arrays and math operations
import spacy                # NLP library — understands English text
from tqdm import tqdm       # Shows a progress bar while processing data
import joblib               # Saves Python objects to disk (like models)

# sklearn = scikit-learn, our ML library
from sklearn.preprocessing import LabelEncoder   # Converts text labels to numbers
from sklearn.model_selection import train_test_split  # Splits data into train/test sets
from sklearn.feature_extraction.text import TfidfVectorizer  # Converts text to numbers

# ── Setup logging ─────────────────────────────────────────────────────────
# logging gives us nice timestamped messages instead of plain print()
logging.basicConfig(
    level=logging.INFO,                              # Show INFO and above messages
    format='%(asctime)s — %(levelname)s — %(message)s',  # Message format
    datefmt='%H:%M:%S'                               # Time format
)
logger = logging.getLogger(__name__)  # Create a logger for this file

# ── Path Setup ────────────────────────────────────────────────────────────
# os.path.dirname(__file__) = folder containing this file (src/)
# Going up one level gets us the project root
BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR      = os.path.join(BASE_DIR, "data", "raw")        # Where raw data lives
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed") # Where clean data goes
MODELS_DIR   = os.path.join(BASE_DIR, "models")             # Where we save models
CONFIG_DIR   = os.path.join(BASE_DIR, "config")             # Config files

# Create folders if they don't exist yet
# exist_ok=True means "don't crash if the folder already exists"
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 1 — SYNTHETIC DATA GENERATOR
# Why? The Kaggle dataset has 962 rows. More data = better ML accuracy.
# We'll generate realistic fake resumes so our model learns better.
# ════════════════════════════════════════════════════════════════════════════

# This dictionary maps every career to skills, tools, and experience phrases.
# It's like a template library for generating realistic resumes.
CAREER_TEMPLATES = {
    "Data Scientist": {
        "skills": [
            "Python", "R", "Machine Learning", "Deep Learning", "TensorFlow",
            "PyTorch", "scikit-learn", "Pandas", "NumPy", "Statistics",
            "SQL", "Tableau", "Power BI", "Natural Language Processing",
            "Computer Vision", "Jupyter Notebook", "Feature Engineering",
            "A/B Testing", "Hypothesis Testing", "Data Visualization"
        ],
        "experience_phrases": [
            "Built predictive models achieving 94% accuracy",
            "Analyzed large datasets using Python and SQL",
            "Deployed machine learning models to production",
            "Conducted A/B tests to optimize business metrics",
            "Created dashboards for executive reporting",
            "Developed NLP models for text classification",
            "Reduced customer churn by 23% using ML models",
            "Processed and cleaned datasets with 10M+ rows",
        ],
        "education": ["B.Tech in Computer Science", "M.S. in Data Science",
                      "B.Sc. in Statistics", "PhD in Machine Learning"],
    },
    "Software Engineer": {
        "skills": [
            "Java", "Python", "C++", "JavaScript", "TypeScript", "Go",
            "React", "Node.js", "Spring Boot", "Microservices", "REST API",
            "Docker", "Kubernetes", "AWS", "Git", "CI/CD", "Agile",
            "PostgreSQL", "MongoDB", "Redis", "System Design", "DSA"
        ],
        "experience_phrases": [
            "Developed scalable backend systems handling 1M requests/day",
            "Built RESTful APIs consumed by 500K+ users",
            "Reduced system latency by 40% through optimization",
            "Led migration from monolith to microservices architecture",
            "Implemented CI/CD pipelines reducing deployment time by 60%",
            "Wrote unit tests achieving 95% code coverage",
            "Designed and implemented database schemas for high-traffic apps",
            "Collaborated with cross-functional teams in Agile environment",
        ],
        "education": ["B.Tech in Computer Science", "B.E. in Information Technology",
                      "M.Tech in Software Engineering"],
    },
    "Machine Learning Engineer": {
        "skills": [
            "Python", "TensorFlow", "PyTorch", "Keras", "scikit-learn",
            "MLflow", "Kubeflow", "Docker", "Kubernetes", "AWS SageMaker",
            "Feature Engineering", "Model Deployment", "ONNX", "FastAPI",
            "Spark", "Hadoop", "Deep Learning", "NLP", "Computer Vision",
            "LangChain", "Hugging Face", "BERT", "GPT", "RAG"
        ],
        "experience_phrases": [
            "Deployed ML models serving 10M predictions per day",
            "Reduced model inference time by 70% using ONNX optimization",
            "Built MLOps pipeline for automated model retraining",
            "Fine-tuned large language models for domain-specific tasks",
            "Implemented real-time recommendation system using collaborative filtering",
            "Designed feature store used by 5 ML teams",
        ],
        "education": ["M.Tech in AI/ML", "B.Tech in Computer Science",
                      "PhD in Deep Learning"],
    },
    "Data Analyst": {
        "skills": [
            "SQL", "Python", "Excel", "Tableau", "Power BI", "Google Analytics",
            "Pandas", "NumPy", "Statistics", "Data Visualization", "ETL",
            "Data Warehousing", "BigQuery", "Looker", "R", "SPSS", "SAS"
        ],
        "experience_phrases": [
            "Analyzed sales data to identify 15% revenue growth opportunity",
            "Created weekly executive dashboards using Tableau",
            "Wrote complex SQL queries for business intelligence reporting",
            "Built automated ETL pipelines for data warehousing",
            "Performed cohort analysis to understand customer behavior",
            "Reduced reporting time from 2 days to 2 hours through automation",
        ],
        "education": ["B.Sc. in Statistics", "BBA in Business Analytics",
                      "B.Tech in Computer Science"],
    },
    "Frontend Developer": {
        "skills": [
            "HTML", "CSS", "JavaScript", "TypeScript", "React", "Vue.js",
            "Next.js", "Angular", "Tailwind CSS", "Bootstrap", "Redux",
            "GraphQL", "Webpack", "Vite", "Jest", "Cypress", "Figma",
            "Responsive Design", "Web Accessibility", "Performance Optimization"
        ],
        "experience_phrases": [
            "Built responsive web applications used by 200K+ users",
            "Improved page load speed by 50% through code optimization",
            "Implemented pixel-perfect UI from Figma designs",
            "Built reusable component library used across 8 projects",
            "Reduced bundle size by 40% using code splitting and lazy loading",
        ],
        "education": ["B.Tech in Computer Science", "B.Sc. in Information Technology"],
    },
    "Backend Developer": {
        "skills": [
            "Python", "Java", "Node.js", "Go", "C#", "Django", "Flask",
            "FastAPI", "Spring Boot", "Express.js", "PostgreSQL", "MySQL",
            "MongoDB", "Redis", "RabbitMQ", "Kafka", "Docker", "AWS", "REST API"
        ],
        "experience_phrases": [
            "Designed and built high-performance REST APIs",
            "Optimized database queries reducing response time by 60%",
            "Implemented message queuing system handling 100K messages/hour",
            "Built authentication and authorization system for SaaS platform",
            "Designed microservices architecture for e-commerce platform",
        ],
        "education": ["B.Tech in Computer Science", "B.E. in Information Technology"],
    },
    "DevOps Engineer": {
        "skills": [
            "Docker", "Kubernetes", "Jenkins", "GitHub Actions", "Terraform",
            "Ansible", "AWS", "Azure", "GCP", "Linux", "Bash", "Python",
            "Prometheus", "Grafana", "ELK Stack", "Nginx", "CI/CD", "Git",
            "CloudFormation", "Helm", "ArgoCD", "Vault"
        ],
        "experience_phrases": [
            "Managed Kubernetes clusters running 500+ microservices",
            "Reduced infrastructure costs by 35% through optimization",
            "Automated deployment pipeline reducing release time from 2 hours to 15 minutes",
            "Implemented monitoring and alerting for 99.99% uptime SLA",
            "Led cloud migration of on-premises workloads to AWS",
        ],
        "education": ["B.Tech in Computer Science", "B.E. in Information Technology"],
    },
    "Cybersecurity Analyst": {
        "skills": [
            "Network Security", "Penetration Testing", "SIEM", "Splunk",
            "Python", "Wireshark", "Metasploit", "Burp Suite", "Nmap",
            "Firewalls", "IDS/IPS", "Vulnerability Assessment", "OWASP",
            "ISO 27001", "CISSP", "CEH", "Threat Intelligence", "SOC"
        ],
        "experience_phrases": [
            "Conducted penetration testing for 50+ enterprise clients",
            "Reduced security incidents by 45% through proactive monitoring",
            "Implemented SIEM solution for real-time threat detection",
            "Performed vulnerability assessments and risk analysis",
            "Led incident response team for critical security breaches",
        ],
        "education": ["B.Tech in Computer Science", "B.Sc. in Cybersecurity"],
    },
    "Full Stack Developer": {
        "skills": [
            "React", "Node.js", "Python", "JavaScript", "TypeScript",
            "PostgreSQL", "MongoDB", "Docker", "AWS", "REST API", "GraphQL",
            "HTML", "CSS", "Tailwind", "Redis", "Git", "Agile", "Next.js"
        ],
        "experience_phrases": [
            "Built end-to-end web applications from design to deployment",
            "Developed SaaS platform with 10K+ active users",
            "Integrated payment gateways processing $1M+ monthly transactions",
            "Built real-time features using WebSockets",
        ],
        "education": ["B.Tech in Computer Science", "B.E. in Software Engineering"],
    },
    "Cloud Architect": {
        "skills": [
            "AWS", "Azure", "GCP", "Kubernetes", "Terraform", "Docker",
            "Microservices", "Serverless", "CloudFormation", "VPC",
            "IAM", "S3", "EC2", "Lambda", "RDS", "EKS", "Python", "Bash"
        ],
        "experience_phrases": [
            "Architected cloud solutions for Fortune 500 companies",
            "Designed multi-region, high-availability infrastructure",
            "Reduced cloud costs by $2M annually through optimization",
            "Led team of 8 engineers in cloud-native transformation",
        ],
        "education": ["B.Tech in Computer Science", "M.Tech in Cloud Computing"],
    },
    "Product Manager": {
        "skills": [
            "Product Roadmap", "Agile", "Scrum", "JIRA", "User Research",
            "Data Analysis", "SQL", "A/B Testing", "Wireframing", "Figma",
            "Stakeholder Management", "Go-to-Market", "OKRs", "KPIs",
            "Competitive Analysis", "User Stories", "Product Strategy"
        ],
        "experience_phrases": [
            "Led product roadmap for SaaS platform with $10M ARR",
            "Increased user retention by 35% through feature improvements",
            "Managed cross-functional team of 15 engineers and designers",
            "Launched 3 major product features with 95% user satisfaction",
        ],
        "education": ["MBA", "B.Tech in Computer Science", "B.Sc. in Business"],
    },
    "Business Analyst": {
        "skills": [
            "SQL", "Excel", "Tableau", "Power BI", "Business Process Modeling",
            "Requirements Gathering", "JIRA", "Agile", "Stakeholder Management",
            "Data Analysis", "Python", "Visio", "BPMN", "User Stories"
        ],
        "experience_phrases": [
            "Gathered and documented requirements for 20+ enterprise projects",
            "Reduced process inefficiencies saving $500K annually",
            "Created business process models improving operational efficiency",
            "Facilitated workshops with C-level stakeholders",
        ],
        "education": ["BBA", "MBA", "B.Tech in Computer Science"],
    },
    "UI/UX Designer": {
        "skills": [
            "Figma", "Adobe XD", "Sketch", "InVision", "Prototyping",
            "User Research", "Usability Testing", "Wireframing", "HTML", "CSS",
            "Design Systems", "Accessibility", "Information Architecture",
            "User Journey Mapping", "A/B Testing", "Adobe Illustrator"
        ],
        "experience_phrases": [
            "Designed app interfaces for 1M+ user base",
            "Improved conversion rate by 28% through UX redesign",
            "Created design system adopted by 5 product teams",
            "Conducted 50+ user interviews to inform product decisions",
        ],
        "education": ["B.Des. in UI/UX", "B.Sc. in Human-Computer Interaction"],
    },
    "Database Administrator": {
        "skills": [
            "MySQL", "PostgreSQL", "Oracle", "SQL Server", "MongoDB",
            "Redis", "Database Design", "Query Optimization", "Backup Recovery",
            "Replication", "Sharding", "Performance Tuning", "PL/SQL", "Python"
        ],
        "experience_phrases": [
            "Managed database cluster serving 50M+ records",
            "Reduced query execution time by 80% through indexing",
            "Implemented disaster recovery with 99.99% uptime",
            "Migrated legacy Oracle database to PostgreSQL",
        ],
        "education": ["B.Tech in Computer Science", "B.Sc. in Information Technology"],
    },
    "Network Engineer": {
        "skills": [
            "Cisco", "Juniper", "TCP/IP", "BGP", "OSPF", "VPN",
            "Firewalls", "Network Security", "Python", "Bash", "MPLS",
            "SD-WAN", "Load Balancing", "Wireshark", "Network Monitoring"
        ],
        "experience_phrases": [
            "Designed network infrastructure for 5000+ user enterprise",
            "Reduced network downtime by 70% through proactive monitoring",
            "Implemented SD-WAN solution across 50 branch offices",
            "Managed firewall rules for PCI-DSS compliant environment",
        ],
        "education": ["B.Tech in Computer Science", "B.E. in Electronics"],
    },
}


def generate_synthetic_resume(career: str, template: dict) -> str:
    """
    Generate one realistic synthetic resume text for a given career.
    
    Args:
        career: The job title (e.g., "Data Scientist")
        template: Dictionary with skills, experience phrases, and education options
    
    Returns:
        A string containing a realistic-looking resume text
    
    Why synthetic data?
    Real datasets are limited. More training data → better ML model accuracy.
    Synthetic data must look realistic so the model learns the right patterns.
    """
    
    # Randomly pick how many skills to include (between 8 and 14)
    # np.random.choice picks random items from a list
    # replace=False means no duplicates
    num_skills = np.random.randint(8, 15)
    
    # Make sure we don't ask for more skills than exist in the template
    num_skills = min(num_skills, len(template["skills"]))
    
    # Randomly select skills from the template
    selected_skills = np.random.choice(
        template["skills"],
        size=num_skills,
        replace=False   # No duplicate skills
    ).tolist()          # Convert numpy array → regular Python list
    
    # Randomly pick 3 to 5 experience bullet points
    num_exp = np.random.randint(3, 6)
    num_exp = min(num_exp, len(template["experience_phrases"]))
    selected_exp = np.random.choice(
        template["experience_phrases"],
        size=num_exp,
        replace=False
    ).tolist()
    
    # Randomly pick one education entry
    education = np.random.choice(template["education"])
    
    # Generate random years of experience (1 to 12 years)
    years_exp = np.random.randint(1, 13)
    
    # Build the resume as a formatted string
    # This simulates what text extraction gives us from a real PDF resume
    resume_text = f"""
{career}

SUMMARY
Experienced {career} with {years_exp} years of experience.
Passionate about delivering high-quality solutions and continuous learning.

SKILLS
{', '.join(selected_skills)}

EXPERIENCE
"""
    # Add each experience bullet point
    for exp in selected_exp:
        resume_text += f"• {exp}\n"
    
    resume_text += f"""
EDUCATION
{education}
Computer Science Department
Graduated: {np.random.randint(2010, 2023)}

CERTIFICATIONS
{np.random.choice(['AWS Certified', 'Google Cloud Professional', 'Microsoft Azure', 
                    'Coursera ML Certificate', 'Udemy Python Certificate', 'None'])}
"""
    return resume_text.strip()  # .strip() removes leading/trailing whitespace


def generate_full_synthetic_dataset(samples_per_career: int = 40) -> pd.DataFrame:
    """
    Generate a complete synthetic dataset with resumes for all careers.
    
    Args:
        samples_per_career: How many fake resumes to make per job category.
                           Default 40 means 40 × 15 careers = 600 samples.
    
    Returns:
        A pandas DataFrame with columns: 'Resume' and 'Category'
    
    A DataFrame is like an Excel table. Each row = one resume.
    'Resume' column = the resume text
    'Category' column = the job title label
    """
    all_resumes = []    # We'll collect all generated resumes here
    all_labels  = []    # We'll collect all career labels here
    
    logger.info(f"Generating {samples_per_career} synthetic resumes per career...")
    
    # Loop through each career and generate samples
    # tqdm() wraps the loop to show a nice progress bar
    for career, template in tqdm(CAREER_TEMPLATES.items(), desc="Generating data"):
        for _ in range(samples_per_career):  # _ means we don't use the loop variable
            resume_text = generate_synthetic_resume(career, template)
            all_resumes.append(resume_text)  # Add resume text to list
            all_labels.append(career)         # Add career label to list
    
    # Create a DataFrame from the two lists
    # pd.DataFrame() creates a table; the dict keys become column names
    df = pd.DataFrame({
        'Resume':   all_resumes,
        'Category': all_labels
    })
    
    # Shuffle the rows randomly
    # frac=1 means 100% of rows, random_state=42 means reproducible shuffle
    # reset_index(drop=True) resets row numbers to 0,1,2,3...
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    logger.info(f"Generated {len(df)} synthetic resume samples")
    return df


# ════════════════════════════════════════════════════════════════════════════
# SECTION 2 — DATA LOADING
# Load both Kaggle data and our synthetic data, then merge them.
# ════════════════════════════════════════════════════════════════════════════

def load_kaggle_dataset() -> pd.DataFrame:
    """
    Load the Kaggle resume dataset from disk.
    
    Returns:
        DataFrame with 'Resume' and 'Category' columns,
        or empty DataFrame if file not found.
    """
    kaggle_path = os.path.join(RAW_DIR, "UpdatedResumeDataSet.csv")
    
    if not os.path.exists(kaggle_path):
        # File doesn't exist — warn the user but don't crash
        logger.warning(
            "Kaggle dataset not found at data/raw/UpdatedResumeDataSet.csv\n"
            "Download from: https://www.kaggle.com/datasets/gauravduttakiit/resume-dataset\n"
            "Continuing with synthetic data only..."
        )
        # Return an empty DataFrame with the right column names
        return pd.DataFrame(columns=['Resume', 'Category'])
    
    # pd.read_csv() reads a CSV file into a DataFrame
    df = pd.read_csv(kaggle_path)
    
    logger.info(f"Loaded Kaggle dataset: {len(df)} rows, {df['Category'].nunique()} categories")
    logger.info(f"Kaggle categories: {df['Category'].unique().tolist()}")
    
    return df


def load_and_merge_datasets() -> pd.DataFrame:
    """
    Load Kaggle data + generate synthetic data and merge them.
    
    Returns:
        Combined, shuffled DataFrame ready for cleaning.
    
    Why merge?
        - Kaggle data: real resumes (authentic language patterns)
        - Synthetic data: more samples per category (better ML training)
        - Together: best of both worlds
    """
    logger.info("=" * 60)
    logger.info("STEP 1: Loading and merging datasets")
    logger.info("=" * 60)
    
    # Load real Kaggle data
    kaggle_df = load_kaggle_dataset()
    
    # Generate synthetic data (40 samples × 15 careers = 600 synthetic rows)
    synthetic_df = generate_full_synthetic_dataset(samples_per_career=40)
    
    # pd.concat() stacks DataFrames on top of each other (like combining Excel sheets)
    # ignore_index=True resets row numbering in the combined DataFrame
    combined_df = pd.concat([kaggle_df, synthetic_df], ignore_index=True)
    
    # Shuffle the combined dataset so real and synthetic are mixed
    combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    logger.info(f"Total combined dataset: {len(combined_df)} rows")
    logger.info(f"Categories: {combined_df['Category'].nunique()} unique")
    
    return combined_df


# ════════════════════════════════════════════════════════════════════════════
# SECTION 3 — DATA CLEANING
# Raw data is messy. We clean it here before any ML work.
# ════════════════════════════════════════════════════════════════════════════

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the raw dataset by removing nulls, duplicates, and bad rows.
    
    Args:
        df: Raw DataFrame from load step
    
    Returns:
        Cleaned DataFrame
    
    Think of this like washing vegetables before cooking —
    messy data leads to bad models, just like dirty veg ruins food.
    """
    logger.info("=" * 60)
    logger.info("STEP 2: Cleaning dataset")
    logger.info("=" * 60)
    
    initial_count = len(df)
    logger.info(f"Starting rows: {initial_count}")
    
    # ── Remove rows where Resume or Category is missing (null/NaN) ──
    # dropna() removes rows where any of the listed columns has NaN/null
    df = df.dropna(subset=['Resume', 'Category'])
    logger.info(f"After dropping nulls: {len(df)} rows")
    
    # ── Remove duplicate resumes ──
    # drop_duplicates() finds rows where 'Resume' text is exactly the same
    # subset=['Resume'] = only check the Resume column for duplicates
    df = df.drop_duplicates(subset=['Resume'])
    logger.info(f"After dropping duplicates: {len(df)} rows")
    
    # ── Remove rows with very short resumes (less than 50 characters) ──
    # str.len() calculates the length of each string in the Resume column
    # The condition [df['Resume'].str.len() >= 50] keeps only long-enough resumes
    df = df[df['Resume'].str.len() >= 50]
    logger.info(f"After removing short resumes: {len(df)} rows")
    
    # ── Standardize category names ──
    # .str.strip() removes leading/trailing whitespace from every value
    # .str.title() converts "data scientist" → "Data Scientist"
    df['Category'] = df['Category'].str.strip().str.title()
    
    # ── Map Kaggle's category names to our standard names ──
    # The Kaggle dataset uses different names than our system.
    # This dictionary maps Kaggle names → our standard names.
    category_mapping = {
        'Java Developer':          'Software Engineer',
        'Web Designing':           'UI/UX Designer',
        'Hr':                      'Business Analyst',
        'Hadoop':                  'Data Engineer',
        'Blockchain':              'Software Engineer',
        'Etl Developer':           'Data Engineer',
        'Operations Manager':      'Product Manager',
        'Arts':                    'UI/UX Designer',
        'Sales':                   'Business Analyst',
        'Advocate':                'Business Analyst',
        'Automation Testing':      'Software Engineer',
        'Testing':                 'Software Engineer',
        'Mechanical Engineer':     'DevOps Engineer',
        'Electrical Engineering':  'Network Engineer',
        'Civil Engineer':          'DevOps Engineer',
        'Health And Fitness':      'Business Analyst',
        'Agriculture':             'Data Analyst',
        'Bpo':                     'Business Analyst',
        'Dot Net Developer':       'Software Engineer',
        'Android':                 'Frontend Developer',
        'Ios':                     'Frontend Developer',
        'Sap Developer':           'Software Engineer',
        'Python Developer':        'Software Engineer',
        'Pmo':                     'Project Manager',
        'Digital Media':           'UI/UX Designer',
        'Network Security Engineer': 'Cybersecurity Analyst',
        'Data Engineer':           'Data Scientist',
    }
    
    # .map() replaces values using the dictionary
    # fillna(df['Category']) means: if no mapping exists, keep original value
    df['Category'] = df['Category'].map(category_mapping).fillna(df['Category'])
    
    # ── Keep only categories that have at least 10 resumes ──
    # This prevents the ML model from training on categories with too few examples
    category_counts = df['Category'].value_counts()  # Count resumes per category
    
    # Keep categories with 10+ resumes
    valid_categories = category_counts[category_counts >= 10].index
    df = df[df['Category'].isin(valid_categories)]
    logger.info(f"After filtering rare categories: {len(df)} rows")
    
    # ── Reset row index ──
    # After all the drops and filters, row numbers have gaps (0, 3, 7, 11...)
    # reset_index gives clean sequential numbers (0, 1, 2, 3...)
    df = df.reset_index(drop=True)
    
    removed = initial_count - len(df)
    logger.info(f"Removed {removed} rows total ({removed/initial_count*100:.1f}%)")
    logger.info(f"Final categories: {sorted(df['Category'].unique().tolist())}")
    
    return df


# ════════════════════════════════════════════════════════════════════════════
# SECTION 4 — TEXT PREPROCESSING
# Convert raw resume text into clean, machine-readable form.
# ════════════════════════════════════════════════════════════════════════════

def preprocess_text(text: str, nlp_model=None) -> str:
    """
    Clean and preprocess a single resume text string.
    
    Args:
        text: Raw resume text (messy, with URLs, symbols, etc.)
        nlp_model: Optional loaded spaCy model for lemmatization
    
    Returns:
        Cleaned, preprocessed text string
    
    What is preprocessing?
    Computers can't understand "Experienced" and "experienced" as the same word.
    Preprocessing makes everything consistent so ML works better.
    
    Steps:
    1. Lowercase everything
    2. Remove URLs, emails, phone numbers
    3. Remove special characters and numbers
    4. Remove extra whitespace
    5. Lemmatize (experienced → experience, running → run)
    6. Remove stopwords (the, is, at, which — useless words)
    """
    
    # Guard: if text is not a string (e.g., NaN), return empty string
    if not isinstance(text, str):
        return ""
    
    # ── Step 1: Lowercase ──────────────────────────────────────────────────
    # "Python" and "python" should be the same word to our ML model
    text = text.lower()
    
    # ── Step 2: Remove URLs ───────────────────────────────────────────────
    # re.sub() finds all text matching a pattern and replaces it
    # r'http\S+' matches any URL starting with http
    # ' ' replaces it with a space
    text = re.sub(r'http\S+|www\S+', ' ', text)
    
    # ── Step 3: Remove email addresses ────────────────────────────────────
    # r'\S+@\S+' matches patterns like name@email.com
    text = re.sub(r'\S+@\S+', ' ', text)
    
    # ── Step 4: Remove phone numbers ──────────────────────────────────────
    # Matches patterns like +91-9876543210, (123) 456-7890, 9876543210
    text = re.sub(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', ' ', text)
    
    # ── Step 5: Remove special characters (keep only letters and spaces) ──
    # [^a-zA-Z\s] means "anything that is NOT a letter or whitespace"
    # Replace those characters with a space
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # ── Step 6: Remove extra whitespace ───────────────────────────────────
    # \s+ matches one or more whitespace characters (spaces, tabs, newlines)
    # Replace all with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # .strip() removes leading and trailing spaces
    text = text.strip()
    
    # ── Step 7: Lemmatize and remove stopwords (using spaCy) ──────────────
    # Lemmatization: "running" → "run", "experiences" → "experience"
    # Stopwords: "the", "is", "at", "which", "on" — these carry no meaning
    if nlp_model is not None:
        # Process the text with spaCy (this does lemmatization and more)
        doc = nlp_model(text)
        
        # Keep only tokens that:
        # 1. are NOT stopwords (token.is_stop == False)
        # 2. are NOT punctuation (token.is_punct == False)
        # 3. have length > 2 (skip tiny words like "or", "of")
        # token.lemma_ = the base form of the word
        tokens = [
            token.lemma_        # Use lemma (base form)
            for token in doc
            if not token.is_stop     # Skip stopwords
            and not token.is_punct   # Skip punctuation
            and len(token.text) > 2  # Skip very short words
        ]
        
        # Join all tokens back into a single string
        text = ' '.join(tokens)
    
    return text


def preprocess_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply text preprocessing to every resume in the dataset.
    
    Args:
        df: Cleaned DataFrame with 'Resume' column
    
    Returns:
        DataFrame with added 'Cleaned_Resume' column
    """
    logger.info("=" * 60)
    logger.info("STEP 3: Preprocessing text")
    logger.info("=" * 60)
    
    # Load spaCy model (the English NLP brain we downloaded)
    # We load it once and reuse it — loading is slow, using it is fast
    logger.info("Loading spaCy NLP model...")
    try:
        # Load the large English model
        nlp = spacy.load("en_core_web_lg")
        
        # nlp.max_length controls how long a text can be
        # Resumes can be long — increase limit to avoid errors
        nlp.max_length = 2000000
        
        # Disable components we don't need for speed
        # We only need the tokenizer and lemmatizer — not NER or parser
        nlp.disable_pipes(["ner", "parser"])
        logger.info("spaCy model loaded successfully")
        
    except OSError:
        # If the model isn't downloaded yet, fall back to basic preprocessing
        logger.warning("spaCy model not found. Using basic preprocessing.")
        logger.warning("Run: python -m spacy download en_core_web_lg")
        nlp = None
    
    # Apply preprocessing to every row in the Resume column
    # tqdm() shows a progress bar so you can see progress
    logger.info("Preprocessing resumes (this may take 2-5 minutes)...")
    
    cleaned_resumes = []  # Store cleaned versions here
    
    # tqdm wraps the iterable to show progress
    for resume in tqdm(df['Resume'], desc="Preprocessing"):
        cleaned = preprocess_text(resume, nlp)
        cleaned_resumes.append(cleaned)
    
    # Add the cleaned text as a new column
    # We keep the original 'Resume' column too — for display purposes
    df['Cleaned_Resume'] = cleaned_resumes
    
    # Show a sample comparison before/after
    logger.info("\nExample — Before preprocessing:")
    logger.info(df['Resume'].iloc[0][:200])     # First 200 chars of original
    logger.info("\nExample — After preprocessing:")
    logger.info(df['Cleaned_Resume'].iloc[0][:200])  # First 200 chars of cleaned
    
    return df


# ════════════════════════════════════════════════════════════════════════════
# SECTION 5 — FEATURE ENGINEERING
# Extract patterns and numbers that ML can learn from.
# ════════════════════════════════════════════════════════════════════════════

# Load our skills database from the JSON config file
def load_skills_db() -> dict:
    """Load the skills database from config/skills_db.json."""
    skills_path = os.path.join(CONFIG_DIR, "skills_db.json")
    
    if os.path.exists(skills_path):
        with open(skills_path, 'r') as f:
            return json.load(f)
    else:
        logger.warning("skills_db.json not found in config/")
        return {"technical_skills": {}, "soft_skills": []}


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer new features from resume text.
    
    Args:
        df: DataFrame with 'Resume' and 'Cleaned_Resume' columns
    
    Returns:
        DataFrame with many new feature columns added
    
    Feature engineering = creating new columns that capture useful patterns.
    Instead of just giving the ML model raw text, we give it:
    - How many skills are mentioned?
    - How many years of experience?
    - Are Python/ML/SQL mentioned? (binary yes/no flags)
    - How long is the resume?
    - Does it mention education?
    
    These handcrafted features help the ML model make better predictions.
    """
    logger.info("=" * 60)
    logger.info("STEP 4: Feature engineering")
    logger.info("=" * 60)
    
    # Load the skills database
    skills_db = load_skills_db()
    
    # Create a flat list of ALL technical skills
    all_tech_skills = []
    for category_skills in skills_db.get("technical_skills", {}).values():
        all_tech_skills.extend(category_skills)  # Add all skills to the list
    
    all_tech_skills = [s.lower() for s in all_tech_skills]  # Lowercase all
    soft_skills = [s.lower() for s in skills_db.get("soft_skills", [])]
    
    # ── Feature 1: Resume word count ──────────────────────────────────────
    # .str.split() splits text by spaces → gives a list of words
    # .str.len() counts the words
    df['word_count'] = df['Resume'].str.split().str.len()
    
    # ── Feature 2: Character count ────────────────────────────────────────
    df['char_count'] = df['Resume'].str.len()
    
    # ── Feature 3: Years of experience mentioned ──────────────────────────
    # Use regex to find patterns like "5 years", "3+ years", "two years"
    # This captures numeric years mentioned in the resume text
    def extract_years_experience(text: str) -> int:
        """Find the maximum years of experience mentioned in resume text."""
        if not isinstance(text, str):
            return 0
        
        # Pattern: finds "5 years", "3+ years", "2-3 years", "10 years experience"
        # r'(\d+)\+?\s*(?:to\s*\d+\s*)?years?' matches:
        #   (\d+) — one or more digits
        #   \+?   — optional plus sign
        #   \s*   — optional space
        #   years? — "year" or "years"
        pattern = r'(\d+)\+?\s*(?:to\s*\d+\s*)?years?'
        matches = re.findall(pattern, text.lower())
        
        if matches:
            # Convert all found numbers to integers, return the largest
            years = [int(m) for m in matches if int(m) <= 30]  # Cap at 30 years
            return max(years) if years else 0
        return 0
    
    df['years_experience'] = df['Resume'].apply(extract_years_experience)
    
    # ── Feature 4: Technical skill count ─────────────────────────────────
    # Count how many technical skills from our database appear in the resume
    def count_technical_skills(text: str) -> int:
        """Count how many technical skills appear in the resume text."""
        if not isinstance(text, str):
            return 0
        text_lower = text.lower()
        # Count skills that appear in the resume text
        count = sum(1 for skill in all_tech_skills if skill in text_lower)
        return count
    
    df['technical_skill_count'] = df['Resume'].apply(count_technical_skills)
    
    # ── Feature 5: Soft skill count ───────────────────────────────────────
    def count_soft_skills(text: str) -> int:
        """Count how many soft skills appear in the resume text."""
        if not isinstance(text, str):
            return 0
        text_lower = text.lower()
        return sum(1 for skill in soft_skills if skill in text_lower)
    
    df['soft_skill_count'] = df['Resume'].apply(count_soft_skills)
    
    # ── Feature 6: Binary skill flags ────────────────────────────────────
    # These are 0 or 1 columns: "Does this resume mention Python? (1=yes, 0=no)"
    # These are very powerful for distinguishing career types
    important_skills = [
        'python', 'java', 'javascript', 'sql', 'machine learning',
        'deep learning', 'tensorflow', 'pytorch', 'react', 'nodejs',
        'docker', 'kubernetes', 'aws', 'azure', 'linux', 'git',
        'tableau', 'power bi', 'excel', 'agile', 'scrum', 'figma',
        'nlp', 'computer vision', 'spark', 'hadoop', 'mongodb'
    ]
    
    for skill in important_skills:
        # Create a column name like 'has_python', 'has_sql', 'has_docker'
        col_name = f"has_{skill.replace(' ', '_').replace('/', '_')}"
        
        # .str.contains() returns True/False if the word is in the text
        # case=False means ignore uppercase/lowercase
        # .astype(int) converts True→1, False→0
        df[col_name] = df['Resume'].str.contains(
            skill, case=False, regex=False, na=False
        ).astype(int)
    
    # ── Feature 7: Has education section ──────────────────────────────────
    # Does the resume mention education? (1=yes, 0=no)
    education_keywords = ['b.tech', 'btech', 'b.e', 'mba', 'm.tech', 'mtech',
                         'bachelor', 'master', 'phd', 'degree', 'university',
                         'college', 'b.sc', 'bsc', 'm.sc', 'diploma']
    
    df['has_education'] = df['Resume'].apply(
        lambda text: 1 if any(kw in text.lower() for kw in education_keywords) else 0
    )
    
    # ── Feature 8: Has certifications ────────────────────────────────────
    cert_keywords = ['certified', 'certification', 'certificate', 'aws certified',
                    'google certified', 'microsoft certified', 'cissp', 'pmp']
    
    df['has_certification'] = df['Resume'].apply(
        lambda text: 1 if any(kw in text.lower() for kw in cert_keywords) else 0
    )
    
    # ── Feature 9: Has GitHub/LinkedIn/portfolio link ─────────────────────
    df['has_links'] = df['Resume'].apply(
        lambda text: 1 if any(kw in text.lower() 
                              for kw in ['github', 'linkedin', 'portfolio', 'kaggle']) 
                    else 0
    )
    
    # ── Feature 10: Encode the Category label as a number ─────────────────
    # ML models need numbers, not text labels.
    # LabelEncoder converts: "Data Scientist"→0, "Software Engineer"→1, etc.
    label_encoder = LabelEncoder()
    df['Category_Encoded'] = label_encoder.fit_transform(df['Category'])
    
    # Print feature summary
    logger.info(f"Engineered {df.shape[1]} total columns")
    logger.info(f"Sample feature values for row 0:")
    feature_cols = ['word_count', 'years_experience', 'technical_skill_count',
                    'soft_skill_count', 'has_python', 'has_education']
    for col in feature_cols:
        if col in df.columns:
            logger.info(f"  {col}: {df[col].iloc[0]}")
    
    return df, label_encoder


# ════════════════════════════════════════════════════════════════════════════
# SECTION 6 — TF-IDF VECTORIZATION
# Convert cleaned resume text into numbers that ML can actually use.
# ════════════════════════════════════════════════════════════════════════════

def create_tfidf_features(df: pd.DataFrame):
    """
    Convert resume text into a TF-IDF feature matrix.
    
    What is TF-IDF? (Explained simply)
    
    Imagine you have 1000 resumes. The word "python" appears in 600 of them.
    The word "tensorflow" appears in only 50 of them.
    
    TF-IDF says: "tensorflow" is MORE UNIQUE and IMPORTANT than "python"
    because it appears in fewer documents. Words that appear everywhere
    are less useful for distinguishing careers.
    
    TF  = Term Frequency: how often a word appears in THIS resume
    IDF = Inverse Document Frequency: how rare is this word across ALL resumes
    TF-IDF = TF × IDF (high score = word is frequent here AND rare overall)
    
    Output: A matrix where:
    - Each ROW = one resume
    - Each COLUMN = one word
    - Each VALUE = TF-IDF score for that word in that resume
    
    Args:
        df: DataFrame with 'Cleaned_Resume' column
    
    Returns:
        tfidf_matrix: Numeric matrix (numpy array)
        vectorizer: Fitted TfidfVectorizer (saved for use with new resumes)
    """
    logger.info("=" * 60)
    logger.info("STEP 5: Creating TF-IDF features")
    logger.info("=" * 60)
    
    # Create and configure the TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=5000,    # Keep only the top 5000 most important words
                              # Too many features → slow training and overfitting
        
        ngram_range=(1, 2),   # Use both single words AND 2-word phrases
                              # (1,2) means: "python", "machine learning", "deep learning"
                              # bigrams (2-word phrases) capture important tech terms
        
        min_df=2,             # Ignore words that appear in fewer than 2 documents
                              # Very rare words are usually typos or noise
        
        max_df=0.95,          # Ignore words that appear in more than 95% of documents
                              # Words in almost every resume aren't useful for distinction
        
        sublinear_tf=True,    # Apply log scaling to term frequency
                              # Prevents very frequent words from dominating
    )
    
    # .fit_transform() does two things at once:
    # 1. fit: learn the vocabulary from all resumes
    # 2. transform: convert all resumes to TF-IDF numbers
    tfidf_matrix = vectorizer.fit_transform(df['Cleaned_Resume'])
    
    logger.info(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
    logger.info(f"  ({tfidf_matrix.shape[0]} resumes × {tfidf_matrix.shape[1]} words)")
    logger.info(f"Top 20 important words: {vectorizer.get_feature_names_out()[:20].tolist()}")
    
    return tfidf_matrix, vectorizer


# ════════════════════════════════════════════════════════════════════════════
# SECTION 7 — SAVE EVERYTHING
# ════════════════════════════════════════════════════════════════════════════

def save_processed_data(df: pd.DataFrame, tfidf_matrix, vectorizer, label_encoder):
    """
    Save all processed data and fitted objects to disk.
    
    Why save?
    - Training takes time. We don't want to redo it every time we run the app.
    - joblib saves Python objects efficiently to .pkl files.
    - .pkl files can be loaded instantly in the app.
    
    Args:
        df: Processed DataFrame
        tfidf_matrix: TF-IDF numeric matrix (scipy sparse matrix)
        vectorizer: Fitted TfidfVectorizer (knows the vocabulary)
        label_encoder: Fitted LabelEncoder (maps categories to numbers)
    """
    logger.info("=" * 60)
    logger.info("STEP 6: Saving processed data")
    logger.info("=" * 60)
    
    # ── Save the clean DataFrame as CSV ───────────────────────────────────
    # CSV = Comma Separated Values, easily opened in Excel
    clean_csv_path = os.path.join(PROCESSED_DIR, "clean_resumes.csv")
    df.to_csv(clean_csv_path, index=False)
    logger.info(f"Saved clean DataFrame: {clean_csv_path}")
    
    # ── Save the TF-IDF matrix as a .pkl file ─────────────────────────────
    # joblib.dump() serializes Python objects to binary files
    # It's like "pickling" the object — saving its state
    tfidf_path = os.path.join(PROCESSED_DIR, "tfidf_matrix.pkl")
    joblib.dump(tfidf_matrix, tfidf_path)
    logger.info(f"Saved TF-IDF matrix: {tfidf_path}")
    
    # ── Save the fitted TF-IDF vectorizer ─────────────────────────────────
    # We need to save the vectorizer because it knows the vocabulary.
    # When a new resume comes in, we use THIS vectorizer to transform it.
    vectorizer_path = os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl")
    joblib.dump(vectorizer, vectorizer_path)
    logger.info(f"Saved TF-IDF vectorizer: {vectorizer_path}")
    
    # ── Save the Label Encoder ────────────────────────────────────────────
    # We need this to convert numbers back to career names after prediction
    # e.g., 0 → "Data Scientist", 1 → "Software Engineer"
    encoder_path = os.path.join(MODELS_DIR, "label_encoder.pkl")
    joblib.dump(label_encoder, encoder_path)
    logger.info(f"Saved label encoder: {encoder_path}")
    
    # ── Save train/test split ─────────────────────────────────────────────
    # Split data into training set (80%) and test set (20%)
    # Training set: used to train the ML model
    # Test set: used to evaluate how good the model is on UNSEEN data
    from scipy.sparse import hstack
    import scipy.sparse as sp
    
    # Get the engineered feature columns (not text columns)
    feature_cols = [col for col in df.columns 
                   if col not in ['Resume', 'Cleaned_Resume', 'Category', 'Category_Encoded']
                   and df[col].dtype in ['int64', 'float64', 'int32']]
    
    # Convert DataFrame columns to a sparse matrix so we can combine with TF-IDF
    eng_features = sp.csr_matrix(df[feature_cols].values)
    
    # Combine TF-IDF features + engineered features into one big matrix
    # hstack = horizontal stack (put side by side)
    X = hstack([tfidf_matrix, eng_features])
    y = df['Category_Encoded'].values  # Labels (what we're predicting)
    
    # train_test_split() randomly splits data
    # test_size=0.2 means 20% goes to test set
    # stratify=y means keep the same class distribution in both sets
    # random_state=42 makes the split reproducible
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )
    
    # Save all four splits
    joblib.dump(X_train, os.path.join(PROCESSED_DIR, "X_train.pkl"))
    joblib.dump(X_test,  os.path.join(PROCESSED_DIR, "X_test.pkl"))
    joblib.dump(y_train, os.path.join(PROCESSED_DIR, "y_train.pkl"))
    joblib.dump(y_test,  os.path.join(PROCESSED_DIR, "y_test.pkl"))
    
    logger.info(f"Train set: {X_train.shape[0]} samples")
    logger.info(f"Test set:  {X_test.shape[0]} samples")
    
    # ── Save feature column names ─────────────────────────────────────────
    # We need to know which features were used so the app can use them too
    feature_info = {
        'engineered_features': feature_cols,
        'tfidf_features':      int(tfidf_matrix.shape[1]),
        'total_features':      int(X.shape[1]),
        'categories':          label_encoder.classes_.tolist(),
        'total_samples':       int(len(df)),
    }
    
    feature_info_path = os.path.join(PROCESSED_DIR, "feature_info.json")
    with open(feature_info_path, 'w') as f:
        json.dump(feature_info, f, indent=2)
    logger.info(f"Saved feature info: {feature_info_path}")
    
    return X_train, X_test, y_train, y_test


# ════════════════════════════════════════════════════════════════════════════
# SECTION 8 — DATASET STATISTICS REPORT
# Understand your data before training. Always explore first!
# ════════════════════════════════════════════════════════════════════════════

def print_dataset_report(df: pd.DataFrame):
    """
    Print a detailed report about the dataset so you understand what we have.
    
    Good data scientists always explore their data before building models.
    This is called EDA — Exploratory Data Analysis.
    """
    logger.info("\n" + "=" * 60)
    logger.info("DATASET REPORT — Exploratory Data Analysis")
    logger.info("=" * 60)
    
    # Basic stats
    logger.info(f"\nTotal resumes:       {len(df):,}")
    logger.info(f"Total categories:    {df['Category'].nunique()}")
    logger.info(f"Total features:      {df.shape[1]} columns")
    
    # Category distribution (sorted by count, descending)
    logger.info("\nCategory distribution:")
    logger.info("-" * 40)
    counts = df['Category'].value_counts()
    for category, count in counts.items():
        # Build a simple bar chart using '*' characters
        bar = '█' * (count // 10)  # One block per 10 resumes
        logger.info(f"  {category:<30} {count:>4} {bar}")
    
    # Text statistics
    if 'word_count' in df.columns:
        logger.info(f"\nResume word count statistics:")
        logger.info(f"  Average: {df['word_count'].mean():.0f} words")
        logger.info(f"  Minimum: {df['word_count'].min()} words")
        logger.info(f"  Maximum: {df['word_count'].max()} words")
    
    # Skill statistics
    if 'technical_skill_count' in df.columns:
        logger.info(f"\nTechnical skills per resume:")
        logger.info(f"  Average: {df['technical_skill_count'].mean():.1f} skills")
        logger.info(f"  Maximum: {df['technical_skill_count'].max()} skills")
    
    # Most common skill flags
    skill_cols = [col for col in df.columns if col.startswith('has_') 
                  and col not in ['has_education', 'has_certification', 'has_links']]
    if skill_cols:
        logger.info("\nMost common skills in dataset:")
        skill_rates = {col: df[col].mean() * 100 for col in skill_cols}
        top_skills = sorted(skill_rates.items(), key=lambda x: x[1], reverse=True)[:10]
        for skill_col, rate in top_skills:
            skill_name = skill_col.replace('has_', '').replace('_', ' ')
            logger.info(f"  {skill_name:<20} {rate:.1f}% of resumes")


# ════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION — Run this file directly to process all data
# ════════════════════════════════════════════════════════════════════════════

def run_full_pipeline():
    """
    Run the complete data pipeline from raw data to ML-ready features.
    
    This is the MAIN function. Running this file will:
    1. Load/generate data
    2. Clean it
    3. Preprocess text
    4. Engineer features
    5. Create TF-IDF matrix
    6. Save everything to disk
    """
    logger.info("PHASE 3 — DATA PIPELINE STARTING")
    logger.info("=" * 60)
    
    # Step 1: Load data
    df = load_and_merge_datasets()
    
    # Step 2: Clean data
    df = clean_dataset(df)
    
    # Step 3: Preprocess text
    df = preprocess_dataset(df)
    
    # Step 4: Engineer features
    df, label_encoder = extract_features(df)
    
    # Step 5: Create TF-IDF
    tfidf_matrix, vectorizer = create_tfidf_features(df)
    
    # Step 6: Print report
    print_dataset_report(df)
    
    # Step 7: Save everything
    X_train, X_test, y_train, y_test = save_processed_data(
        df, tfidf_matrix, vectorizer, label_encoder
    )
    
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 3 COMPLETE!")
    logger.info("Files saved to data/processed/ and models/")
    logger.info("Ready for Phase 4 — NLP Implementation")
    logger.info("=" * 60)
    
    return df, tfidf_matrix, vectorizer, label_encoder


# This block runs ONLY when you execute this file directly:
# python src/data_pipeline.py
# It does NOT run when another file imports this module.
if __name__ == "__main__":
    run_full_pipeline()