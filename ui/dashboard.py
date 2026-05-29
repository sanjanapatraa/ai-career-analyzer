import pandas as pd
import streamlit as st

from ui.charts import donut_chart, gauge_chart, hbar_chart, line_chart, radar_chart
from ui.components import (
    card_end,
    card_start,
    chip_row,
    close_shell,
    empty_state,
    insight_row,
    metric_card,
    page_header,
    progress_row,
    section_title,
)


def _component_label(name: str) -> str:
    return name.replace("_", " ").title()


def show_dashboard():
    result = st.session_state.get("analysis_result")
    page_header(
        "ATS Dashboard",
        "A recruiter-style command center for the latest resume analysis, match quality, skill gaps, and next actions.",
        "Overview",
    )

    if not result:
        empty_state(
            "No resume analysis available",
            "Start with the Resume Analyzer to generate a live ATS score and populate this dashboard.",
            "Open Resume Analyzer",
            "analyzer",
        )
        close_shell()
        return

    resume = result.get("resume_data", {})
    skills_result = result.get("skills_result", {})
    ats = result.get("ats_result", {})
    match = result.get("match_result") or {}
    components = ats.get("component_scores", {})
    skills = skills_result.get("all_skills", [])
    missing = ats.get("missing_skills", [])

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("ATS Score", f"{ats.get('overall_score', 0):.0f}%", ats.get("label", "Candidate score"), "green")
    with m2:
        metric_card("Skills Found", str(skills_result.get("total_count", len(skills))), "Extracted from resume", "blue")
    with m3:
        metric_card("Experience", f"{resume.get('experience_years', 0)} yrs", result.get("target_level", "mid").title(), "indigo")
    with m4:
        metric_card("Job Match", f"{match.get('overall_score', 0):.0f}%" if match else "N/A", match.get("match_label", "No JD supplied"), "amber")

    left, right = st.columns([.58, .42], gap="large")
    with left:
        card_start()
        section_title("Score Breakdown", "Weighted ATS components used by the backend scorer.")
        if components:
            labels = [_component_label(k) for k in components.keys()]
            values = list(components.values())
            st.plotly_chart(radar_chart(labels, values), use_container_width=True)
            st.plotly_chart(hbar_chart(labels, values, "Component Scores"), use_container_width=True)
        card_end()

        card_start()
        section_title("Candidate Skills", "Detected technical and soft skills.")
        chip_row(skills[:36], "blue", "No skills detected.")
        card_end()

    with right:
        card_start()
        section_title("ATS Gauge", "Reference line is the common recruiter shortlist threshold.")
        st.plotly_chart(gauge_chart(ats.get("overall_score", 0)), use_container_width=True)
        card_end()

        card_start()
        section_title("Pipeline Forecast", "Illustrative recruiter workflow metrics for this candidate.")
        st.plotly_chart(line_chart(["Parse", "Screen", "Match", "Shortlist", "Interview"], [72, ats.get("overall_score", 0), match.get("overall_score", 68), 76, 81], "Candidate Momentum"), use_container_width=True)
        card_end()

    lower1, lower2, lower3 = st.columns([.34, .33, .33], gap="large")
    with lower1:
        card_start()
        section_title("Recruiter Decision", "Recommended decision cues.")
        progress_row("ATS Quality", ats.get("overall_score", 0), "green")
        progress_row("Keyword Coverage", components.get("keyword_density", 0), "blue")
        progress_row("Format Quality", components.get("format_quality", 0), "indigo")
        progress_row("Contact Completeness", components.get("contact_info", 0), "amber")
        card_end()

    with lower2:
        card_start()
        section_title("Missing Skills", "Highest-priority gaps from the ATS engine.")
        chip_row(missing[:18], "red", "No missing skills detected from the current target.")
        card_end()

    with lower3:
        card_start()
        section_title("Next Actions", "Concrete improvements generated from the scoring result.")
        actions = ats.get("improvements") or ats.get("feedback") or ["Tailor the summary to the target role.", "Add measurable business outcomes."]
        for idx, action in enumerate(actions[:5], start=1):
            insight_row(f"Action {idx}", action, "Priority")
        card_end()

    card_start()
    section_title("Candidate Snapshot", "Structured resume information extracted by the backend parser.")
    rows = [
        {"Field": "Name", "Value": resume.get("name", "Not detected")},
        {"Field": "Email", "Value": resume.get("email", "Not detected")},
        {"Field": "Phone", "Value": resume.get("phone", "Not detected")},
        {"Field": "Pages", "Value": resume.get("page_count", "N/A")},
        {"Field": "Word Count", "Value": resume.get("word_count", "N/A")},
        {"Field": "Sections", "Value": ", ".join(resume.get("sections", {}).keys()) or "Not detected"},
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    card_end()

    close_shell()
