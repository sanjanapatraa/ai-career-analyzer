import streamlit as st

from src.job_matcher import match_resume_to_job
from ui.components import card_end, card_start, chip_row, close_shell, empty_state, insight_row, metric_card, page_header, progress_row, section_title


def show_jobmatch():
    result = st.session_state.get("analysis_result")
    page_header("Job Match", "Compare the latest analyzed candidate against a target job description.", "Matching")

    if not result:
        empty_state("No candidate loaded", "Analyze a resume first, then return here to compare it with any target role.", "Analyze Resume", "analyzer")
        close_shell()
        return

    resume = result.get("resume_data", {})
    skills = result.get("skills", [])
    default_jd = result.get("jd_text", "")

    card_start()
    section_title("Target Job Description", "Update the job description and rerun the match without re-uploading the resume.")
    jd_text = st.text_area("Job description", value=default_jd, height=220)
    if st.button("Update Match", type="primary"):
        if jd_text.strip():
            with st.spinner("Matching resume to job description..."):
                result["jd_text"] = jd_text
                result["match_result"] = match_resume_to_job(resume, jd_text, skills)
                st.session_state.analysis_result = result
                st.rerun()
        else:
            st.warning("Paste a job description before running match analysis.")
    card_end()

    match = result.get("match_result") or {}
    m1, m2, m3 = st.columns(3)
    with m1:
        metric_card("Overall Match", f"{match.get('overall_score', 0):.0f}%" if match else "N/A", match.get("match_label", "No JD supplied"), "green")
    with m2:
        metric_card("Skill Match", f"{match.get('skill_match_score', 0):.0f}%" if match else "N/A", "Required skills coverage", "blue")
    with m3:
        metric_card("Experience", "Pass" if match.get("experience_match") else "Review", f"Required: {match.get('required_experience', 'N/A')} yrs", "amber")

    left, right = st.columns(2, gap="large")
    with left:
        card_start()
        section_title("Matched Skills", "Skills found in both the resume and job description.")
        chip_row(match.get("matched_skills", []), "good", "Run a JD match to see shared skills.")
        card_end()
    with right:
        card_start()
        section_title("Missing Skills", "Required skills absent from the current resume.")
        chip_row(match.get("missing_skills", []), "red", "No gaps detected yet.")
        card_end()

    card_start()
    section_title("Recommendations", "Job-specific improvements from the matching engine.")
    for idx, rec in enumerate(match.get("recommendations", [])[:6], 1):
        insight_row(f"Recommendation {idx}", rec, "Match")
    if not match.get("recommendations"):
        st.info("Paste a job description and update the match to generate recommendations.")
    card_end()

    close_shell()
