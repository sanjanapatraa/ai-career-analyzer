import os
import sys

import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

st.set_page_config(
    page_title="ResumeIQ - AI ATS Career Platform",
    page_icon="RI",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULTS = {
    "page": "landing",
    "analysis_result": None,
    "chat_history": [],
    "jd_text": "",
    "target_level": "mid",
    "education_req": "bachelor",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

from ui.styles import inject_css

inject_css()

page = st.session_state.page

if page == "landing":
    from ui.landing import show_landing

    show_landing()
else:
    from ui.nav import sidebar, topbar

    sidebar(page)
    topbar(page)

    routes = {
        "dashboard": ("ui.dashboard", "show_dashboard"),
        "analyzer": ("ui.analyzer", "show_analyzer"),
        "career": ("ui.career", "show_career"),
        "jobmatch": ("ui.jobmatch", "show_jobmatch"),
        "chatbot": ("ui.chatbot", "show_chatbot"),
        "interview": ("ui.interview", "show_interview"),
        "roadmap": ("ui.roadmap", "show_roadmap"),
        "recruiter": ("ui.recruiter", "show_recruiter"),
    }

    module_name, function_name = routes.get(page, routes["dashboard"])
    module = __import__(module_name, fromlist=[function_name])
    getattr(module, function_name)()
