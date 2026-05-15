# pages/3_Job_Matcher.py
# Compare your resume against any job description.

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Job Matcher", page_icon="💼", layout="wide")

st.markdown("# 💼 Job Description Matcher")
st.markdown("Paste any job description and see exactly how well your resume matches it.")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📄 Your Resume")
    resume_input = st.text_area(
        "Paste your resume text",
        height=350,
        placeholder="Paste your full resume text here..."
    )

with col2:
    st.markdown("### 📋 Job Description")
    jd_input = st.text_area(
        "Paste the job description",
        height=350,
        placeholder="Paste the full job description here..."
    )

if st.button("🔍 Analyze Match", type="primary", use_container_width=True):
    if not resume_input.strip():
        st.warning("Please paste your resume text.")
        st.stop()
    if not jd_input.strip():
        st.warning("Please paste the job description.")
        st.stop()

    with st.spinner("Analyzing match using NLP and ML..."):
        from src.resume_parser   import parse_resume_from_text
        from src.skill_extractor import extract_skills
        from src.job_matcher     import match_resume_to_job

        resume_data   = parse_resume_from_text(resume_input)
        skills_result = extract_skills(resume_input, resume_data.get('sections'))
        match_result  = match_resume_to_job(
            resume_data, jd_input, skills_result['all_skills']
        )

    st.divider()
    st.markdown("## 📊 Match Results")

    # ── Score metrics ─────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Overall Match",    f"{match_result['overall_score']:.0f}%",
              delta=match_result['match_label'])
    m2.metric("Skill Match",      f"{match_result['skill_match_score']:.0f}%")
    m3.metric("Keyword Match",    f"{match_result['tfidf_score']:.0f}%")
    m4.metric("Semantic Match",   f"{match_result['semantic_score']:.0f}%")

    # ── Visual match indicator ────────────────────────────────────────
    score = match_result['overall_score']
    color = '#2ecc71' if score >= 70 else ('#f39c12' if score >= 50 else '#e74c3c')

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        gauge={
            'axis':  {'range': [0, 100]},
            'bar':   {'color': color},
            'steps': [
                {'range': [0,  50],  'color': '#fadbd8'},
                {'range': [50, 70],  'color': '#fdebd0'},
                {'range': [70, 100], 'color': '#d5f5e3'},
            ],
        },
        title={'text': "Overall Match Score"},
    ))
    fig.update_layout(height=250, margin=dict(t=40, b=10, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Skill comparison ──────────────────────────────────────────────
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown("### ✅ Matching Skills")
        for skill in match_result.get('matched_skills', [])[:15]:
            st.markdown(f"✅ {skill}")
        if not match_result.get('matched_skills'):
            st.info("No direct skill matches found.")

    with sc2:
        st.markdown("### ❌ Missing Skills")
        for skill in match_result.get('missing_skills', [])[:15]:
            st.markdown(f"❌ {skill}")
        if not match_result.get('missing_skills'):
            st.success("No critical skills missing!")

    st.divider()

    # ── Recommendations ────────────────────────────────────────────────
    st.markdown("### 💡 Recommendations")
    for rec in match_result.get('recommendations', []):
        st.markdown(f"→ {rec}")

    # ── Experience match ───────────────────────────────────────────────
    req_exp = match_result.get('required_experience')
    if req_exp:
        cand_exp = match_result.get('candidate_experience', 0)
        exp_ok   = match_result.get('experience_match', False)
        if exp_ok:
            st.success(f"✅ Experience: You have {cand_exp} years — meets the {req_exp}+ year requirement.")
        else:
            st.warning(f"⚠️ Experience gap: Job needs {req_exp}+ years, you have {cand_exp} years.")