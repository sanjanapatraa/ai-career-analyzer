import streamlit as st

from ui.components import H, metric_card


def _go(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def show_landing():
    H(
        """
        <div class="landing">
            <header class="landing-nav">
                <div class="brand"><span class="brand-mark">RI</span>ResumeIQ</div>
                <div class="topbar-badge">AI ATS Platform</div>
            </header>
            <section class="hero">
                <div>
                    <p class="eyebrow">Recruiter-grade resume intelligence</p>
                    <h1>AI ATS and career platform for sharper hiring decisions.</h1>
                    <p>
                        Analyze resumes, compare candidate fit, surface skill gaps, and turn raw career data into
                        a focused recruiter dashboard without changing the existing backend engine.
                    </p>
                    <div class="hero-actions">
        """
    )

    c1, c2, c3 = st.columns([.22, .22, .56])
    with c1:
        if st.button("Analyze Resume", type="primary", use_container_width=True):
            _go("analyzer")
    with c2:
        if st.button("Open Dashboard", use_container_width=True):
            _go("dashboard")

    H(
        """
                    </div>
                </div>
                <aside class="hero-board">
                    <div class="board-head">
                        <span>Candidate Pipeline</span>
                        <span>Live scoring</span>
                    </div>
                    <div class="pipeline">
                        <div class="candidate"><div><strong>Priya Patel</strong><br><span>ML Engineer candidate</span></div><b class="score-pill">92%</b></div>
                        <div class="candidate"><div><strong>John Smith</strong><br><span>Data Scientist candidate</span></div><b class="score-pill">87%</b></div>
                        <div class="candidate"><div><strong>Rahul Kumar</strong><br><span>Software Engineer candidate</span></div><b class="score-pill">78%</b></div>
                    </div>
                </aside>
            </section>
            <section class="stats-band">
        """
    )

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        metric_card("Resume parsing", "PDF", "PyMuPDF and pdfplumber extraction", "blue")
    with s2:
        metric_card("ATS scoring", "6", "Weighted recruiter signals", "green")
    with s3:
        metric_card("Job match", "TF-IDF", "Skill and keyword similarity", "indigo")
    with s4:
        metric_card("Reports", "PDF", "Downloadable candidate analysis", "amber")

    H("</section></div>")
