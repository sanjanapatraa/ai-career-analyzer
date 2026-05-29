import streamlit as st

from ui.components import H


PAGES = [
    ("dashboard", "Dashboard"),
    ("analyzer", "Resume Analyzer"),
    ("career", "Career Match"),
    ("jobmatch", "Job Match"),
    ("chatbot", "AI Career Coach"),
    ("interview", "Interview Prep"),
    ("roadmap", "Learning Roadmap"),
    ("recruiter", "Recruiter Analytics"),
]

PAGE_META = {
    "dashboard": ("Dashboard", "Pipeline health, ATS scores, and resume intelligence"),
    "analyzer": ("Resume Analyzer", "Upload, parse, score, and benchmark a resume"),
    "career": ("Career Match", "Role recommendations and skill path planning"),
    "jobmatch": ("Job Match", "Compare a candidate profile against a target role"),
    "chatbot": ("AI Career Coach", "Context-aware coaching from the latest analysis"),
    "interview": ("Interview Prep", "Generate focused interview preparation plans"),
    "roadmap": ("Learning Roadmap", "Prioritized growth plan from missing skills"),
    "recruiter": ("Recruiter Analytics", "Hiring dashboard for shortlist decisions"),
}


def navigate(page_name: str) -> None:
    st.session_state.page = page_name
    st.rerun()


def sidebar(active_page: str) -> None:
    with st.sidebar:
        H(
            """
            <nav class="sb">
                <div class="sb-logo">
                    <div class="sb-mark">RI</div>
                    <div>ResumeIQ</div>
                </div>
                <div class="sb-section">ATS Suite</div>
            """
        )

        for page_key, label in PAGES:
            button_type = "primary" if page_key == active_page else "secondary"
            if st.button(label, key=f"nav_{page_key}", use_container_width=True, type=button_type):
                navigate(page_key)

        H(
            """
                <div class="sb-foot">
                    <strong>Production Workspace</strong>
                    Resume intelligence, candidate scoring, job matching, and recruiter analytics in one focused dashboard.
                </div>
            </nav>
            """
        )


def topbar(page: str) -> None:
    title, subtitle = PAGE_META.get(page, ("ResumeIQ", "AI ATS career platform"))
    H(
        f"""
        <header class="topbar">
            <div>
                <div class="topbar-title">{title}</div>
                <div class="topbar-subtitle">{subtitle}</div>
            </div>
            <div class="topbar-actions">
                <span class="topbar-badge">ATS Ready</span>
            </div>
        </header>
        """
    )
