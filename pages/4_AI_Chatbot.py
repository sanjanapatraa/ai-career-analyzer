# pages/4_AI_Chatbot.py
# ══════════════════════════════════════════════════════════════════════════
# AI CAREER CHATBOT PAGE
# Powered by the Anthropic API — gives users a personal AI career advisor.
# ══════════════════════════════════════════════════════════════════════════

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import requests
import json
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Career Advisor", page_icon="🤖", layout="wide")

st.markdown("""
<style>
.chat-user { background:#e8f4fd; border-radius:12px; padding:12px 16px;
            margin:8px 0; border-left:4px solid #3498db; }
.chat-bot  { background:#f0fff4; border-radius:12px; padding:12px 16px;
            margin:8px 0; border-left:4px solid #2ecc71; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🤖 AI Career Advisor")
st.markdown("Ask your personal AI career coach anything about jobs, skills, resumes, or interviews.")

# ── API Key check ──────────────────────────────────────────────────────────
api_key = os.getenv("GROQ_API_KEY", "")
if not api_key or api_key == "your_api_key_here":
    st.warning("""
    **API Key Required**
    Add your Groq API key to the `.env` file:Get a free key at: https://console.groq.com
    """)
    st.stop()

# ── Chat history (stored in session state) ─────────────────────────────────
# st.session_state persists across reruns within the same browser session
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# ── Sidebar: Chatbot settings ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 Chat Context")
    chat_mode = st.selectbox(
        "Advisor Mode",
        ["General Career Advice", "Resume Review", "Interview Prep",
        "Skill Gap Analysis", "Salary Negotiation", "Career Switch"],
    )

    user_role = st.text_input(
        "Your target job role",
        placeholder="e.g., Data Scientist, SWE at Google"
    )

    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_messages = []
        st.rerun()

    # ── Quick prompt buttons ───────────────────────────────────────────
    st.markdown("**Quick Questions:**")
    quick_prompts = [
        "What skills should I learn for Data Science in 2025?",
        "How do I negotiate my salary?",
        "What are the most common interview mistakes?",
        "How do I switch from IT to ML?",
        "Review my resume for a Software Engineer role",
    ]
    for prompt in quick_prompts:
        if st.button(prompt[:45] + "...", use_container_width=True):
            st.session_state.pending_prompt = prompt

# ── Build system prompt based on mode ─────────────────────────────────────
SYSTEM_PROMPTS = {
    "General Career Advice": (
        "You are an expert career counselor for software and data professionals in India. "
        "Give practical, actionable advice. Be encouraging but honest. "
        "Focus on the Indian tech job market (Bengaluru, Hyderabad, Pune, remote). "
        "Mention real companies, realistic salaries in LPA, and actual skill requirements."
    ),
    "Resume Review": (
        "You are a professional resume writer and ATS expert. "
        "Help users improve their resumes. Point out specific weaknesses and give "
        "concrete rewrite suggestions. Know ATS best practices."
    ),
    "Interview Prep": (
        "You are an interview coach. Help candidates prepare for technical and behavioral interviews. "
        "Give example questions and ideal answer frameworks (STAR method). "
        "Be specific to their target role."
    ),
    "Skill Gap Analysis": (
        "You are a learning path advisor. Analyze skill gaps and recommend specific courses, "
        "certifications, and projects. Give realistic timelines and free/paid resource recommendations."
    ),
    "Salary Negotiation": (
        "You are a salary negotiation expert familiar with Indian tech market rates. "
        "Give data-driven advice on negotiation strategies and realistic salary ranges by role and experience."
    ),
    "Career Switch": (
        "You are a career transition coach. Help people switching careers into tech. "
        "Give honest timelines, required upskilling, and realistic expectations."
    ),
}

system_prompt = SYSTEM_PROMPTS.get(chat_mode, SYSTEM_PROMPTS["General Career Advice"])
if user_role:
    system_prompt += f"\n\nThe user is targeting the role of: {user_role}. Keep advice relevant to this role."


def get_ai_response(user_message: str, history: list) -> str:
    """
    Call the Anthropic API to get a response.

    Args:
        user_message: Latest user message
        history:      List of past messages [{'role': ..., 'content': ...}]

    Returns:
        AI response text
    """
    headers = {
        "Content-Type": "application/json",
        "x-api-key":    api_key,
        "anthropic-version": "2023-06-01",
    }

    # Build message history (include last 10 messages for context)
    messages = history[-10:] + [{"role": "user", "content": user_message}]

    body = {
        "model":      "claude-sonnet-4-20250514",
        "max_tokens": 1024,
        "system":     system_prompt,
        "messages":   messages,
    }

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=body,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()['content'][0]['text']
    except requests.exceptions.Timeout:
        return "Response timed out. Please try again."
    except Exception as e:
        return f"Error: {e}. Check your API key and internet connection."


# ── Display chat history ───────────────────────────────────────────────────
st.markdown("---")
chat_container = st.container()

with chat_container:
    for msg in st.session_state.chat_messages:
        if msg['role'] == 'user':
            st.markdown(
                f"<div class='chat-user'>👤 <b>You:</b><br>{msg['content']}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='chat-bot'>🤖 <b>Career Advisor:</b><br>{msg['content']}</div>",
                unsafe_allow_html=True
            )

# ── Handle pending quick prompt ────────────────────────────────────────────
if 'pending_prompt' in st.session_state:
    pending = st.session_state.pop('pending_prompt')
    st.session_state.chat_messages.append({'role': 'user', 'content': pending})
    with st.spinner("Thinking..."):
        reply = get_ai_response(pending, st.session_state.chat_messages[:-1])
    st.session_state.chat_messages.append({'role': 'assistant', 'content': reply})
    st.rerun()

# ── Chat input ─────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask your career question...")

if user_input:
    st.session_state.chat_messages.append({'role': 'user', 'content': user_input})

    with st.spinner("Career Advisor is thinking..."):
        response = get_ai_response(
            user_input,
            [m for m in st.session_state.chat_messages if m['role'] != 'user' or
            m != st.session_state.chat_messages[-1]]
        )

    st.session_state.chat_messages.append({'role': 'assistant', 'content': response})
    st.rerun()

# ── Empty state ────────────────────────────────────────────────────────────
if not st.session_state.chat_messages:
    st.markdown("""
    <div style="text-align:center; padding: 2rem; opacity: 0.6;">
        <h3>Your personal AI Career Advisor</h3>
        <p>Ask anything about careers, skills, resumes, interviews, or salaries</p>
        <p>Try the quick questions in the sidebar →</p>
    </div>
    """, unsafe_allow_html=True)