# app.py
# ══════════════════════════════════════════════════════════════════════════
# ResumeIQ — Premium ATS Resume Analyzer
# Main Streamlit entry point — redesigned as a production SaaS platform
# Run: streamlit run app.py
# ══════════════════════════════════════════════════════════════════════════

import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# ── Page config — MUST be first Streamlit call ─────────────────────────────
st.set_page_config(
    page_title   = "ResumeIQ — AI-Powered ATS Analyzer",
    page_icon    = "🎯",
    layout       = "wide",
    initial_sidebar_state = "expanded",
)

# ── Inject all custom CSS ──────────────────────────────────────────────────
from ui.styles import inject_styles
inject_styles()

# ── Route to the correct page ──────────────────────────────────────────────
# We use session_state to track which "page" the user is on.
# Streamlit re-runs the whole script on every interaction, so
# session_state is how we remember things between runs.
if "page" not in st.session_state:
    st.session_state.page = "landing"

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ── Import page modules ────────────────────────────────────────────────────
from ui.landing   import show_landing
from ui.analyzer  import show_analyzer
from ui.dashboard import show_dashboard

# ── Render the correct page ────────────────────────────────────────────────
if st.session_state.page == "landing":
    show_landing()
elif st.session_state.page == "analyzer":
    show_analyzer()
elif st.session_state.page == "dashboard":
    show_dashboard()