import os

import streamlit as st

from src.ats_scorer import calculate_ats_score
from src.job_matcher import extract_required_skills_from_jd, match_resume_to_job
from src.resume_parser import parse_resume, parse_resume_from_text
from src.skill_extractor import extract_skills
from ui.charts import donut_chart, gauge_chart, radar_chart
from ui.components import (
    card_end,
    card_start,
    chip_row,
    close_shell,
    empty_state,
    metric_card,
    page_header,
    progress_row,
    section_title,
)


def _load_sample_resume():
    sample_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "sample_resumes",
        "data_scientist_john_smith.txt",
    )
    if not os.path.exists(sample_path):
        return None
    with open(sample_path, encoding="utf-8") as handle:
        return parse_resume_from_text(handle.read())


def _run_analysis(resume_data, jd_text, target_level, education_req):
    if not resume_data or resume_data.get("error"):
        return {"error": resume_data.get("error", "Unable to parse resume")}

    skills_result = extract_skills(resume_data["raw_text"], resume_data.get("sections"))
    resume_skills = skills_result.get("all_skills", [])
    jd_skills = extract_required_skills_from_jd(jd_text) if jd_text else []

    ats_result = calculate_ats_score(
        resume_data=resume_data,
        resume_skills=resume_skills,
        job_description=jd_text or None,
        job_skills=jd_skills,
        target_level=target_level,
        required_education=education_req,
    )

    match_result = None
    if jd_text:
        match_result = match_resume_to_job(resume_data, jd_text, resume_skills)

    top_careers = []
    career_result = {"career": "Model unavailable", "confidence": 0}
    try:
        from src.career_recommender import CareerRecommender

        recommender = CareerRecommender()
        career_result = recommender.predict(resume_data["raw_text"], resume_data)
        top_careers = recommender.predict_top_n(resume_data["raw_text"], resume_data, n=5)
    except Exception as exc:
        career_result = {"career": "Model unavailable", "confidence": 0, "error": str(exc)}

    return {
        "resume_data": resume_data,
        "skills_result": skills_result,
        "ats_result": ats_result,
        "match_result": match_result,
        "career_result": career_result,
        "top_careers": top_careers,
        "jd_text": jd_text,
        "target_level": target_level,
        "education_req": education_req,
        "score": ats_result.get("overall_score", 0),
        "skills": resume_skills,
    }


def show_analyzer():
    page_header(
        "Resume Analyzer",
        "Upload a resume, select target requirements, and run the existing ATS engine through a production-grade workflow.",
        "Intake",
    )

    left, right = st.columns([1.25, .75], gap="large")

    with left:
        card_start()
        section_title("Candidate Intake", "Upload a PDF resume or use the bundled sample profile for a fast demo.")
        uploaded_file = st.file_uploader("Resume PDF", type=["pdf"], help="Upload a text-based PDF resume.")
        use_sample = st.checkbox("Use sample resume", value=False)
        st.session_state.target_level = st.selectbox(
            "Target experience level",
            ["entry", "mid", "senior", "lead"],
            index=["entry", "mid", "senior", "lead"].index(st.session_state.get("target_level", "mid")),
        )
        st.session_state.education_req = st.selectbox(
            "Required education",
            ["any", "diploma", "bachelor", "master", "phd"],
            index=["any", "diploma", "bachelor", "master", "phd"].index(st.session_state.get("education_req", "bachelor")),
        )
        card_end()

        card_start()
        section_title("Target Role", "Paste a job description to unlock keyword, skill, and job-fit scoring.")
        jd_text = st.text_area(
            "Job description",
            value=st.session_state.get("jd_text", ""),
            height=220,
            placeholder="Paste the full target job description here.",
        )
        st.session_state.jd_text = jd_text
        card_end()

        if st.button("Run ATS Analysis", type="primary", use_container_width=True):
            if not uploaded_file and not use_sample:
                st.warning("Upload a resume PDF or enable the sample resume option.")
            else:
                with st.spinner("Parsing resume and running ATS scoring..."):
                    resume_data = _load_sample_resume() if use_sample else parse_resume(uploaded_file.read())
                    result = _run_analysis(
                        resume_data,
                        jd_text,
                        st.session_state.target_level,
                        st.session_state.education_req,
                    )
                    if result.get("error"):
                        st.error(result["error"])
                    else:
                        st.session_state.analysis_result = result
                        st.session_state.page = "dashboard"
                        st.rerun()

    with right:
        card_start("panel-muted")
        section_title("Analysis Coverage", "Signals included in the scoring workflow.")
        progress_row("ATS parsing readiness", 96, "green")
        progress_row("Keyword alignment", 88, "blue")
        progress_row("Skill extraction", 92, "indigo")
        progress_row("Recruiter scan quality", 84, "amber")
        card_end()

        card_start()
        section_title("Current Result", "Latest analysis stored in session.")
        result = st.session_state.get("analysis_result")
        if result:
            ats = result.get("ats_result", {})
            r1, r2 = st.columns(2)
            with r1:
                metric_card("ATS Score", f"{ats.get('overall_score', 0):.0f}%", ats.get("label", "Resume score"), "green")
            with r2:
                metric_card("Skills", str(len(result.get("skills", []))), "Detected keywords", "blue")
            st.plotly_chart(gauge_chart(ats.get("overall_score", 0)), use_container_width=True)
        else:
            empty_state("No analysis yet", "Run the analyzer to populate ATS score, resume skills, and recruiter insights.")
        card_end()

        card_start()
        section_title("Platform Signals", "The charts below use the same visual system as the dashboard.")
        st.plotly_chart(donut_chart(["Parsing", "Skills", "Keywords", "Format"], [28, 32, 24, 16], "Analysis Mix"), use_container_width=True)
        st.plotly_chart(
            radar_chart(["Skills", "Keywords", "Format", "Experience", "Education"], [88, 76, 84, 72, 80]),
            use_container_width=True,
        )
        card_end()

    close_shell()
