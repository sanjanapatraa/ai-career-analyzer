import streamlit as st

from ui.components import card_end, card_start, chip_row, close_shell, empty_state, metric_card, page_header, progress_row, section_title


def show_career():
    result = st.session_state.get("analysis_result")
    page_header("Career Match", "Ranked career recommendations, confidence signals, and role-readiness guidance.", "Career")

    if not result:
        empty_state("No analysis available", "Run a resume analysis first so career recommendations can use real candidate data.", "Analyze Resume", "analyzer")
        close_shell()
        return

    career = result.get("career_result", {})
    top_careers = result.get("top_careers") or []
    skills = result.get("skills", [])

    m1, m2, m3 = st.columns(3)
    with m1:
        metric_card("Best Role", career.get("career", "Unknown"), f"{career.get('confidence', 0):.0f}% confidence", "green")
    with m2:
        metric_card("Career Options", str(len(top_careers) or 1), "Ranked by model confidence", "blue")
    with m3:
        metric_card("Skill Signals", str(len(skills)), "Detected from resume", "indigo")

    left, right = st.columns([.58, .42], gap="large")
    with left:
        card_start()
        section_title("Recommended Career Paths", "Top model outputs where trained artifacts are available.")
        if top_careers:
            for item in top_careers:
                progress_row(item.get("career", "Career"), item.get("confidence", 0), "green")
        else:
            progress_row(career.get("career", "Model unavailable"), career.get("confidence", 0), "amber")
        card_end()

    with right:
        card_start()
        section_title("Transferable Skills", "Current strengths that support the recommended roles.")
        chip_row(skills[:24], "blue")
        card_end()

    close_shell()
