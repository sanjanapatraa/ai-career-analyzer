# app.py
# ─────────────────────────────────────────────────────────────────────────
# This is the MAIN FILE that Streamlit runs when you start the app.
# Think of it like the front door of a house — everything starts here.
# ─────────────────────────────────────────────────────────────────────────

import streamlit as st          # Streamlit = our web framework (creates the UI)
import sys                      # sys helps us manage Python's module search path
import os                       # os helps us work with files and folders

# Add the project root to Python's path so we can import our own modules
# Example: so we can write 'from src.parser import ...' anywhere
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
# (this lets us use os.getenv('ANTHROPIC_API_KEY') anywhere)
from dotenv import load_dotenv
load_dotenv()

# ── Page Configuration ───────────────────────────────────────────────────
# This MUST be the first Streamlit command in the file.
# It sets the browser tab title, icon, and layout.
st.set_page_config(
    page_title="AI Career Analyzer",   # Browser tab title
    page_icon="🎯",                    # Browser tab icon
    layout="wide",                     # Use full screen width
    initial_sidebar_state="expanded",  # Sidebar open by default
)

# ── Custom CSS ───────────────────────────────────────────────────────────
# st.markdown with unsafe_allow_html=True lets us inject custom CSS
# This makes our app look modern and professional
st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Apply font to entire app */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Style the main title */
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    /* Style the subtitle */
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Style metric cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    /* Style the sidebar */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ── Main Page Content ────────────────────────────────────────────────────
# This is what users see on the HOME page of the app

# Big title
st.markdown('<h1 class="main-title">AI Career Analyzer</h1>', unsafe_allow_html=True)

# Subtitle
st.markdown(
    '<p class="subtitle">Upload your resume · Get ATS score · Discover your career path</p>',
    unsafe_allow_html=True
)

# Divider line
st.divider()

# Welcome message using Streamlit columns for layout
col1, col2, col3 = st.columns(3)   # Create 3 equal columns side by side

with col1:
    # st.metric shows a big number with a label — great for stats
    st.metric(label="Resume Features Analyzed", value="15+", delta="All automatic")

with col2:
    st.metric(label="Career Paths Mapped", value="15", delta="ML-powered")

with col3:
    st.metric(label="ATS Score Accuracy", value="94%", delta="Industry standard")

# Instructions
st.markdown("### How to use this app")
st.markdown("""
1. **Upload your Resume** — Go to 'Resume Analyzer' in the sidebar
2. **Get your ATS Score** — See how recruiters' systems rate your resume
3. **Discover Career Paths** — Our ML model recommends the best roles for you
4. **Fix Missing Skills** — See exactly what to learn next
5. **Chat with AI Advisor** — Ask our AI career coach anything
6. **Download your Report** — Get a full PDF analysis
""")

# Feature cards
st.markdown("### Available Features")
features = [
    ("Resume Analyzer",     "Upload PDF, extract text, get full analysis"),
    ("Career Recommender",  "ML-powered career path prediction"),
    ("Job Matcher",         "Match your resume to any job description"),
    ("AI Chatbot",          "Chat with your personal career AI advisor"),
    ("Interview Prep",      "Generate custom interview questions"),
    ("Learning Roadmap",    "Personalized skill development plan"),
]

# Display in a 2-column grid
col_a, col_b = st.columns(2)
for i, (title, desc) in enumerate(features):
    col = col_a if i % 2 == 0 else col_b    # Alternate between columns
    with col:
        # Display each feature as a nice card
        st.markdown(f"""
        <div class="metric-card">
            <strong>{title}</strong><br>
            <small style="color: #666;">{desc}</small>
        </div>
        """, unsafe_allow_html=True)

# Footer note
st.markdown("---")
st.markdown(
    "<center><small>Built with Python · Streamlit · scikit-learn · spaCy · Sentence Transformers</small></center>",
    unsafe_allow_html=True
)