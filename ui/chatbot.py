import streamlit as st

from ui.components import card_end, card_start, close_shell, empty_state, insight_row, page_header, section_title


def _coach_response(question: str, result: dict) -> str:
    ats = result.get("ats_result", {})
    skills = result.get("skills", [])
    missing = ats.get("missing_skills", [])
    score = ats.get("overall_score", 0)
    if not question.strip():
        return "Ask about resume improvements, missing skills, job fit, or interview preparation."
    if "skill" in question.lower():
        if missing:
            return f"Prioritize these gaps first: {', '.join(missing[:6])}. Then add evidence for your strongest existing skills: {', '.join(skills[:6])}."
        return f"Your strongest visible skill signals are {', '.join(skills[:8])}. Keep them tied to measurable outcomes."
    if "score" in question.lower() or "ats" in question.lower():
        return f"Your ATS score is {score:.0f}%. The fastest lift usually comes from keyword alignment, quantified achievements, and clean section headers."
    if "interview" in question.lower():
        return "Prepare one story each for impact, conflict, technical depth, ownership, and learning. Keep answers structured around context, action, and measurable result."
    return "Focus on role alignment: mirror the job description language, make achievements measurable, and keep the top third of the resume dense with the target title, core skills, and business impact."


def show_chatbot():
    result = st.session_state.get("analysis_result")
    page_header("AI Career Coach", "A focused coaching workspace using the latest resume analysis as context.", "Coach")

    if not result:
        empty_state("No analysis context", "Run the resume analyzer first so the coach can reference real ATS signals.", "Analyze Resume", "analyzer")
        close_shell()
        return

    card_start()
    section_title("Ask the Coach", "Responses are grounded in the current session analysis.")
    question = st.text_input("Question", placeholder="How can I improve my ATS score?")
    if st.button("Send", type="primary"):
        answer = _coach_response(question, result)
        st.session_state.chat_history.append({"question": question, "answer": answer})
        st.rerun()
    card_end()

    card_start()
    section_title("Conversation", "Latest coaching guidance.")
    for item in reversed(st.session_state.get("chat_history", [])[-8:]):
        insight_row(item["question"], item["answer"], "Coach")
    if not st.session_state.get("chat_history"):
        st.info("Ask a question to begin.")
    card_end()

    close_shell()
