# pages/5_Interview_Prep.py
# Generates custom interview questions based on the resume and target role.

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import requests
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Interview Prep", page_icon="🎤", layout="wide")

st.markdown("# 🎤 Interview Question Generator")
st.markdown("Generate custom interview questions tailored to your skills and target role.")

api_key = os.getenv("GROQ_API_KEY", "")

with st.sidebar:
    st.markdown("### Settings")
    target_role = st.text_input("Target Role", value="Data Scientist")
    experience  = st.selectbox("Experience Level", ["Fresher", "1-3 years", "3-5 years", "5+ years"])
    num_qs      = st.slider("Number of Questions", 5, 20, 10)
    q_types     = st.multiselect(
        "Question Types",
        ["Technical", "Behavioral", "Situational", "System Design", "HR/Culture"],
        default=["Technical", "Behavioral", "HR/Culture"]
    )

col1, col2 = st.columns([1, 1])

with col1:
    skills_input = st.text_area(
        "Your Key Skills (one per line)",
        height=150,
        placeholder="Python\nMachine Learning\nSQL\nTensorFlow\nPandas",
    )

with col2:
    jd_input = st.text_area(
        "Job Description (optional)",
        height=150,
        placeholder="Paste job description for role-specific questions...",
    )

def generate_questions(role, exp, skills, num, types, jd):
    """Call Anthropic API to generate interview questions."""
    if not api_key or api_key == "your_api_key_here":
        return "Please add your GROQ_API_KEY to the .env file."

    skills_list = [s.strip() for s in skills.split('\n') if s.strip()]

    prompt = f"""Generate exactly {num} interview questions for a {exp} {role} candidate.

Skills: {', '.join(skills_list) if skills_list else 'Not specified'}
Question types needed: {', '.join(types)}
{f'Job Description context: {jd[:500]}' if jd else ''}

Format each question as:
**[TYPE] Q1:** [Question text]
**Expected Answer Focus:** [2-3 sentences on what a good answer covers]
**Difficulty:** [Easy/Medium/Hard]

---

Make questions realistic, role-specific, and increasingly challenging.
Include questions about specific skills mentioned."""

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000,
            },
            timeout=30,
        )

        data = resp.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Error: {e}"

if st.button("🎯 Generate Interview Questions", type="primary", use_container_width=True):
    if not target_role:
        st.warning("Please enter a target role.")
    else:
        with st.spinner("Generating personalized interview questions..."):
            questions = generate_questions(
                target_role, experience, skills_input,
                num_qs, q_types, jd_input
            )

        st.markdown("---")
        st.markdown("## 📋 Your Interview Questions")
        st.markdown(questions)

        st.download_button(
            "⬇️ Download Questions",
            data=questions,
            file_name=f"interview_questions_{target_role.replace(' ','_')}.txt",
            mime="text/plain",
        )