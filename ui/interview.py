import streamlit as st

from ui.components import card_end, card_start, close_shell, empty_state, insight_row, metric_card, page_header, section_title


def show_interview():
    result = st.session_state.get("analysis_result")
    page_header("Interview Prep", "Role-specific interview focus areas based on the analyzed resume.", "Prep")

    if not result:
        empty_state("No candidate context", "Analyze a resume first to generate tailored interview prep.", "Analyze Resume", "analyzer")
        close_shell()
        return

    career = result.get("career_result", {}).get("career", "Target role")
    score = result.get("ats_result", {}).get("overall_score", 0)

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Target Role", career, "Predicted fit", "blue")
    with c2:
        metric_card("ATS Readiness", f"{score:.0f}%", "Resume quality", "green")
    with c3:
        metric_card("Prep Tracks", "5", "Behavioral and technical", "indigo")

    card_start()
    section_title("Question Plan", "Use these prompts to evaluate depth, clarity, and role fit.")
    questions = [
        ("Technical depth", "Walk through a project where you used your strongest technical skills to solve a business problem."),
        ("Impact", "Describe a measurable improvement you delivered and how you tracked success."),
        ("Ownership", "Tell me about a time you made a decision with incomplete information."),
        ("Collaboration", "How have you handled disagreement with a stakeholder or teammate?"),
        ("Growth", "Which missing skill are you actively improving and what is your plan?"),
    ]
    for title, body in questions:
        insight_row(title, body, "Interview")
    card_end()

    close_shell()
