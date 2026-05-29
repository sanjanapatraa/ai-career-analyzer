import streamlit as st

from ui.components import card_end, card_start, chip_row, close_shell, empty_state, insight_row, metric_card, page_header, section_title


def show_roadmap():
    result = st.session_state.get("analysis_result")
    page_header("Learning Roadmap", "A prioritized growth plan from resume gaps and target-role signals.", "Roadmap")

    if not result:
        empty_state("No roadmap yet", "Run a resume analysis with a target job description to generate a stronger roadmap.", "Analyze Resume", "analyzer")
        close_shell()
        return

    missing = result.get("ats_result", {}).get("missing_skills", [])
    skills = result.get("skills", [])

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Priority Gaps", str(len(missing)), "From ATS scorer", "amber")
    with c2:
        metric_card("Current Skills", str(len(skills)), "Resume signals", "blue")
    with c3:
        metric_card("Plan Horizon", "30 days", "Focused sprint", "green")

    card_start()
    section_title("30-Day Plan", "Keep the plan small, demonstrable, and tied to portfolio evidence.")
    focus = missing[:5] or ["quantified achievements", "job keywords", "project outcomes"]
    for idx, skill in enumerate(focus, 1):
        insight_row(f"Week {idx}", f"Build proof for {skill}: one project update, one resume bullet, and one interview story.", "Plan")
    card_end()

    card_start()
    section_title("Existing Strengths", "Use these as anchors while closing gaps.")
    chip_row(skills[:30], "blue")
    card_end()

    close_shell()
