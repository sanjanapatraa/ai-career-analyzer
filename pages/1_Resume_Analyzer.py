# pages/1_Resume_Analyzer.py
# ══════════════════════════════════════════════════════════════════════════
# RESUME ANALYZER PAGE
# The main page where users upload their resume and get full analysis.
# ══════════════════════════════════════════════════════════════════════════

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io

from src.resume_parser    import parse_resume, parse_resume_from_text
from src.skill_extractor  import extract_skills
from src.ats_scorer       import calculate_ats_score
from src.report_generator import generate_report

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(page_title="Resume Analyzer", page_icon="📄", layout="wide")

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.score-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px; padding: 2rem; text-align: center;
    color: white; margin: 1rem 0;
}
.score-number { font-size: 4rem; font-weight: 700; line-height: 1; }
.score-label  { font-size: 1.1rem; opacity: 0.9; margin-top: 0.5rem; }
.metric-card  {
    background: white; border-radius: 12px; padding: 1.2rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin: 0.5rem 0;
    border-left: 4px solid #667eea;
}
.skill-badge {
    display: inline-block; background: #f0f4ff; color: #667eea;
    border: 1px solid #667eea; border-radius: 20px;
    padding: 3px 12px; margin: 3px; font-size: 0.85rem;
}
.missing-badge {
    display: inline-block; background: #fff0f0; color: #e74c3c;
    border: 1px solid #e74c3c; border-radius: 20px;
    padding: 3px 12px; margin: 3px; font-size: 0.85rem;
}
.strength-item { color: #27ae60; padding: 4px 0; }
.improvement-item { color: #e67e22; padding: 4px 0; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

def create_ats_gauge(score: float) -> go.Figure:
    """
    Create a beautiful gauge chart for the ATS score.
    Gauge charts look professional and convey score intuitively.
    """
    # Determine color based on score
    if score >= 75:
        color = '#2ecc71'
    elif score >= 55:
        color = '#3498db'
    elif score >= 40:
        color = '#f39c12'
    else:
        color = '#e74c3c'

    fig = go.Figure(go.Indicator(
        mode    = "gauge+number+delta",
        value   = score,
        domain  = {'x': [0, 1], 'y': [0, 1]},
        title   = {'text': "ATS Score", 'font': {'size': 18}},
        delta   = {'reference': 70, 'increasing': {'color': '#2ecc71'}},
        gauge   = {
            'axis':       {'range': [0, 100], 'tickwidth': 1},
            'bar':        {'color': color},
            'bgcolor':    "white",
            'borderwidth': 2,
            'steps': [
                {'range': [0,  40],  'color': '#fadbd8'},
                {'range': [40, 60],  'color': '#fdebd0'},
                {'range': [60, 80],  'color': '#d5f5e3'},
                {'range': [80, 100], 'color': '#a9dfbf'},
            ],
            'threshold': {
                'line':  {'color': "black", 'width': 3},
                'thickness': 0.75,
                'value': 70,
            },
        },
    ))
    fig.update_layout(height=280, margin=dict(t=40, b=10, l=10, r=10))
    return fig


def create_radar_chart(component_scores: dict) -> go.Figure:
    """
    Radar/spider chart showing ATS component scores.
    Shows all 6 dimensions of the resume at once — very impressive visually.
    """
    categories = [c.replace('_', ' ').title() for c in component_scores.keys()]
    values = list(component_scores.values())
    values.append(values[0])   # Close the polygon by repeating first value
    categories.append(categories[0])

    fig = go.Figure(go.Scatterpolar(
        r    = values,
        theta = categories,
        fill = 'toself',
        line = dict(color='#667eea', width=2),
        fillcolor = 'rgba(102, 126, 234, 0.2)',
        name = 'Your Resume',
    ))

    fig.update_layout(
        polar = dict(
            radialaxis = dict(visible=True, range=[0, 100]),
            bgcolor    = 'rgba(255,255,255,0.1)',
        ),
        showlegend = False,
        height     = 350,
        margin     = dict(t=30, b=30, l=30, r=30),
    )
    return fig


def create_skill_gap_bar(matched: list, missing: list) -> go.Figure:
    """Horizontal bar chart comparing matched vs missing skills."""
    if not matched and not missing:
        return None

    fig = go.Figure()

    # Matched skills (green)
    if matched:
        fig.add_trace(go.Bar(
            y    = matched[:10],    # Top 10
            x    = [100] * len(matched[:10]),
            orientation = 'h',
            name = 'Skills You Have',
            marker_color = '#2ecc71',
        ))

    # Missing skills (red)
    if missing:
        fig.add_trace(go.Bar(
            y    = missing[:10],
            x    = [100] * len(missing[:10]),
            orientation = 'h',
            name = 'Missing Skills',
            marker_color = '#e74c3c',
        ))

    fig.update_layout(
        title  = 'Skill Gap Analysis',
        height = 400,
        margin = dict(t=40, b=20, l=20, r=20),
        barmode = 'group',
        xaxis  = dict(showticklabels=False),
    )
    return fig


def create_wordcloud(skills: list) -> bytes:
    """Generate a word cloud image of detected skills."""
    if not skills:
        return None

    text = ' '.join(skills)
    wc = WordCloud(
        width=800, height=400,
        background_color='white',
        colormap='viridis',
        max_words=60,
        prefer_horizontal=0.8,
    ).generate(text)

    buf = io.BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(buf, format='png', dpi=120, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf.getvalue()


# ════════════════════════════════════════════════════════════════════════════
# MAIN PAGE UI
# ════════════════════════════════════════════════════════════════════════════

st.markdown("# 📄 Resume Analyzer")
st.markdown("Upload your resume to get a complete ATS score, skill analysis, and improvement suggestions.")
st.divider()

# ── Sidebar controls ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Analysis Settings")

    target_level = st.selectbox(
        "Target Experience Level",
        ["entry", "mid", "senior", "lead"],
        index=1,
        help="What level of role are you targeting?"
    )

    education_req = st.selectbox(
        "Required Education",
        ["any", "diploma", "bachelor", "master", "phd"],
        index=2,
    )

    job_description = st.text_area(
        "Paste Job Description (optional)",
        height=200,
        placeholder="Paste the job description here for keyword matching...",
        help="If you paste a job description, we compare your resume against it specifically."
    )

    use_sample = st.checkbox("Use sample resume (for demo)")

# ── File Upload ────────────────────────────────────────────────────────────
col_upload, col_info = st.columns([2, 1])

with col_upload:
    uploaded_file = st.file_uploader(
        "Upload your Resume (PDF)",
        type=['pdf'],
        help="Upload a PDF resume. Max 5MB."
    )

with col_info:
    st.markdown("""
    **What we analyze:**
    - 📊 ATS Score (0–100)
    - 🎯 Career recommendation
    - 🔧 Skills extracted
    - ❌ Missing skills
    - 💡 Improvement tips
    - 📥 Downloadable report
    """)

# ── Load resume data ───────────────────────────────────────────────────────
resume_data    = None
skills_result  = None
ats_result     = None

if uploaded_file:
    with st.spinner("Reading your resume..."):
        pdf_bytes   = uploaded_file.read()
        resume_data = parse_resume(pdf_bytes)

elif use_sample:
    sample_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", "sample_resumes", "data_scientist_john_smith.txt"
    )
    if os.path.exists(sample_path):
        text = open(sample_path, encoding='utf-8').read()
        resume_data = parse_resume_from_text(text)
        st.info("Using sample resume: Data Scientist — John Smith")

# ── Run analysis if we have data ───────────────────────────────────────────
if resume_data and not resume_data.get('error'):

    with st.spinner("Analyzing resume... (this takes ~10 seconds)"):
        # Extract skills
        skills_result = extract_skills(
            resume_data['raw_text'],
            resume_data.get('sections')
        )

        # Get career recommendation (if models trained)
        career_result = {'career': 'Run Phase 5 to train models', 'confidence': 0}
        try:
            from src.career_recommender import CareerRecommender
            recommender   = CareerRecommender()
            career_result = recommender.predict(
                resume_data['raw_text'],
                resume_data
            )
            top_careers = recommender.predict_top_n(resume_data['raw_text'], resume_data, n=5)
        except Exception:
            top_careers = []

        # Calculate ATS score
        ats_result = calculate_ats_score(
            resume_data   = resume_data,
            resume_skills = skills_result['all_skills'],
            job_description = job_description if job_description else None,
            target_level    = target_level,
            required_education = education_req,
        )

    # ══════════════════════════════════════════════════════════════════════
    # RESULTS SECTION
    # ══════════════════════════════════════════════════════════════════════

    st.success("✅ Analysis complete!")
    st.divider()

    # ── Row 1: Key Metrics ─────────────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.metric("ATS Score",       f"{ats_result['overall_score']:.0f}%",
                  delta=f"Grade: {ats_result['grade']}")
    with m2:
        st.metric("Skills Found",    skills_result['total_count'])
    with m3:
        st.metric("Experience",      f"{resume_data.get('experience_years', 0)} yrs")
    with m4:
        st.metric("Word Count",      resume_data.get('word_count', 0))
    with m5:
        st.metric("Resume Pages",    resume_data.get('page_count', 1))

    st.divider()

    # ── Row 2: Charts ──────────────────────────────────────────────────
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.plotly_chart(
            create_ats_gauge(ats_result['overall_score']),
            use_container_width=True
        )

    with chart_col2:
        st.plotly_chart(
            create_radar_chart(ats_result['component_scores']),
            use_container_width=True
        )

    # ── Row 3: Component Scores Table ─────────────────────────────────
    st.markdown("### 📊 ATS Score Breakdown")
    comp_df = pd.DataFrame([
        {
            'Component':   k.replace('_', ' ').title(),
            'Score':       f"{v:.0f}%",
            'Weight':      f"{int(v * 0.35 if 'skill' in k else v * 0.2):.0f}pts",
            'Status':      '🟢 Good' if v >= 70 else ('🟡 Average' if v >= 50 else '🔴 Needs Work'),
        }
        for k, v in ats_result['component_scores'].items()
    ])
    st.dataframe(comp_df, use_container_width=True, hide_index=True)

    st.divider()

    # ── Row 4: Contact Info + Career Prediction ────────────────────────
    info_col, career_col = st.columns(2)

    with info_col:
        st.markdown("### 👤 Detected Information")
        st.markdown(f"""
        <div class='metric-card'>
        <b>Name:</b> {resume_data.get('name', 'Not detected')}<br>
        <b>Email:</b> {resume_data.get('email', 'Not found')}<br>
        <b>Phone:</b> {resume_data.get('phone', 'Not found')}<br>
        <b>LinkedIn:</b> {'✅ Found' if resume_data.get('has_linkedin') else '❌ Not found'}<br>
        <b>GitHub:</b>   {'✅ Found' if resume_data.get('has_github')   else '❌ Not found'}<br>
        <b>Education:</b> {', '.join([e.get('degree','?') for e in resume_data.get('education',[])])
                           or 'Not detected'}
        </div>
        """, unsafe_allow_html=True)

    with career_col:
        st.markdown("### 🎯 Career Prediction")
        if top_careers:
            for i, c in enumerate(top_careers):
                bar_val = int(c['confidence'])
                st.markdown(f"**#{c['rank']} {c['career']}** — {c['confidence']:.0f}%")
                st.progress(bar_val / 100)
        else:
            st.info("Train the ML model (Phase 5) to see career predictions.")

    st.divider()

    # ── Row 5: Skills Analysis ─────────────────────────────────────────
    st.markdown("### 🔧 Skills Analysis")
    skill_tab1, skill_tab2, skill_tab3 = st.tabs(
        ["All Skills", "By Category", "Skill Gap"]
    )

    with skill_tab1:
        st.markdown("**Skills detected in your resume:**")
        badges_html = ' '.join(
            f"<span class='skill-badge'>{s}</span>"
            for s in skills_result['all_skills']
        )
        st.markdown(badges_html, unsafe_allow_html=True)

        # Word Cloud
        wc_bytes = create_wordcloud(skills_result['all_skills'])
        if wc_bytes:
            st.image(wc_bytes, caption="Skills Word Cloud", use_column_width=True)

    with skill_tab2:
        by_cat = skills_result.get('by_category', {})
        if by_cat:
            for category, cat_skills in by_cat.items():
                if cat_skills:
                    st.markdown(f"**{category.replace('_', ' ').title()}**")
                    st.markdown(' '.join(
                        f"<span class='skill-badge'>{s}</span>"
                        for s in cat_skills
                    ), unsafe_allow_html=True)
        else:
            st.info("Skills not categorized — ensure skills_db.json is in config/")

    with skill_tab3:
        missing = ats_result.get('missing_skills', [])
        matched = [s for s in skills_result['all_skills'] if s in
                   set(ats_result.get('component_details', {})
                       .get('skill_match', {})
                       .get('matched_skills', []))]

        col_m, col_miss = st.columns(2)
        with col_m:
            st.markdown("**✅ Skills You Have:**")
            for s in matched[:15]:
                st.markdown(f"<span class='skill-badge'>✓ {s}</span>", unsafe_allow_html=True)

        with col_miss:
            st.markdown("**❌ Skills to Add:**")
            for s in missing[:15]:
                st.markdown(f"<span class='missing-badge'>+ {s}</span>", unsafe_allow_html=True)

        gap_fig = create_skill_gap_bar(matched, missing)
        if gap_fig:
            st.plotly_chart(gap_fig, use_container_width=True)

    st.divider()

    # ── Row 6: Feedback ───────────────────────────────────────────────
    fb_col1, fb_col2 = st.columns(2)

    with fb_col1:
        st.markdown("### 💪 Strengths")
        for strength in ats_result.get('strengths', ['Complete Phase 5 training']):
            st.markdown(f"<div class='strength-item'>✅ {strength}</div>",
                        unsafe_allow_html=True)

    with fb_col2:
        st.markdown("### 🚀 Improvements")
        for imp in ats_result.get('improvements', []):
            st.markdown(f"<div class='improvement-item'>→ {imp}</div>",
                        unsafe_allow_html=True)

    st.divider()

    # ── Row 7: Resume Tips ────────────────────────────────────────────
    with st.expander("💡 Professional Resume Tips", expanded=False):
        for tip in ats_result.get('resume_tips', []):
            st.markdown(f"• {tip}")

    # ── Row 8: Download Report ────────────────────────────────────────
    st.markdown("### 📥 Download Full Report")
    pdf_bytes_report = generate_report(
        resume_data, ats_result,
        {}, career_result, skills_result
    )

    if pdf_bytes_report:
        st.download_button(
            label     = "⬇️ Download PDF Report",
            data      = pdf_bytes_report,
            file_name = f"resume_analysis_{resume_data.get('name','candidate').replace(' ','_')}.pdf",
            mime      = "application/pdf",
            type      = "primary",
        )

elif resume_data and resume_data.get('error'):
    st.error(f"Error parsing resume: {resume_data['error']}")
    st.info("Make sure your PDF is not scanned/image-based.")
else:
    # ── Empty state ────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding: 3rem; opacity: 0.6;">
        <h2>Upload your resume to get started</h2>
        <p>Supported format: PDF (max 5MB)</p>
        <p>Or enable "Use sample resume" in the sidebar for a demo</p>
    </div>
    """, unsafe_allow_html=True)