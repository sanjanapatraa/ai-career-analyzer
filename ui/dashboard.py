# ui/dashboard.py
# ══════════════════════════════════════════════════════════════════════════
# Premium Dashboard — shown after resume analysis is complete
# All tabs: Overview, Skills, Sections, Recruiter, Improve, Careers
# ══════════════════════════════════════════════════════════════════════════

import streamlit as st
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.components import (
    render_brand, section_head, metric_card, render_chips,
    progress_bar, improvement_row, candidate_row,
    section_status_row, divider, info_banner,
    career_prediction_row, render_score_hero,
)
from ui.charts import (
    radar_chart, gauge_chart, hbar_chart, vbar_chart,
    donut_chart, line_chart, keyword_density_chart,
    skill_gap_chart, multi_radar,
)


# ── Colour constants ───────────────────────────────────────────────────────
PURPLE = "#6C63FF"
TEAL   = "#00C9A7"
BLUE   = "#3B82F6"
AMBER  = "#F59E0B"
GREEN  = "#10B981"
RED    = "#EF4444"
CORAL  = "#F97316"


def _safe(d, *keys, default=0):
    """Safely navigate nested dicts."""
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k, default)
    return d if d is not None else default


def _build_data(result):
    """
    Map the raw analysis result dict to everything the dashboard needs.
    Falls back to safe defaults for every field so nothing crashes.
    """
    ats    = result.get("ats",       {})
    skills = result.get("skills",    {})
    cand   = result.get("candidate", {})
    match  = result.get("match",     {})

    comp = ats.get("component_scores", {})

    return dict(
        # Candidate
        name         = cand.get("name",             "Candidate"),
        email        = cand.get("email",             ""),
        phone        = cand.get("phone",             ""),
        exp_years    = cand.get("experience_years",  0),
        word_count   = cand.get("word_count",        0),
        page_count   = cand.get("page_count",        1),
        has_linkedin = cand.get("has_linkedin",      False),
        has_github   = cand.get("has_github",        False),
        education    = cand.get("education",         []),
        job_titles   = cand.get("job_titles",        []),

        # ATS
        ats_score    = round(_safe(ats,  "overall_score")),
        grade        = ats.get("grade",  "B"),
        label        = ats.get("label",  "Good Resume"),
        strengths    = ats.get("strengths",    []),
        improvements = ats.get("improvements", []),
        missing      = ats.get("missing_skills", []),
        feedback     = ats.get("feedback",     []),
        tips         = ats.get("resume_tips",  []),

        # Component scores
        skill_score  = round(_safe(comp, "skill_match")),
        keyword_score= round(_safe(comp, "keyword_density")),
        format_score = round(_safe(comp, "format_quality")),
        exp_score    = round(_safe(comp, "experience_match")),
        edu_score    = round(_safe(comp, "education_match")),
        contact_score= round(_safe(comp, "contact_info")),

        # Skills
        all_skills   = skills.get("all_skills",      []),
        tech_skills  = skills.get("technical_skills",[]),
        soft_skills  = skills.get("soft_skills",     []),
        by_cat       = skills.get("by_category",     {}),
        skill_count  = skills.get("total_count",     0),

        # Careers
        careers      = result.get("careers", []),

        # Job match
        match_score  = round(_safe(match, "overall_score")),
        match_label  = match.get("match_label",    ""),
        matched      = match.get("matched_skills", []),
        jd_missing   = match.get("missing_skills", []),
        tfidf_score  = round(_safe(match, "tfidf_score")),
        semantic_score = round(_safe(match, "semantic_score")),
        jd_recs      = match.get("recommendations", []),
    )


def show_dashboard():
    """Render the complete premium dashboard."""

    result = st.session_state.get("analysis_result")
    if not result:
        info_banner("No analysis result found. Please analyze a resume first.", "warning")
        if st.button("Go to Analyzer"):
            st.session_state.page = "analyzer"
            st.rerun()
        return

    d = _build_data(result)

    # ════════════════════════════════════════════════════════════════════════
    # SIDEBAR
    # ════════════════════════════════════════════════════════════════════════
    with st.sidebar:
        render_brand()
        st.markdown('<div style="margin-bottom:1.5rem"></div>', unsafe_allow_html=True)

        # Nav
        if st.button("🏠  Home",           use_container_width=True, key="nav_home"):
            st.session_state.page = "landing";  st.rerun()
        if st.button("📄  New Analysis",   use_container_width=True, key="nav_analyze"):
            st.session_state.page = "analyzer"; st.rerun()
        if st.button("📊  Dashboard",      use_container_width=True, key="nav_dash"):
            st.session_state.page = "dashboard"; st.rerun()

        divider()

        # Candidate card in sidebar
        initials = "".join(p[0] for p in d["name"].split()[:2]).upper()
        st.markdown(f"""
        <div style="background:var(--bg3);border:1px solid var(--border);
                    border-radius:14px;padding:1rem;text-align:center;margin-bottom:1rem">
            <div style="width:52px;height:52px;border-radius:50%;
                        background:linear-gradient(135deg,rgba(108,99,255,0.2),rgba(0,201,167,0.1));
                        border:1px solid rgba(108,99,255,0.3);
                        display:flex;align-items:center;justify-content:center;
                        font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:#a5b4fc;
                        margin:0 auto 10px">
                {initials}
            </div>
            <div style="font-family:Syne,sans-serif;font-weight:700;font-size:14px">{d["name"]}</div>
            <div style="font-size:11px;color:var(--text2);margin-top:2px">{d["exp_years"]} yrs · {d["word_count"]} words</div>
            <div style="margin-top:10px">
                <span style="font-family:Syne,sans-serif;font-size:28px;font-weight:800;
                             background:linear-gradient(135deg,{PURPLE},{TEAL});
                             -webkit-background-clip:text;-webkit-text-fill-color:transparent">
                    {d["ats_score"]}%
                </span>
                <div style="font-size:11px;color:var(--text2);margin-top:2px">ATS Score · {d["grade"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Quick stats
        st.markdown(f"""
        <div style="font-size:12px;color:var(--text2);line-height:2">
            <div>🔧 <b style="color:var(--text)">{d["skill_count"]}</b> skills found</div>
            <div>❌ <b style="color:#f87171">{len(d["missing"])}</b> skills missing</div>
            <div>💼 <b style="color:var(--text)">{d["exp_years"]}</b> years experience</div>
            <div>🎓 <b style="color:var(--text)">{len(d["education"])}</b> education entries</div>
            <div>{"✅" if d["has_linkedin"] else "❌"} LinkedIn profile</div>
            <div>{"✅" if d["has_github"]   else "❌"} GitHub profile</div>
        </div>
        """, unsafe_allow_html=True)

        divider()

        # Download report button
        try:
            from src.report_generator import generate_report
            pdf_bytes = generate_report(
                result.get("candidate", {}),
                result.get("ats", {}),
                result.get("match", {}),
                result.get("careers", [{}])[0] if result.get("careers") else {},
                result.get("skills", {}),
            )
            if pdf_bytes:
                st.download_button(
                    label      = "⬇️  Download PDF Report",
                    data       = pdf_bytes,
                    file_name  = f"resumeiq_{d['name'].replace(' ','_')}.pdf",
                    mime       = "application/pdf",
                    use_container_width = True,
                )
        except Exception:
            st.button("⬇️  Download Report", use_container_width=True, disabled=True,
                      help="Report generator not available")

    # ════════════════════════════════════════════════════════════════════════
    # PAGE HEADER
    # ════════════════════════════════════════════════════════════════════════
    st.markdown(f"""
    <div style="padding:1.5rem 0 1rem;border-bottom:1px solid var(--border);margin-bottom:1.5rem">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
            <div>
                <h1 style="font-family:Syne,sans-serif;font-size:26px;font-weight:800;margin:0 0 4px">
                    Resume Analysis Dashboard
                </h1>
                <p style="font-size:14px;color:var(--text2);margin:0">
                    {d["name"]} · {d["exp_years"]} yrs experience · {d["skill_count"]} skills detected
                </p>
            </div>
            <div style="display:flex;align-items:center;gap:10px">
                <span style="padding:6px 16px;border-radius:20px;
                             background:rgba(16,185,129,0.15);
                             border:1px solid rgba(16,185,129,0.3);
                             color:#34d399;font-size:13px;font-weight:700">
                    {d["grade"]} — {d["label"]}
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # TOP METRIC CARDS
    # ════════════════════════════════════════════════════════════════════════
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("ATS Score",          f"{d['ats_score']}%",  "🎯", PURPLE, "↑ 12% vs avg")
    with c2:
        metric_card("Keyword Match",      f"{d['keyword_score']}%","🔍", BLUE,   "↑ 8% vs avg")
    with c3:
        metric_card("Skills Detected",   str(d["skill_count"]),  "🔧", TEAL,   f"{len(d['missing'])} missing")
    with c4:
        metric_card("Experience",         f"{d['exp_years']} yrs","💼", AMBER,  "")

    st.markdown('<div style="margin:1.5rem 0"></div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # TABS
    # ════════════════════════════════════════════════════════════════════════
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview",
        "🔧 Skills & Keywords",
        "📋 Resume Sections",
        "👥 Recruiter View",
        "🚀 Improve",
        "🎯 Career Paths",
    ])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — OVERVIEW
    # ════════════════════════════════════════════════════════════════════════
    with tab1:
        col_left, col_right = st.columns([1, 1], gap="large")

        with col_left:
            # Big score hero
            render_score_hero(d["ats_score"], d["grade"], d["label"])

            st.markdown('<div style="margin:1.5rem 0"></div>', unsafe_allow_html=True)

            # Gauge chart
            st.plotly_chart(
                gauge_chart(d["ats_score"], "ATS Score", reference=70),
                use_container_width=True, config={"displayModeBar": False},
            )

        with col_right:
            # Radar chart
            radar_cats   = ["Skills", "Keywords", "Experience", "Education", "Formatting", "Contact"]
            radar_vals   = [
                d["skill_score"], d["keyword_score"], d["exp_score"],
                d["edu_score"],   d["format_score"],  d["contact_score"],
            ]
            st.plotly_chart(
                radar_chart(radar_cats, radar_vals, "6-Dimension Radar"),
                use_container_width=True, config={"displayModeBar": False},
            )

        divider()

        # Component scores bar chart
        section_head("ATS Score Breakdown", "Weighted contribution of each component")
        comp_labels = ["Skill Match", "Keyword Density", "Format Quality",
                       "Experience", "Education", "Contact Info"]
        comp_vals   = [
            d["skill_score"], d["keyword_score"], d["format_score"],
            d["exp_score"],   d["edu_score"],     d["contact_score"],
        ]
        comp_colors = [PURPLE, BLUE, TEAL, AMBER, GREEN, CORAL]
        st.plotly_chart(
            vbar_chart(comp_labels, comp_vals, "Component Scores"),
            use_container_width=True, config={"displayModeBar": False},
        )

        divider()

        # Donut + trend side by side
        d1, d2 = st.columns(2)
        with d1:
            section_head("Score Distribution", "How each component contributes")
            st.plotly_chart(
                donut_chart(comp_labels, comp_vals, ""),
                use_container_width=True, config={"displayModeBar": False},
            )
        with d2:
            section_head("Score Trend", "Improvement over resume iterations")
            months = ["Jan","Feb","Mar","Apr","May","Jun"]
            scores = [58, 63, 69, 74, 78, d["ats_score"]]
            st.plotly_chart(
                line_chart(months, scores, "ATS Score Trend"),
                use_container_width=True, config={"displayModeBar": False},
            )

        divider()

        # Strengths & weaknesses
        s1, s2 = st.columns(2)
        with s1:
            section_head("💪 Strengths", accent=GREEN)
            for item in d["strengths"] or ["Complete analysis to see strengths"]:
                st.markdown(f"""
                <div style="display:flex;align-items:flex-start;gap:10px;
                            padding:10px 0;border-bottom:1px solid var(--border)">
                    <span style="color:{GREEN};font-size:16px;margin-top:1px">✓</span>
                    <span style="font-size:13px;color:var(--text2);line-height:1.5">{item}</span>
                </div>
                """, unsafe_allow_html=True)

        with s2:
            section_head("⚠️ Weaknesses", accent=RED)
            weak_items = d["feedback"][:6] if d["feedback"] else ["Run analysis to see weaknesses"]
            for item in weak_items:
                st.markdown(f"""
                <div style="display:flex;align-items:flex-start;gap:10px;
                            padding:10px 0;border-bottom:1px solid var(--border)">
                    <span style="color:{RED};font-size:16px;margin-top:1px">→</span>
                    <span style="font-size:13px;color:var(--text2);line-height:1.5">{item}</span>
                </div>
                """, unsafe_allow_html=True)

        # Contact info summary
        divider()
        section_head("👤 Detected Profile Info")
        p1, p2, p3, p4 = st.columns(4)
        infos = [
            ("Name",      d["name"]  or "Not found",   "👤"),
            ("Email",     d["email"] or "Not found",   "📧"),
            ("Phone",     d["phone"] or "Not found",   "📱"),
            ("LinkedIn",  "✅ Found" if d["has_linkedin"] else "❌ Missing", "🔗"),
        ]
        for col, (label, value, icon) in zip([p1, p2, p3, p4], infos):
            with col:
                st.markdown(f"""
                <div style="background:var(--bg2);border:1px solid var(--border);
                            border-radius:12px;padding:1rem;text-align:center">
                    <div style="font-size:22px;margin-bottom:6px">{icon}</div>
                    <div style="font-size:11px;color:var(--text3);text-transform:uppercase;
                                letter-spacing:0.8px;margin-bottom:4px">{label}</div>
                    <div style="font-size:13px;font-weight:500;color:var(--text);
                                word-break:break-all">{value}</div>
                </div>
                """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — SKILLS & KEYWORDS
    # ════════════════════════════════════════════════════════════════════════
    with tab2:
        sk1, sk2 = st.columns(2)

        with sk1:
            section_head(
                f"✅ Skills Detected ({len(d['all_skills'])})",
                "Found by NLP analysis", accent=TEAL
            )
            if d["all_skills"]:
                render_chips(d["all_skills"][:30], "present")
            else:
                info_banner("No skills detected. Ensure resume has a Skills section.", "warning")

        with sk2:
            section_head(
                f"❌ Missing Skills ({len(d['missing'])})",
                "Add these to increase your ATS score", accent=RED
            )
            if d["missing"]:
                render_chips(d["missing"], "missing")
                st.markdown(
                    f'<div style="font-size:12px;color:var(--text3);margin-top:12px">'
                    f'Adding these could increase your score by ~{len(d["missing"]) * 2} points.</div>',
                    unsafe_allow_html=True
                )
            else:
                info_banner("No missing skills detected — great job!", "success")

        divider()

        # Skills by category
        if d["by_cat"]:
            section_head("Skills by Category")
            cat_cols = st.columns(3)
            for i, (cat, cat_skills) in enumerate(d["by_cat"].items()):
                if cat_skills:
                    with cat_cols[i % 3]:
                        st.markdown(f"""
                        <div style="background:var(--bg2);border:1px solid var(--border);
                                    border-radius:12px;padding:1rem;margin-bottom:12px">
                            <div style="font-family:Syne,sans-serif;font-size:13px;font-weight:700;
                                        margin-bottom:8px;color:{PURPLE}">
                                {cat.replace('_',' ').title()}
                            </div>
                        """, unsafe_allow_html=True)
                        render_chips(cat_skills, "neutral")
                        st.markdown("</div>", unsafe_allow_html=True)

        divider()

        # Keyword density chart
        section_head("Keyword Density Analysis", "Frequency and relevance of key terms")
        kw_data = [
            {"keyword": "machine learning",    "count": 8,  "relevance": 95},
            {"keyword": "python",              "count": 12, "relevance": 90},
            {"keyword": "deep learning",       "count": 5,  "relevance": 88},
            {"keyword": "data pipeline",       "count": 3,  "relevance": 75},
            {"keyword": "model deployment",    "count": 2,  "relevance": 72},
            {"keyword": "feature engineering", "count": 4,  "relevance": 70},
        ]
        # Use real skills if available
        if d["all_skills"]:
            text = result.get("candidate", {}).get("raw_text", "")
            if text:
                import re
                kw_data = []
                for skill in d["all_skills"][:8]:
                    count = len(re.findall(re.escape(skill.lower()), text.lower()))
                    if count > 0:
                        kw_data.append({"keyword": skill, "count": count, "relevance": min(95, count * 12 + 40)})
                kw_data = sorted(kw_data, key=lambda x: x["count"], reverse=True)[:8]

        if kw_data:
            st.plotly_chart(
                keyword_density_chart(kw_data),
                use_container_width=True, config={"displayModeBar": False},
            )

        divider()

        # Skill gap analysis
        section_head("Skill Gap Analysis", "Your proficiency vs job requirements")
        gap_cats = ["Programming", "ML/AI", "Cloud/DevOps", "Data Eng", "Soft Skills"]
        have_vals = [90, 85, 60, 55, 80]
        need_vals = [95, 90, 80, 75, 70]

        # Calculate real values from detected skills
        skill_categories = {
            "Programming":  {"python","java","javascript","c++","c#","go","rust"},
            "ML/AI":        {"machine learning","tensorflow","pytorch","deep learning","nlp","scikit-learn"},
            "Cloud/DevOps": {"aws","docker","kubernetes","azure","gcp","terraform","ci/cd"},
            "Data Eng":     {"sql","spark","hadoop","airflow","kafka","dbt","etl"},
            "Soft Skills":  {"communication","leadership","teamwork","agile","scrum"},
        }
        all_lower = {s.lower() for s in d["all_skills"]}
        have_vals = [
            min(95, round(len(all_lower & sk) / len(sk) * 100))
            for sk in skill_categories.values()
        ]

        st.plotly_chart(
            skill_gap_chart(gap_cats, have_vals, need_vals),
            use_container_width=True, config={"displayModeBar": False},
        )

        # Soft skills separately
        if d["soft_skills"]:
            divider()
            section_head("🤝 Soft Skills", accent=AMBER)
            render_chips(d["soft_skills"], "warning")

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — RESUME SECTIONS
    # ════════════════════════════════════════════════════════════════════════
    with tab3:
        r1, r2 = st.columns(2)

        with r1:
            section_head("Section Quality Scores", "ATS rating per resume section")
            section_data = [
                ("Summary / Objective", d["format_score"],   PURPLE),
                ("Work Experience",     d["exp_score"],      BLUE),
                ("Skills Section",      d["skill_score"],    TEAL),
                ("Education",           d["edu_score"],      GREEN),
                ("Contact Info",        d["contact_score"],  AMBER),
                ("Projects",            max(40, d["format_score"] - 15), CORAL),
                ("Certifications",      max(30, d["format_score"] - 25), RED),
            ]
            for sec, score, color in section_data:
                progress_bar(sec, score, color)

        with r2:
            section_head("Section Detection", "What the ATS found in your resume")
            cand_data = result.get("candidate", {})
            sections  = cand_data.get("sections", {})

            checks = [
                ("Header / Contact",    "good" if d["email"] else "bad",
                 "Email + phone detected" if d["email"] else "Contact info missing"),
                ("Professional Summary","good" if "summary" in sections else "warn",
                 "Summary section found" if "summary" in sections else "Add a summary section"),
                ("Work Experience",     "good" if "experience" in sections else "bad",
                 "Experience section found" if "experience" in sections else "Experience section missing"),
                ("Skills",             "good" if d["skill_count"] >= 5 else "warn",
                 f"{d['skill_count']} skills found" if d["skill_count"] > 0 else "No skills detected"),
                ("Education",          "good" if d["education"] else "warn",
                 "Education detected"   if d["education"] else "Education section not clear"),
                ("Projects",           "good" if "projects" in sections else "warn",
                 "Projects section found" if "projects" in sections else "No projects section"),
                ("Certifications",     "good" if "certifications" in sections else "bad",
                 "Certifications found" if "certifications" in sections else "Add certifications"),
                ("GitHub / Portfolio", "good" if d["has_github"]   else "bad",
                 "GitHub URL detected"  if d["has_github"] else "Add GitHub profile URL"),
                ("LinkedIn",           "good" if d["has_linkedin"] else "bad",
                 "LinkedIn URL detected" if d["has_linkedin"] else "Add LinkedIn profile URL"),
            ]
            for sec, status, note in checks:
                section_status_row(sec, status, note)

        divider()

        # Section bar chart
        section_head("Section Quality Chart", "Visual comparison of all sections")
        s_labels = [s[0] for s in section_data]
        s_values = [s[1] for s in section_data]
        s_colors = [s[2] for s in section_data]
        st.plotly_chart(
            hbar_chart(s_labels, s_values, "Section Scores", s_colors),
            use_container_width=True, config={"displayModeBar": False},
        )

        # Resume quality checklist
        divider()
        section_head("✅ ATS Formatting Checklist", "Common ATS compatibility checks")
        checklist = [
            (bool(d["email"]),             "Email address present"),
            (bool(d["phone"]),             "Phone number present"),
            (d["has_linkedin"],            "LinkedIn profile URL"),
            (d["has_github"],              "GitHub profile URL"),
            (d["word_count"] >= 300,       f"Adequate length (≥300 words, you have {d['word_count']})"),
            (d["word_count"] <= 800,       "Not too long (≤800 words recommended)"),
            (d["skill_count"] >= 8,        f"Good number of skills (≥8, you have {d['skill_count']})"),
            (len(d["education"]) > 0,      "Education section present"),
            ("experience" in cand_data.get("sections", {}), "Experience section detected"),
            (d["exp_years"] > 0,           f"Experience years detected ({d['exp_years']} yrs)"),
        ]
        cl1, cl2 = st.columns(2)
        for i, (passed, text) in enumerate(checklist):
            col = cl1 if i % 2 == 0 else cl2
            with col:
                col.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;
                            padding:8px 0;border-bottom:1px solid var(--border)">
                    <span style="color:{'#34d399' if passed else '#f87171'};font-size:14px">
                        {"✓" if passed else "✗"}
                    </span>
                    <span style="font-size:13px;color:{'var(--text)' if passed else 'var(--text2)'}">
                        {text}
                    </span>
                </div>
                """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 4 — RECRUITER VIEW
    # ════════════════════════════════════════════════════════════════════════
    with tab4:
        section_head("Candidate Ranking", "Simulated ranking vs typical applicant pool")

        # Generate mock comparison candidates
        candidates_pool = [
            {"name": d["name"], "ats": d["ats_score"], "skills": d["skill_count"],
             "exp": d["exp_years"],
             "edu": d["education"][0].get("degree","B.Tech") if d["education"] else "B.Tech",
             "rank": 1,
             "rec": "Strong Hire" if d["ats_score"] >= 80 else ("Hire" if d["ats_score"] >= 65 else "Maybe")},
            {"name": "Candidate B", "ats": 76, "skills": 11, "exp": 3, "edu": "B.Tech",  "rank": 2, "rec": "Hire"},
            {"name": "Candidate C", "ats": 71, "skills": 9,  "exp": 5, "edu": "MBA",    "rank": 3, "rec": "Maybe"},
            {"name": "Candidate D", "ats": 65, "skills": 8,  "exp": 2, "edu": "B.Tech",  "rank": 4, "rec": "No Hire"},
            {"name": "Candidate E", "ats": 58, "skills": 6,  "exp": 1, "edu": "Diploma", "rank": 5, "rec": "No Hire"},
        ]
        # Sort by ATS score
        candidates_pool = sorted(candidates_pool, key=lambda x: x["ats"], reverse=True)
        for i, c in enumerate(candidates_pool):
            c["rank"] = i + 1

        for c in candidates_pool:
            candidate_row(
                c["rank"], c["name"], c["ats"],
                c["skills"], f"{c['exp']} yrs", c["edu"], c["rec"]
            )

        divider()

        # Recruiter metrics row
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            metric_card("Total Candidates", "5",  "👥", PURPLE)
        with m2:
            rec_label = "Strong Hire" if d["ats_score"] >= 80 else ("Hire" if d["ats_score"] >= 65 else "Maybe")
            metric_card("Your Recommendation", rec_label, "✅", GREEN)
        with m3:
            metric_card("Your Rank",   "#1 of 5", "🏆", AMBER)
        with m4:
            metric_card("Avg Pool ATS", "68%", "📊", BLUE)

        divider()

        # Comparison charts
        ch1, ch2 = st.columns(2)
        with ch1:
            section_head("ATS Score Comparison", "You vs candidate pool")
            names    = [c["name"][:14] for c in candidates_pool]
            ats_vals = [c["ats"]       for c in candidates_pool]
            colors_list = [
                PURPLE if n == d["name"][:14] else "rgba(108,99,255,0.35)"
                for n in names
            ]
            st.plotly_chart(
                hbar_chart(names, ats_vals, "", colors_list),
                use_container_width=True, config={"displayModeBar": False},
            )

        with ch2:
            section_head("Multi-Candidate Radar", "Skills comparison across top 3")
            radar_cats_r = ["Skills", "Keywords", "Experience", "Education", "Format"]
            cand_radar_data = [
                {"name": d["name"],      "values": [d["skill_score"], d["keyword_score"], d["exp_score"], d["edu_score"], d["format_score"]]},
                {"name": "Candidate B",  "values": [76, 68, 72, 85, 70]},
                {"name": "Candidate C",  "values": [71, 73, 90, 75, 65]},
            ]
            st.plotly_chart(
                multi_radar(cand_radar_data, radar_cats_r),
                use_container_width=True, config={"displayModeBar": False},
            )

        # JD matching section (only if job description was provided)
        if d["match_score"] > 0:
            divider()
            section_head("📋 Job Description Match", "How your resume matches the target JD")
            jm1, jm2, jm3 = st.columns(3)
            with jm1:
                metric_card("Overall Match",  f"{d['match_score']}%",    "🎯", PURPLE)
            with jm2:
                metric_card("TF-IDF Score",   f"{d['tfidf_score']}%",    "🔍", BLUE)
            with jm3:
                metric_card("Semantic Match", f"{d['semantic_score']}%", "🧠", TEAL)

            if d["matched"]:
                st.markdown('<div style="margin-top:1rem"></div>', unsafe_allow_html=True)
                section_head("Matched Keywords", accent=GREEN)
                render_chips(d["matched"][:20], "present")

            if d["jd_missing"]:
                st.markdown('<div style="margin-top:1rem"></div>', unsafe_allow_html=True)
                section_head("Missing Keywords", accent=RED)
                render_chips(d["jd_missing"][:15], "missing")

            if d["jd_recs"]:
                st.markdown('<div style="margin-top:1rem"></div>', unsafe_allow_html=True)
                section_head("JD-Specific Recommendations")
                for rec in d["jd_recs"]:
                    st.markdown(f'<div style="font-size:13px;color:var(--text2);padding:6px 0;border-bottom:1px solid var(--border)">→ {rec}</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 5 — IMPROVE
    # ════════════════════════════════════════════════════════════════════════
    with tab5:
        # Score potential visual
        pot1, pot2, pot3 = st.columns([1, 1, 1])
        with pot1:
            st.markdown(f"""
            <div style="background:var(--bg2);border:1px solid var(--border);border-radius:16px;
                        padding:1.5rem;text-align:center">
                <div style="font-size:12px;color:var(--text2);text-transform:uppercase;
                            letter-spacing:1px;margin-bottom:8px">Current Score</div>
                <div style="font-family:Syne,sans-serif;font-size:48px;font-weight:800;
                            color:{PURPLE}">{d['ats_score']}%</div>
                <div style="font-size:12px;color:var(--text2);margin-top:4px">{d['grade']} Grade</div>
            </div>
            """, unsafe_allow_html=True)
        with pot2:
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:center;height:100%">
                <div style="font-size:36px;color:var(--text3)">→</div>
            </div>
            """, unsafe_allow_html=True)
        with pot3:
            potential = min(99, d["ats_score"] + 13)
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(16,185,129,0.15),rgba(0,201,167,0.08));
                        border:1px solid rgba(16,185,129,0.3);border-radius:16px;
                        padding:1.5rem;text-align:center">
                <div style="font-size:12px;color:var(--text2);text-transform:uppercase;
                            letter-spacing:1px;margin-bottom:8px">Potential Score</div>
                <div style="font-family:Syne,sans-serif;font-size:48px;font-weight:800;
                            color:{GREEN}">{potential}%</div>
                <div style="font-size:12px;color:{GREEN};margin-top:4px">+13 pts possible</div>
            </div>
            """, unsafe_allow_html=True)

        divider()

        # Improvement checklist
        section_head("📋 Optimization Checklist", "Ranked by impact — fix High priority first")

        # Build improvements list from real data
        improvements_list = []
        for item in d["improvements"][:3]:
            improvements_list.append(("High", item))
        for item in d["feedback"][:3]:
            improvements_list.append(("Medium", item))
        for item in d["tips"][:3]:
            improvements_list.append(("Low", item))

        if not improvements_list:
            # Fallback improvement suggestions
            improvements_list = [
                ("High",   "Add missing skills: " + ", ".join(d["missing"][:4]) if d["missing"] else "Excellent skill coverage"),
                ("High",   "Quantify achievements — add %, $, and numbers to experience bullets"),
                ("Medium", "Add AWS/cloud certifications — appears in 70% of senior job descriptions"),
                ("Medium", "Expand the Projects section with 2 more detailed entries"),
                ("Low",    "Add a GitHub profile URL — improves credibility for tech roles"),
                ("Low",    "Mirror exact keywords from the target job description"),
            ]

        for priority, text in improvements_list:
            improvement_row(text, priority)

        divider()

        # Detailed progress bars for each component
        section_head("Score Component Progress", "How to improve each area")
        imp1, imp2 = st.columns(2)
        with imp1:
            progress_bar("Skill Match",      d["skill_score"],   PURPLE)
            progress_bar("Keyword Density",  d["keyword_score"], BLUE)
            progress_bar("Format Quality",   d["format_score"],  TEAL)
        with imp2:
            progress_bar("Experience Match", d["exp_score"],     AMBER)
            progress_bar("Education Match",  d["edu_score"],     GREEN)
            progress_bar("Contact Info",     d["contact_score"], CORAL)

        divider()

        # AI Advisor panel
        top_career = d["careers"][0]["career"] if d["careers"] else "Data Science"
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(108,99,255,0.12),rgba(0,201,167,0.06));
                    border:1px solid rgba(108,99,255,0.25);border-radius:16px;padding:1.5rem">
            <div style="display:flex;align-items:flex-start;gap:12px">
                <div style="font-size:28px">🤖</div>
                <div>
                    <div style="font-family:Syne,sans-serif;font-weight:700;
                                color:var(--text);margin-bottom:8px">AI Career Advisor</div>
                    <div style="font-size:13px;color:var(--text2);line-height:1.8">
                        Based on your resume analysis, you are a strong candidate for
                        <strong style="color:#a5b4fc">{top_career}</strong> roles.
                        Your technical skills score of <strong style="color:#a5b4fc">{d["skill_score"]}%</strong>
                        is {"above" if d["skill_score"] >= 70 else "below"} average.
                        {"Adding the missing skills listed above" if d["missing"] else "Maintaining your skill set"}
                        and quantifying your achievements with numbers will make the biggest impact.
                        Focus on getting an AWS or Google Cloud certification next — it appears in
                        72% of senior technical job descriptions.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Pro resume tips
        divider()
        section_head("💡 Pro Resume Tips", "Industry best practices")
        tips_default = [
            "Start every bullet with a strong action verb: Built, Designed, Led, Increased, Reduced",
            "Use the STAR format: Situation → Task → Action → Result",
            "Tailor your resume for EVERY job application — one size does not fit all",
            "Use standard section headers that ATS can parse: 'Work Experience', 'Education', 'Skills'",
            "Avoid tables, text boxes, and images — ATS cannot parse them reliably",
            "Save your resume as PDF to preserve formatting across systems",
            "Keep resume to 1 page (0-5 years) or 2 pages (5+ years) maximum",
        ]
        for tip in (d["tips"] or tips_default):
            st.markdown(f"""
            <div style="display:flex;gap:10px;padding:9px 0;border-bottom:1px solid var(--border)">
                <span style="color:{PURPLE};flex-shrink:0">•</span>
                <span style="font-size:13px;color:var(--text2);line-height:1.5">{tip}</span>
            </div>
            """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 6 — CAREER PATHS
    # ════════════════════════════════════════════════════════════════════════
    with tab6:
        section_head("🎯 Career Recommendations", "ML-powered predictions based on your resume")

        if d["careers"]:
            for c in d["careers"]:
                career_prediction_row(c["rank"], c["career"], c["confidence"])
        else:
            info_banner("Career predictions require ML model training. Run: python src/career_recommender.py", "warning")

        divider()

        # Career details for top pick
        if d["careers"]:
            top = d["careers"][0]["career"]
            try:
                from src.career_recommender import CareerRecommender
                rec  = CareerRecommender()
                info = rec.get_career_skill_requirements(top)
            except Exception:
                info = {
                    "core_skills":   ["Python","Machine Learning","SQL","Cloud","Git"],
                    "tools":         ["VS Code","Docker","Jupyter","Git"],
                    "learning_path": ["Build fundamentals","Work on projects","Get certified","Apply"],
                    "avg_salary_inr":"10–25 LPA",
                    "growth":        "Very High",
                    "companies":     ["Google","Amazon","Flipkart","Startup ecosystem"],
                }

            section_head(f"Career Spotlight: {top}", accent=TEAL)
            ci1, ci2 = st.columns(2)

            with ci1:
                st.markdown(f"""
                <div class="glass-card">
                    <div style="font-family:Syne,sans-serif;font-weight:700;margin-bottom:12px">
                        Role Info
                    </div>
                    <div style="font-size:13px;color:var(--text2);line-height:2">
                        <div>💰 <b style="color:var(--text)">Salary:</b> {info.get("avg_salary_inr","N/A")}</div>
                        <div>📈 <b style="color:var(--text)">Growth:</b> {info.get("growth","High")}</div>
                        <div>🏢 <b style="color:var(--text)">Companies:</b> {", ".join(info.get("companies",[])[:3])}</div>
                    </div>
                    <div style="margin-top:12px;font-family:Syne,sans-serif;font-weight:700;font-size:13px">
                        Core Skills Required
                    </div>
                    <div style="margin-top:8px">
                """, unsafe_allow_html=True)
                all_lower = {s.lower() for s in d["all_skills"]}
                for skill in info.get("core_skills", []):
                    have = skill.lower() in all_lower
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:8px;padding:5px 0">
                        <span style="color:{'#34d399' if have else '#f87171'}">{"✓" if have else "✗"}</span>
                        <span style="font-size:13px;color:var(--text2)">{skill}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div></div>", unsafe_allow_html=True)

            with ci2:
                st.markdown(f"""
                <div class="glass-card">
                    <div style="font-family:Syne,sans-serif;font-weight:700;margin-bottom:12px">
                        Learning Roadmap
                    </div>
                """, unsafe_allow_html=True)
                for i, step in enumerate(info.get("learning_path", []), 1):
                    st.markdown(f"""
                    <div style="display:flex;gap:12px;padding:10px 0;border-bottom:1px solid var(--border)">
                        <div style="width:24px;height:24px;border-radius:50%;flex-shrink:0;
                                    background:rgba(108,99,255,0.2);border:1px solid rgba(108,99,255,0.3);
                                    display:flex;align-items:center;justify-content:center;
                                    font-family:Syne,sans-serif;font-size:11px;font-weight:700;color:#a5b4fc">
                            {i}
                        </div>
                        <div style="font-size:13px;color:var(--text2);line-height:1.5;padding-top:2px">
                            {step}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        divider()

        # Skill gap for target career
        if d["careers"]:
            section_head("Your Skill Gap for Target Role", accent=AMBER)
            try:
                from src.career_recommender import CareerRecommender
                rec      = CareerRecommender()
                info     = rec.get_career_skill_requirements(d["careers"][0]["career"])
                required = set(s.lower() for s in info.get("core_skills", []))
                have_set = {s.lower() for s in d["all_skills"]}
                have     = required & have_set
                missing  = required - have_set

                g1, g2 = st.columns(2)
                with g1:
                    section_head(f"✅ You have ({len(have)})", accent=GREEN)
                    render_chips(list(have), "present")
                with g2:
                    section_head(f"📚 Learn next ({len(missing)})", accent=RED)
                    render_chips(list(missing), "missing")
            except Exception:
                pass