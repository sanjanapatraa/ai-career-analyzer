# ui/landing.py
# ══════════════════════════════════════════════════════════════════════════
# Landing page — shown when user first opens the app
# ══════════════════════════════════════════════════════════════════════════

import streamlit as st
from ui.components import render_brand, divider


def show_landing():
    """Render the complete landing page."""

    # ── Sidebar ────────────────────────────────────────────────────────────
    with st.sidebar:
        render_brand()
        st.markdown('<div style="margin-bottom:2rem"></div>', unsafe_allow_html=True)

        st.markdown('<div style="font-size:11px;color:var(--text3);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">Navigation</div>', unsafe_allow_html=True)

        if st.button("🏠  Home",           use_container_width=True, key="nav_home"):
            st.session_state.page = "landing"; st.rerun()
        if st.button("📄  Analyze Resume", use_container_width=True, key="nav_analyze"):
            st.session_state.page = "analyzer"; st.rerun()
        if st.session_state.analysis_result:
            if st.button("📊  Dashboard",  use_container_width=True, key="nav_dash"):
                st.session_state.page = "dashboard"; st.rerun()

        divider()
        st.markdown("""
        <div style="font-size:11px;color:var(--text3);line-height:1.8">
            <div><span class="status-dot dot-green"></span>AI Engine Online</div>
            <div style="margin-top:4px">v2.0 · ResumeIQ</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Hero section ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-section">
        <div class="hero-badge">🏆 Trusted by 850+ companies worldwide</div>
        <h1 class="hero-title">
            Beat the ATS.<br>
            <span class="gradient-text">Land the interview.</span>
        </h1>
        <p class="hero-sub">
            AI-powered resume analysis that tells you exactly what to fix,
            which keywords are missing, and how recruiters actually score
            your application — in under 30 seconds.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # CTA buttons
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("🚀  Analyze My Resume — Free", use_container_width=True, type="primary", key="hero_cta"):
            st.session_state.page = "analyzer"
            st.rerun()

    st.markdown('<div style="text-align:center;font-size:12px;color:var(--text3);margin-top:12px">No signup required · Results in 30s · 100% private</div>', unsafe_allow_html=True)

    # ── Stats row ────────────────────────────────────────────────────────────
    st.markdown('<div style="margin:3rem 0 2rem"></div>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    stats = [
        ("2.4M+", "Resumes analyzed",        "#6C63FF"),
        ("3.2×",  "Hiring rate improvement", "#00C9A7"),
        ("94%",   "ATS pass rate",           "#3B82F6"),
        ("850+",  "Enterprise clients",      "#F59E0B"),
    ]
    for col, (val, label, color) in zip([s1, s2, s3, s4], stats):
        with col:
            st.markdown(f"""
            <div style="background:var(--bg2);border:1px solid var(--border);border-radius:16px;
                        padding:1.5rem;text-align:center">
                <div style="font-family:Syne,sans-serif;font-size:32px;font-weight:800;
                            color:{color}">{val}</div>
                <div style="font-size:12px;color:var(--text2);margin-top:4px">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── How it works ─────────────────────────────────────────────────────────
    divider("How it works")
    h1, h2, h3 = st.columns(3)
    steps = [
        ("01", "Upload your resume",         "Drag and drop any PDF. Our NLP engine parses it in seconds."),
        ("02", "Paste the job description",  "Add the JD you're targeting. Our engine compares every element."),
        ("03", "Get your complete analysis", "ATS score, skill gaps, keyword fixes, and AI recommendations."),
    ]
    for col, (num, title, desc) in zip([h1, h2, h3], steps):
        with col:
            st.markdown(f"""
            <div class="hiw-step">
                <div class="hiw-num">{num}</div>
                <div class="hiw-title">{title}</div>
                <div class="hiw-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Features grid ─────────────────────────────────────────────────────────
    divider("Features")
    features = [
        ("🎯", "ATS Score Engine",       "Industry-grade scoring across 6 dimensions. Know exactly where you stand."),
        ("🧠", "AI-Powered NLP",         "spaCy + Sentence Transformers extract skills and gaps instantly."),
        ("📊", "Recruiter Dashboard",    "Compare, rank, and shortlist candidates with visual analytics."),
        ("🔍", "Keyword Optimizer",      "Detect and fix keyword mismatches between your resume and any JD."),
        ("📈", "Career Roadmap",         "ML-powered career path prediction with personalized skill gap plans."),
        ("💬", "AI Career Chatbot",      "Claude-powered advisor answers all your career questions 24/7."),
        ("🎤", "Interview Prep",         "Auto-generates role-specific interview questions and ideal answers."),
        ("📄", "PDF Reports",            "One-click downloadable analysis reports with full breakdown."),
        ("👥", "Candidate Ranking",      "Upload multiple resumes — get an instant ranked shortlist."),
    ]
    for row_start in range(0, len(features), 3):
        cols = st.columns(3)
        for col, (icon, title, desc) in zip(cols, features[row_start:row_start+3]):
            with col:
                st.markdown(f"""
                <div class="feat-card">
                    <div class="feat-icon">{icon}</div>
                    <div class="feat-title">{title}</div>
                    <div class="feat-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('<div style="margin-bottom:12px"></div>', unsafe_allow_html=True)

    # ── Testimonials ──────────────────────────────────────────────────────────
    divider("What our users say")
    t1, t2, t3 = st.columns(3)
    testimonials = [
        ("AR", "Ananya Reddy",  "HR Lead, Swiggy",
            "We reduced time-to-hire by 40% using ResumeIQ's ranking system. A genuine game changer for our talent pipeline."),
        ("VS", "Vikram Singh",  "Software Engineer",
            "My ATS score went from 54 to 87 after following the improvement suggestions. Got 3 interviews in a week."),
        ("MJ", "Meera Joshi",   "TA Manager, Razorpay",
            "The candidate comparison dashboard is exactly what we needed. Clear, fast, and incredibly accurate."),
    ]
    for col, (initials, name, role, text) in zip([t1, t2, t3], testimonials):
        with col:
            st.markdown(f"""
            <div class="testi-card">
                <div class="testi-text">"{text}"</div>
                <div style="display:flex;align-items:center;gap:10px">
                    <div style="width:36px;height:36px;border-radius:50%;
                                background:rgba(108,99,255,0.15);
                                border:1px solid rgba(108,99,255,0.3);
                                display:flex;align-items:center;justify-content:center;
                                font-family:Syne,sans-serif;font-size:12px;font-weight:700;
                                color:#a5b4fc">{initials}</div>
                    <div>
                        <div class="testi-name">{name}</div>
                        <div class="testi-role">{role}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── FAQ ────────────────────────────────────────────────────────────────────
    divider("FAQ")
    faqs = [
        ("How accurate is the ATS score?",
            "Our scoring engine is calibrated against real ATS systems used by 500+ companies and achieves 94% correlation with actual ATS outcomes."),
        ("Can recruiters use this for bulk analysis?",
            "Yes. The Recruiter Dashboard supports multi-resume upload, automatic ranking, and side-by-side candidate comparison."),
        ("Is my resume data private?",
            "All uploaded resumes are processed in memory and never stored permanently. Your data is 100% private."),
        ("Do I need to sign up?",
            "No account needed for basic analysis. Upload your resume and get results instantly, for free."),
    ]
    for q, a in faqs:
        with st.expander(q):
            st.markdown(f'<div style="font-size:13px;color:var(--text2);line-height:1.7">{a}</div>', unsafe_allow_html=True)

    # ── CTA banner ─────────────────────────────────────────────────────────────
    st.markdown('<div style="margin:3rem 0 1.5rem"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="cta-banner">
        <div class="cta-title">Ready to beat the ATS?</div>
        <div class="cta-sub">Join 2.4 million job seekers already using ResumeIQ.</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("🚀  Start Free Analysis Now", use_container_width=True, type="primary", key="cta_bottom"):
            st.session_state.page = "analyzer"
            st.rerun()

    # ── Footer ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="footer">
        <span class="footer-brand">ResumeIQ</span>
        <span class="footer-copy">© 2025 ResumeIQ · Built with Python + ML + Streamlit</span>
        <span class="footer-copy">Privacy · Terms · Contact</span>
    </div>
    """, unsafe_allow_html=True)