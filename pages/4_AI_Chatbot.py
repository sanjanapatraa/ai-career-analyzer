# pages/4_AI_Chatbot.py

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Career Advisor",
    page_icon="🤖",
    layout="wide"
)

# ─────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>

.chat-user {
    background:#e8f4fd;
    border-radius:12px;
    padding:12px 16px;
    margin:10px 0;
    border-left:4px solid #3498db;
    color:black;
}

.chat-bot {
    background:#f0fff4;
    border-radius:12px;
    padding:12px 16px;
    margin:10px 0;
    border-left:4px solid #2ecc71;
    color:black;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.title("🤖 AI Career Advisor")

st.markdown(
    "Ask your personal AI career coach anything about jobs, "
    "skills, resumes, interviews, or salaries."
)

# ─────────────────────────────────────────────────────────────
# LOAD API KEY
# ─────────────────────────────────────────────────────────────
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("""
    GROQ API KEY NOT FOUND

    Add this to your .env file:

    GROQ_API_KEY=your_key_here
    """)
    st.stop()

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:

    st.header("⚙️ Settings")

    advisor_mode = st.selectbox(
        "Advisor Mode",
        [
            "General Career Advice",
            "Resume Review",
            "Interview Prep",
            "Skill Gap Analysis",
            "Career Switch"
        ]
    )

    target_role = st.text_input(
        "Target Role",
        placeholder="e.g. Data Scientist"
    )

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ─────────────────────────────────────────────────────────────
# SYSTEM PROMPTS
# ─────────────────────────────────────────────────────────────
SYSTEM_PROMPTS = {
    "General Career Advice":
        "You are an expert AI career advisor helping students and professionals.",

    "Resume Review":
        "You are an ATS resume reviewer and recruiter.",

    "Interview Prep":
        "You are a technical interview coach.",

    "Skill Gap Analysis":
        "You help users identify missing skills and learning paths.",

    "Career Switch":
        "You help users transition into tech careers."
}

system_prompt = SYSTEM_PROMPTS.get(
    advisor_mode,
    SYSTEM_PROMPTS["General Career Advice"]
)

if target_role:
    system_prompt += f"\nThe user is targeting the role: {target_role}"

# ─────────────────────────────────────────────────────────────
# AI FUNCTION
# ─────────────────────────────────────────────────────────────
def get_ai_response(user_message):

    try:

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",

            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },

            json={
                "model": "llama-3.3-70b-versatile",

                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],

                "temperature": 0.7
            },

            timeout=30
        )

        # DEBUG
        print(response.status_code)
        print(response.text)

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ ERROR:\n{str(e)}"

# ─────────────────────────────────────────────────────────────
# DISPLAY CHAT
# ─────────────────────────────────────────────────────────────
st.markdown("---")

for message in st.session_state.messages:

    if message["role"] == "user":

        st.markdown(
            f"""
            <div class="chat-user">
            👤 <b>You:</b><br>
            {message['content']}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class="chat-bot">
            🤖 <b>Career Advisor:</b><br>
            {message['content']}
            </div>
            """,
            unsafe_allow_html=True
        )

# ─────────────────────────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask your career question...")

if user_input:

    # Store user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Generate response
    with st.spinner("Thinking..."):

        ai_response = get_ai_response(user_input)

    # Store AI response
    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_response
    })

    st.rerun()

# ─────────────────────────────────────────────────────────────
# EMPTY STATE
# ─────────────────────────────────────────────────────────────
if not st.session_state.messages:

    st.markdown("""
    <div style="text-align:center; padding:2rem; opacity:0.7;">

    <h3>🚀 Your AI Career Coach</h3>

    <p>
    Ask anything about:
    careers, resumes, interviews, salaries, or skills.
    </p>

    </div>
    """, unsafe_allow_html=True)