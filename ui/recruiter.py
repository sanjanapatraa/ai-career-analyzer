import pandas as pd
import streamlit as st

from ui.charts import donut_chart
from ui.components import card_end, card_start, close_shell, empty_state, metric_card, page_header, section_title


def show_recruiter():
    result = st.session_state.get("analysis_result")
    page_header("Recruiter Analytics", "Shortlist-ready candidate intelligence for hiring teams.", "Recruiter")

    if not result:
        empty_state("No candidate in pipeline", "Analyze a resume to populate recruiter analytics.", "Analyze Resume", "analyzer")
        close_shell()
        return

    ats = result.get("ats_result", {})
    match = result.get("match_result") or {}
    resume = result.get("resume_data", {})

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Shortlist Score", f"{ats.get('overall_score', 0):.0f}%", ats.get("grade", "N/A"), "green")
    with c2:
        metric_card("Job Match", f"{match.get('overall_score', 0):.0f}%" if match else "N/A", match.get("match_label", "No JD"), "blue")
    with c3:
        metric_card("Experience", f"{resume.get('experience_years', 0)} yrs", "Detected", "indigo")
    with c4:
        metric_card("Missing Skills", str(len(ats.get("missing_skills", []))), "Target gaps", "amber")

    left, right = st.columns([.52, .48], gap="large")
    with left:
        card_start()
        section_title("Hiring Funnel", "Professional recruiter dashboard visualization.")
        st.plotly_chart(donut_chart(["Screened", "Matched", "Shortlisted", "Interview"], [42, 28, 18, 12], "Pipeline Distribution"), use_container_width=True)
        card_end()
    with right:
        card_start()
        section_title("Candidate Table", "Structured snapshot for review.")
        data = pd.DataFrame(
            [
                {
                    "Candidate": resume.get("name", "Candidate"),
                    "ATS Score": ats.get("overall_score", 0),
                    "Grade": ats.get("grade", "N/A"),
                    "Experience": resume.get("experience_years", 0),
                    "Recommendation": "Shortlist" if ats.get("overall_score", 0) >= 75 else "Review",
                }
            ]
        )
        st.dataframe(data, use_container_width=True, hide_index=True)
        card_end()

    close_shell()
