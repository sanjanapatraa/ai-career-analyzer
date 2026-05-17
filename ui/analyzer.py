# ui/analyzer.py
# ══════════════════════════════════════════════════════════════════════════
# Resume upload and analysis page
# ══════════════════════════════════════════════════════════════════════════

import os
import sys
import time
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.components import render_brand, section_head, info_banner, divider


def _run_analysis(resume_text, pdf_bytes, jd, target_level, education_req):
    """Run the complete analysis pipeline and return the result dict."""

    from src.resume_parser    import parse_resume, parse_resume_from_text
    from src.skill_extractor  import extract_skills
    from src.ats_scorer       import calculate_ats_score

    # Parse
    if pdf_bytes:
        resume_data = parse_resume(pdf_bytes)
    else:
        resume_data = parse_resume_from_text(resume_text)

    if resume_data.get("error"):
        return {"error": resume_data["error"]}

    # Skills
    skills_result = extract_skills(
        resume_data.get("raw_text", ""),
        resume_data.get("sections"),
    )

    # ATS score
    ats_result = calculate_ats_score(
        resume_data     = resume_data,
        resume_skills   = skills_result.get("all_skills", []),
        job_description = jd if jd.strip() else None,
        target_level    = target_level,
        required_education = education_req,
    )

    # Job matching (only if JD provided)
    match_result = {}
    if jd.strip():
        try:
            from src.job_matcher import match_resume_to_job
            match_result = match_resume_to_job(
                resume_data, jd,
                skills_result.get("all_skills", []),
            )
        except Exception:
            pass

    # Career prediction
    top_careers = []
    try:
        from src.career_recommender import CareerRecommender
        rec = CareerRecommender()
        top_careers = rec.predict_top_n(
            resume_data.get("raw_text", ""), resume_data, n=5
        )
    except Exception:
        # Rule-based fallback
        skills_lower = {s.lower() for s in skills_result.get("all_skills", [])}
        career_map = {
            "Data Scientist":            {"python","machine learning","sql","tensorflow","pandas"},
            "Machine Learning Engineer": {"python","tensorflow","pytorch","mlops","docker"},
            "Software Engineer":         {"java","python","c++","git","system design"},
            "Data Analyst":              {"sql","excel","tableau","power bi","python"},
            "Frontend Developer":        {"html","css","javascript","react","typescript"},
            "Backend Developer":         {"python","java","node.js","postgresql","mongodb"},
            "DevOps Engineer":           {"docker","kubernetes","aws","terraform","ci/cd"},
        }
        scores = {c: len(skills_lower & sk) for c, sk in career_map.items()}
        total  = sum(scores.values()) or 1
        top_careers = [
            {"rank": i+1, "career": c, "confidence": round(s/total*100, 1)}
            for i, (c, s) in enumerate(
                sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
            ) if s > 0
        ]

    return {
        "candidate":    resume_data,
        "ats":          ats_result,
        "skills":       skills_result,
        "careers":      top_careers,
        "match":        match_result,
    }


def show_analyzer():
    """Render the upload + analysis page."""

    # ── Sidebar ─────────────────────────────────────────────────────────────
    with st.sidebar:
        render_brand()
        st.markdown('<div style="margin-bottom:2rem"></div>', unsafe_allow_html=True)

        if st.button("🏠  Home",           use_container_width=True, key="nav_home"):
            st.session_state.page = "landing"; st.rerun()
        if st.button("📄  Analyze Resume", use_container_width=True, key="nav_analyze"):
            st.session_state.page = "analyzer"; st.rerun()
        if st.session_state.analysis_result:
            if st.button("📊  Dashboard",  use_container_width=True, key="nav_dash"):
                st.session_state.page = "dashboard"; st.rerun()

        divider()

        st.markdown("### ⚙️ Settings")
        target_level  = st.selectbox("Target level",   ["entry","mid","senior","lead"], index=1)
        education_req = st.selectbox("Education req",  ["any","diploma","bachelor","master","phd"], index=2)

        st.markdown('<div style="margin-top:1rem"></div>', unsafe_allow_html=True)
        st.markdown("### 📂 Sample Resumes")
        sample_choice = st.selectbox(
            "Load sample",
            ["None","Data Scientist","Software Engineer","Fresher"],
        )

    # ── Page header ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="padding:2rem 0 1rem">
        <h1 style="font-family:Syne,sans-serif;font-size:32px;font-weight:800;margin:0 0 8px">
            Analyze your resume
        </h1>
        <p style="font-size:15px;color:var(--text2);margin:0">
            Upload your PDF and get a complete ATS score, skill gap analysis, and AI improvement plan.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Upload area ─────────────────────────────────────────────────────────
    left, right = st.columns([3, 2], gap="large")

    with left:
        section_head("Upload Resume", "PDF format · Max 5MB")
        uploaded_file = st.file_uploader(
            label      = " ",
            type       = ["pdf"],
            label_visibility = "collapsed",
        )

        st.markdown('<div style="margin-top:1rem"></div>', unsafe_allow_html=True)
        section_head("Job Description", "Optional — improves keyword matching accuracy")
        jd_text = st.text_area(
            label       = " ",
            height      = 160,
            placeholder = "Paste the job description here for targeted keyword matching and skill gap analysis...",
            label_visibility = "collapsed",
        )

    with right:
        st.markdown("""
        <div class="glass-card" style="margin-top:0.5rem">
            <div style="font-family:Syne,sans-serif;font-size:14px;font-weight:700;margin-bottom:1rem">
                What you'll get
            </div>
        """, unsafe_allow_html=True)

        items = [
            ("🎯", "ATS Score (0–100)",              "Industry-standard scoring"),
            ("🔧", "15–200+ Skills detected",         "Technical + soft skills"),
            ("❌", "Missing skills identified",        "Exactly what to add"),
            ("📊", "6-component breakdown",            "Weighted analysis"),
            ("🤖", "AI career recommendations",        "ML-powered predictions"),
            ("💡", "Improvement checklist",            "Prioritized action plan"),
            ("📥", "Downloadable PDF report",          "Share with anyone"),
        ]
        for icon, title, sub in items:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid var(--border)">
                <span style="font-size:16px">{icon}</span>
                <div>
                    <div style="font-size:13px;font-weight:500;color:var(--text)">{title}</div>
                    <div style="font-size:11px;color:var(--text3)">{sub}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Load sample if chosen ────────────────────────────────────────────────
    sample_text = ""
    sample_map  = {
        "Data Scientist":    "data/sample_resumes/data_scientist_john_smith.txt",
        "Software Engineer": "data/sample_resumes/software_engineer_priya_patel.txt",
        "Fresher":           "data/sample_resumes/fresher_rahul_kumar.txt",
    }
    if sample_choice != "None":
        path = sample_map.get(sample_choice, "")
        if path and os.path.exists(path):
            sample_text = open(path, encoding="utf-8").read()
            info_banner(f"Sample loaded: <b>{sample_choice}</b>. Click Analyze to run.", "success")
        else:
            info_banner("Sample file not found. Run Phase 3 to create sample resumes.", "warning")

    # ── Analyze button ────────────────────────────────────────────────────────
    st.markdown('<div style="margin-top:1.5rem"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        analyze_clicked = st.button(
            "🔍  Analyze Resume Now",
            use_container_width=True,
            type="primary",
        )

    if not analyze_clicked:
        return

    # ── Validation ─────────────────────────────────────────────────────────
    has_pdf    = uploaded_file is not None
    has_text   = bool(sample_text.strip())

    if not has_pdf and not has_text:
        info_banner("Please upload a PDF resume or select a sample resume from the sidebar.", "warning")
        return

    # ── Animated loading screen ───────────────────────────────────────────
    loading_placeholder = st.empty()

    steps = [
        ("📖", "Extracting text from PDF..."),
        ("🔬", "Parsing resume sections..."),
        ("🧠", "Identifying skills with NLP..."),
        ("🎯", "Calculating ATS score..."),
        ("✨", "Generating AI insights..."),
    ]

    progress_bar = st.progress(0)

    for i, (icon, label) in enumerate(steps):
        loading_placeholder.markdown(f"""
        <div style="text-align:center;padding:2rem">
            <div class="loading-orb"></div>
            <h3 style="font-family:Syne,sans-serif;font-weight:700;margin-bottom:8px">{icon} {label}</h3>
            <p style="color:var(--text2);font-size:14px">Step {i+1} of {len(steps)}</p>
        </div>
        """, unsafe_allow_html=True)
        progress_bar.progress((i+1) / len(steps))
        time.sleep(0.3)

    # ── Run real analysis ─────────────────────────────────────────────────
    try:
        pdf_bytes = uploaded_file.read() if has_pdf else None
        result    = _run_analysis(
            resume_text   = sample_text,
            pdf_bytes     = pdf_bytes,
            jd            = jd_text,
            target_level  = target_level,
            education_req = education_req,
        )

        if result.get("error"):
            loading_placeholder.empty()
            progress_bar.empty()
            info_banner(f"Analysis error: {result['error']}", "error")
            return

        st.session_state.analysis_result = result
        loading_placeholder.empty()
        progress_bar.empty()

    except Exception as e:
        loading_placeholder.empty()
        progress_bar.empty()
        info_banner(f"Unexpected error: {str(e)}\n\nMake sure you ran Phase 3 (data_pipeline.py) first.", "error")
        return

    # ── Success → go to dashboard ─────────────────────────────────────────
    st.success("✅ Analysis complete! Redirecting to dashboard...")
    time.sleep(0.8)
    st.session_state.page = "dashboard"
    st.rerun()
