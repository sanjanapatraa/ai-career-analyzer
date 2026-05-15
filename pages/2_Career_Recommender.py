# pages/2_Career_Recommender.py
# Career recommendation page with ML predictions and roadmap display.

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Career Recommender", page_icon="🎯", layout="wide")

st.markdown("""
<style>
.career-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px; padding: 1.5rem; color: white; margin: 1rem 0;
}
.roadmap-step {
    background: var(--background-color, #f8f9fa);
    border: 1px solid #e0e0e0; border-radius: 10px;
    padding: 1rem; margin: 0.5rem 0;
    border-left: 4px solid #667eea;
}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🎯 Career Recommender")
st.markdown("Enter your skills and experience to get ML-powered career recommendations.")
st.divider()

# ── Input section ─────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Your Skills")
    skills_input = st.text_area(
        "Enter your skills (comma-separated or one per line)",
        height=180,
        placeholder="Python, Machine Learning, SQL, TensorFlow, Docker, AWS...",
        value="Python, Machine Learning, SQL, Pandas, TensorFlow, Git, Docker"
    )
    experience_years = st.slider("Years of Experience", 0, 20, 3)

with col2:
    st.markdown("### Your Background")
    education = st.selectbox(
        "Highest Education",
        ["High School", "Diploma", "B.Tech/B.E.", "B.Sc./BCA/BBA",
         "M.Tech/M.E.", "MBA", "M.Sc./MCA", "PhD"]
    )
    current_role = st.text_input(
        "Current Role (optional)",
        placeholder="e.g., Software Engineer, Fresher, Data Analyst"
    )
    resume_text_input = st.text_area(
        "Or paste your resume text (optional — for better accuracy)",
        height=100,
        placeholder="Paste resume text here for ML-based prediction..."
    )

if st.button("🚀 Get Career Recommendations", type="primary", use_container_width=True):

    # Parse skills from input
    if ',' in skills_input:
        user_skills = [s.strip() for s in skills_input.split(',') if s.strip()]
    else:
        user_skills = [s.strip() for s in skills_input.split('\n') if s.strip()]

    if not user_skills:
        st.warning("Please enter at least a few skills.")
        st.stop()

    with st.spinner("Analyzing your profile with ML models..."):

        # Try ML model prediction
        ml_predictions = []
        try:
            from src.career_recommender import CareerRecommender
            from src.data_pipeline import preprocess_text

            recommender   = CareerRecommender()
            resume_text   = resume_text_input if resume_text_input else \
                            f"Skills: {', '.join(user_skills)}\n" \
                            f"Experience: {experience_years} years\n" \
                            f"Education: {education}"
            cleaned_text  = preprocess_text(resume_text)
            ml_predictions = recommender.predict_top_n(cleaned_text, n=5)

        except Exception as e:
            st.info(f"ML model not trained yet (run Phase 5 training). "
                    f"Showing rule-based recommendations.")

        # Rule-based fallback
        if not ml_predictions:
            skills_lower = {s.lower() for s in user_skills}

            career_scores = {
                "Data Scientist":           len(skills_lower & {'python','machine learning','sql','tensorflow','statistics','pandas','deep learning'}),
                "Machine Learning Engineer": len(skills_lower & {'python','tensorflow','pytorch','mlops','docker','kubernetes','deep learning'}),
                "Software Engineer":        len(skills_lower & {'java','python','c++','algorithms','system design','git','rest api'}),
                "Data Analyst":             len(skills_lower & {'sql','excel','tableau','power bi','python','statistics','r'}),
                "Frontend Developer":       len(skills_lower & {'html','css','javascript','react','typescript','vue','figma'}),
                "Backend Developer":        len(skills_lower & {'python','java','node.js','django','flask','postgresql','mongodb'}),
                "DevOps Engineer":          len(skills_lower & {'docker','kubernetes','aws','terraform','ci/cd','linux','jenkins'}),
                "Cybersecurity Analyst":    len(skills_lower & {'network security','penetration testing','linux','python','firewalls','siem'}),
                "Cloud Architect":          len(skills_lower & {'aws','azure','gcp','terraform','kubernetes','cloud','docker'}),
                "Product Manager":          len(skills_lower & {'product management','agile','jira','sql','communication','analytics'}),
            }

            sorted_careers = sorted(career_scores.items(), key=lambda x: x[1], reverse=True)
            total = sum(s for _, s in sorted_careers[:5]) or 1

            ml_predictions = [
                {
                    'rank':       i + 1,
                    'career':     career,
                    'confidence': round((score / total) * 100, 1)
                }
                for i, (career, score) in enumerate(sorted_careers[:5])
                if score > 0
            ]

            if not ml_predictions:
                ml_predictions = [{'rank': 1, 'career': 'Software Engineer', 'confidence': 60.0}]

    # ── Display Results ────────────────────────────────────────────────
    st.divider()
    st.markdown("## 🏆 Your Career Recommendations")

    top = ml_predictions[0]

    # Top recommendation card
    st.markdown(f"""
    <div class="career-card">
        <h2 style="margin:0; color:white;">🥇 Best Match: {top['career']}</h2>
        <p style="margin:0.5rem 0 0; font-size:1.1rem; opacity:0.9;">
            Confidence Score: {top['confidence']:.0f}%
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Bar chart of all predictions
    if len(ml_predictions) > 1:
        fig = go.Figure(go.Bar(
            x=[p['confidence'] for p in ml_predictions],
            y=[p['career']      for p in ml_predictions],
            orientation='h',
            marker=dict(
                color=[p['confidence'] for p in ml_predictions],
                colorscale='Viridis',
            ),
            text=[f"{p['confidence']:.0f}%" for p in ml_predictions],
            textposition='outside',
        ))
        fig.update_layout(
            title="Career Match Scores",
            xaxis_title="Confidence %",
            height=300,
            margin=dict(t=40, b=20, l=20, r=60),
            xaxis=dict(range=[0, 110]),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Career Details + Roadmap ───────────────────────────────────────
    st.markdown(f"## 📍 Roadmap for {top['career']}")

    try:
        from src.career_recommender import CareerRecommender
        recommender = CareerRecommender()
        career_info = recommender.get_career_skill_requirements(top['career'])
    except Exception:
        career_info = {
            'core_skills':   user_skills[:6],
            'tools':         ['VS Code', 'Git', 'GitHub'],
            'learning_path': ['Build fundamentals', 'Work on projects', 'Get certified'],
            'avg_salary_inr': 'Varies by experience',
            'growth':         'Research the role',
            'companies':      ['Many options available'],
        }

    info_col, roadmap_col = st.columns(2)

    with info_col:
        st.markdown("### 📊 Role Information")
        st.metric("Average Salary (India)", career_info.get('avg_salary_inr', 'N/A'))
        st.metric("Market Growth",           career_info.get('growth', 'N/A'))

        st.markdown("**Core Skills Required:**")
        for skill in career_info.get('core_skills', []):
            in_yours = skill.lower() in {s.lower() for s in user_skills}
            icon = "✅" if in_yours else "❌"
            st.markdown(f"{icon} {skill}")

        st.markdown("**Top Hiring Companies:**")
        st.markdown(", ".join(career_info.get('companies', [])))

    with roadmap_col:
        st.markdown("### 🗺️ Learning Roadmap")
        steps = career_info.get('learning_path', [])
        for i, step in enumerate(steps, 1):
            st.markdown(f"""
            <div class="roadmap-step">
                <strong>Step {i}:</strong> {step}
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ── Skill Gap for top career ───────────────────────────────────────
    st.markdown("### 🔍 Your Skill Gap Analysis")
    required = set(s.lower() for s in career_info.get('core_skills', []))
    have     = set(s.lower() for s in user_skills)
    missing  = required - have
    present  = required & have

    g1, g2 = st.columns(2)
    with g1:
        st.markdown(f"**✅ Skills you already have ({len(present)}):**")
        for s in present:
            st.markdown(f"- {s.title()}")
    with g2:
        st.markdown(f"**📚 Skills to learn ({len(missing)}):**")
        for s in missing:
            st.markdown(f"- {s.title()}")

    if missing:
        st.info(f"💡 Focus on learning: **{', '.join(list(missing)[:3])}** to strengthen your profile.")