# ui/styles.py
# ══════════════════════════════════════════════════════════════════════════
# ALL custom CSS for the premium SaaS redesign.
# Called once from app.py via inject_styles().
# ══════════════════════════════════════════════════════════════════════════

import streamlit as st


def inject_styles():
    """Inject the complete premium CSS into the Streamlit app."""
    st.markdown("""
    <style>
    /* ── Google Fonts ─────────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

    /* ── CSS Variables ────────────────────────────────────────────────── */
    :root {
        --purple:       #6C63FF;
        --purple-dark:  #4B44CC;
        --purple-light: #EEEDff;
        --purple-glow:  rgba(108,99,255,0.18);
        --teal:         #00C9A7;
        --teal-light:   #E0FAF6;
        --blue:         #3B82F6;
        --blue-light:   #EFF6FF;
        --amber:        #F59E0B;
        --amber-light:  #FFFBEB;
        --red:          #EF4444;
        --red-light:    #FEF2F2;
        --green:        #10B981;
        --green-light:  #ECFDF5;
        --coral:        #F97316;
        --coral-light:  #FFF7ED;
        --bg:           #0F0F1A;
        --bg2:          #16162A;
        --bg3:          #1E1E35;
        --border:       rgba(255,255,255,0.07);
        --border2:      rgba(255,255,255,0.12);
        --text:         #F1F0FF;
        --text2:        #A8A8C0;
        --text3:        #6B6B88;
        --card-shadow:  0 4px 32px rgba(0,0,0,0.35);
        --card-shadow2: 0 2px 12px rgba(0,0,0,0.25);
        --glow:         0 0 40px rgba(108,99,255,0.15);
    }

    /* ── Global resets ────────────────────────────────────────────────── */
    html, body, [class*="css"], .stApp {
        font-family: 'DM Sans', sans-serif !important;
        background: var(--bg) !important;
        color: var(--text) !important;
    }

    /* Hide Streamlit branding & hamburger */
    #MainMenu, footer, header,
    .stDeployButton, [data-testid="stToolbar"],
    [data-testid="stDecoration"] { display: none !important; }

    /* ── Scrollbar ────────────────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg2); }
    ::-webkit-scrollbar-thumb { background: var(--purple); border-radius: 3px; }

    /* ── Sidebar ──────────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: var(--bg2) !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    /* ── Main content area ────────────────────────────────────────────── */
    .block-container {
        padding: 1.5rem 2rem 4rem !important;
        max-width: 100% !important;
    }

    /* ── Buttons ──────────────────────────────────────────────────────── */
    .stButton > button {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        border: none !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(108,99,255,0.35) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--purple), var(--purple-dark)) !important;
        color: #fff !important;
        padding: 0.6rem 1.5rem !important;
    }

    /* ── File uploader ────────────────────────────────────────────────── */
    [data-testid="stFileUploader"] {
        background: var(--bg3) !important;
        border: 2px dashed var(--purple) !important;
        border-radius: 16px !important;
        padding: 1rem !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: var(--teal) !important;
        background: rgba(108,99,255,0.05) !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        background: transparent !important;
        border: none !important;
    }

    /* ── Text inputs & textareas ──────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background: var(--bg3) !important;
        border: 1px solid var(--border2) !important;
        border-radius: 10px !important;
        color: var(--text) !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--purple) !important;
        box-shadow: 0 0 0 2px var(--purple-glow) !important;
    }

    /* ── Tabs ──────────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg2) !important;
        border-radius: 12px !important;
        padding: 4px !important;
        gap: 4px !important;
        border-bottom: none !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 8px !important;
        color: var(--text2) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--purple) !important;
        color: #fff !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background: transparent !important;
        padding: 1.5rem 0 0 !important;
    }

    /* ── Metrics ──────────────────────────────────────────────────────── */
    [data-testid="metric-container"] {
        background: var(--bg2) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        padding: 1rem 1.2rem !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: 'Syne', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }

    /* ── Expanders ────────────────────────────────────────────────────── */
    [data-testid="stExpander"] {
        background: var(--bg2) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }
    [data-testid="stExpander"] > div > div {
        color: var(--text) !important;
    }

    /* ── Progress bars ────────────────────────────────────────────────── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--purple), var(--teal)) !important;
        border-radius: 4px !important;
    }
    .stProgress > div > div > div {
        background: var(--bg3) !important;
        border-radius: 4px !important;
    }

    /* ── Dividers ─────────────────────────────────────────────────────── */
    hr { border-color: var(--border) !important; }

    /* ── Alerts / info boxes ──────────────────────────────────────────── */
    .stAlert {
        background: var(--bg2) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
    }

    /* ── Plotly charts ────────────────────────────────────────────────── */
    .js-plotly-plot .plotly {
        background: transparent !important;
    }

    /* ══════════════════════════════════════════════════════════════════════
       CUSTOM COMPONENT CLASSES
       Used via st.markdown(..., unsafe_allow_html=True)
    ════════════════════════════════════════════════════════════════════════ */

    /* Logo + brand */
    .brand {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 2rem;
    }
    .brand-icon {
        width: 36px; height: 36px;
        background: linear-gradient(135deg, var(--purple), var(--teal));
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px; font-weight: 800; color: #fff;
        font-family: 'Syne', sans-serif;
    }
    .brand-name {
        font-family: 'Syne', sans-serif;
        font-size: 20px; font-weight: 800;
        background: linear-gradient(135deg, var(--purple), var(--teal));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Sidebar nav links */
    .nav-link {
        display: flex; align-items: center; gap: 10px;
        padding: 10px 14px; border-radius: 10px;
        color: var(--text2); font-size: 14px; font-weight: 500;
        cursor: pointer; margin-bottom: 4px;
        text-decoration: none;
        transition: all 0.15s;
        border: 1px solid transparent;
    }
    .nav-link:hover {
        background: var(--purple-glow);
        color: var(--text);
        border-color: var(--border2);
    }
    .nav-link.active {
        background: linear-gradient(135deg, rgba(108,99,255,0.2), rgba(0,201,167,0.1));
        color: var(--purple);
        border-color: rgba(108,99,255,0.3);
        font-weight: 600;
    }

    /* Score card (big circular-style) */
    .score-hero {
        background: linear-gradient(135deg, rgba(108,99,255,0.15), rgba(0,201,167,0.08));
        border: 1px solid rgba(108,99,255,0.3);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .score-hero::before {
        content: '';
        position: absolute; top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle at 50% 50%, rgba(108,99,255,0.06), transparent 60%);
        pointer-events: none;
    }
    .score-number {
        font-family: 'Syne', sans-serif;
        font-size: 72px; font-weight: 800; line-height: 1;
        background: linear-gradient(135deg, var(--purple), var(--teal));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: block;
    }
    .score-label {
        font-size: 13px; color: var(--text2); margin-top: 6px;
        text-transform: uppercase; letter-spacing: 1.5px;
    }
    .score-grade {
        display: inline-block; margin-top: 12px;
        padding: 4px 16px; border-radius: 20px;
        font-size: 12px; font-weight: 700;
        text-transform: uppercase; letter-spacing: 1px;
    }

    /* Metric mini card */
    .metric-card {
        background: var(--bg2);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        position: relative;
        overflow: hidden;
        transition: border-color 0.2s, transform 0.2s;
    }
    .metric-card:hover {
        border-color: var(--border2);
        transform: translateY(-2px);
    }
    .metric-card .mc-accent {
        position: absolute; top: 0; left: 0;
        width: 4px; height: 100%;
        border-radius: 14px 0 0 14px;
    }
    .metric-card .mc-icon {
        font-size: 22px; margin-bottom: 8px;
    }
    .metric-card .mc-value {
        font-family: 'Syne', sans-serif;
        font-size: 26px; font-weight: 700;
        line-height: 1;
    }
    .metric-card .mc-label {
        font-size: 12px; color: var(--text2);
        margin-top: 4px; text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .metric-card .mc-delta {
        font-size: 11px; margin-top: 8px;
    }

    /* Skill chip */
    .chip {
        display: inline-block;
        padding: 4px 12px; margin: 3px 3px;
        border-radius: 20px; font-size: 12px; font-weight: 500;
    }
    .chip-present {
        background: rgba(16,185,129,0.15);
        color: #34d399;
        border: 1px solid rgba(16,185,129,0.3);
    }
    .chip-missing {
        background: rgba(239,68,68,0.15);
        color: #f87171;
        border: 1px solid rgba(239,68,68,0.3);
    }
    .chip-neutral {
        background: rgba(108,99,255,0.15);
        color: #a5b4fc;
        border: 1px solid rgba(108,99,255,0.3);
    }
    .chip-warning {
        background: rgba(245,158,11,0.15);
        color: #fbbf24;
        border: 1px solid rgba(245,158,11,0.3);
    }

    /* Section heading */
    .section-head {
        display: flex; align-items: center; gap: 10px;
        margin-bottom: 1rem;
    }
    .section-head .accent-bar {
        width: 4px; height: 22px;
        border-radius: 2px;
        background: linear-gradient(180deg, var(--purple), var(--teal));
    }
    .section-head h3 {
        font-family: 'Syne', sans-serif;
        font-size: 16px; font-weight: 700;
        color: var(--text); margin: 0;
    }
    .section-head p {
        font-size: 12px; color: var(--text2);
        margin: 2px 0 0 14px;
    }

    /* Glass card */
    .glass-card {
        background: rgba(22,22,42,0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.4rem;
        box-shadow: var(--card-shadow2);
    }

    /* Landing page hero */
    .hero-section {
        text-align: center;
        padding: 5rem 2rem 3rem;
        background:
            radial-gradient(ellipse 70% 40% at 50% 0%, rgba(108,99,255,0.15), transparent),
            radial-gradient(ellipse 40% 30% at 80% 60%, rgba(0,201,167,0.08), transparent);
    }
    .hero-badge {
        display: inline-block; margin-bottom: 1.5rem;
        padding: 6px 18px; border-radius: 20px;
        background: rgba(108,99,255,0.15);
        border: 1px solid rgba(108,99,255,0.35);
        color: #a5b4fc; font-size: 13px; font-weight: 500;
        letter-spacing: 0.5px;
    }
    .hero-title {
        font-family: 'Syne', sans-serif;
        font-size: 56px; font-weight: 800; line-height: 1.1;
        margin: 0 0 1.2rem;
        letter-spacing: -1.5px;
    }
    .hero-title .gradient-text {
        background: linear-gradient(135deg, var(--purple) 30%, var(--teal));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-sub {
        font-size: 18px; color: var(--text2);
        max-width: 540px; margin: 0 auto 2.5rem;
        line-height: 1.7;
    }

    /* Stat pills */
    .stat-pill {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 8px 18px; border-radius: 12px;
        background: var(--bg2); border: 1px solid var(--border);
        margin: 6px;
    }
    .stat-pill .sp-value {
        font-family: 'Syne', sans-serif;
        font-size: 18px; font-weight: 800;
    }
    .stat-pill .sp-label {
        font-size: 12px; color: var(--text2);
    }

    /* Feature card */
    .feat-card {
        background: var(--bg2);
        border: 1px solid var(--border);
        border-radius: 16px; padding: 1.5rem;
        height: 100%;
        transition: border-color 0.2s, transform 0.2s;
    }
    .feat-card:hover {
        border-color: rgba(108,99,255,0.4);
        transform: translateY(-3px);
    }
    .feat-icon {
        font-size: 28px; margin-bottom: 0.75rem;
    }
    .feat-title {
        font-family: 'Syne', sans-serif;
        font-size: 15px; font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .feat-desc {
        font-size: 13px; color: var(--text2);
        line-height: 1.6;
    }

    /* Improvement row */
    .imp-row {
        display: flex; align-items: flex-start; gap: 12px;
        padding: 14px 0; border-bottom: 1px solid var(--border);
    }
    .imp-priority {
        padding: 3px 10px; border-radius: 12px;
        font-size: 11px; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.5px;
        white-space: nowrap;
    }
    .priority-high   { background: rgba(239,68,68,0.15);   color: #f87171; border: 1px solid rgba(239,68,68,0.3);   }
    .priority-medium { background: rgba(245,158,11,0.15);  color: #fbbf24; border: 1px solid rgba(245,158,11,0.3);  }
    .priority-low    { background: rgba(16,185,129,0.15);  color: #34d399; border: 1px solid rgba(16,185,129,0.3);  }

    /* Candidate table row */
    .cand-row {
        display: flex; align-items: center; gap: 12px;
        padding: 12px 0; border-bottom: 1px solid var(--border);
    }
    .cand-avatar {
        width: 38px; height: 38px; border-radius: 50%;
        background: linear-gradient(135deg, var(--purple-glow), rgba(0,201,167,0.15));
        border: 1px solid rgba(108,99,255,0.3);
        display: flex; align-items: center; justify-content: center;
        font-family: 'Syne', sans-serif;
        font-size: 13px; font-weight: 700; color: #a5b4fc;
        flex-shrink: 0;
    }

    /* Recommendation badge */
    .rec-badge {
        padding: 4px 10px; border-radius: 12px;
        font-size: 11px; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.5px;
    }
    .rec-strong { background: rgba(16,185,129,0.15);  color: #34d399; border: 1px solid rgba(16,185,129,0.3); }
    .rec-hire   { background: rgba(59,130,246,0.15);  color: #60a5fa; border: 1px solid rgba(59,130,246,0.3); }
    .rec-maybe  { background: rgba(245,158,11,0.15);  color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }
    .rec-no     { background: rgba(239,68,68,0.15);   color: #f87171; border: 1px solid rgba(239,68,68,0.3); }

    /* Loading animation */
    @keyframes pulse-glow {
        0%, 100% { opacity: 0.6; transform: scale(1); }
        50%       { opacity: 1;   transform: scale(1.04); }
    }
    .loading-orb {
        width: 80px; height: 80px; border-radius: 50%;
        background: linear-gradient(135deg, var(--purple), var(--teal));
        margin: 0 auto 1.5rem;
        animation: pulse-glow 1.8s ease-in-out infinite;
    }

    /* Progress ring helper (CSS only, no JS needed) */
    .progress-ring-wrap {
        display: flex; flex-direction: column;
        align-items: center; gap: 6px;
    }
    .progress-ring-label {
        font-size: 12px; color: var(--text2);
        text-align: center;
    }

    /* Testimonial card */
    .testi-card {
        background: var(--bg2); border: 1px solid var(--border);
        border-radius: 16px; padding: 1.4rem;
    }
    .testi-text {
        font-size: 14px; color: var(--text2);
        line-height: 1.7; margin-bottom: 1rem;
        font-style: italic;
    }
    .testi-name {
        font-family: 'Syne', sans-serif;
        font-size: 14px; font-weight: 700; color: var(--text);
    }
    .testi-role {
        font-size: 12px; color: var(--text3);
    }

    /* Divider with text */
    .divider-text {
        display: flex; align-items: center; gap: 12px;
        margin: 2rem 0;
    }
    .divider-text::before,
    .divider-text::after {
        content: ''; flex: 1;
        height: 1px; background: var(--border);
    }
    .divider-text span {
        font-size: 12px; color: var(--text3);
        text-transform: uppercase; letter-spacing: 1px;
        white-space: nowrap;
    }

    /* Info tooltip icon */
    .info-icon {
        display: inline-flex; align-items: center; justify-content: center;
        width: 16px; height: 16px; border-radius: 50%;
        background: var(--bg3); border: 1px solid var(--border2);
        color: var(--text3); font-size: 10px; font-weight: 700;
        cursor: help; vertical-align: middle; margin-left: 4px;
    }

    /* Section separator */
    .s-sep {
        height: 1px; background: var(--border);
        margin: 2rem 0;
    }

    /* How it works step */
    .hiw-step {
        background: var(--bg2); border: 1px solid var(--border);
        border-radius: 16px; padding: 1.5rem;
        text-align: center;
        position: relative;
    }
    .hiw-num {
        font-family: 'Syne', sans-serif;
        font-size: 40px; font-weight: 800;
        opacity: 0.12; color: var(--purple);
        line-height: 1; margin-bottom: 8px;
    }
    .hiw-title {
        font-family: 'Syne', sans-serif;
        font-size: 15px; font-weight: 700;
        margin-bottom: 6px;
    }
    .hiw-desc {
        font-size: 13px; color: var(--text2); line-height: 1.6;
    }

    /* CTA banner */
    .cta-banner {
        background: linear-gradient(135deg, rgba(108,99,255,0.2), rgba(0,201,167,0.12));
        border: 1px solid rgba(108,99,255,0.3);
        border-radius: 20px; padding: 3rem 2rem;
        text-align: center;
        position: relative; overflow: hidden;
    }
    .cta-banner::before {
        content: '';
        position: absolute; inset: 0;
        background: radial-gradient(ellipse 60% 50% at 50% 50%, rgba(108,99,255,0.08), transparent);
        pointer-events: none;
    }
    .cta-title {
        font-family: 'Syne', sans-serif;
        font-size: 32px; font-weight: 800;
        margin-bottom: 0.75rem;
    }
    .cta-sub {
        font-size: 16px; color: var(--text2);
        margin-bottom: 2rem;
    }

    /* Footer */
    .footer {
        border-top: 1px solid var(--border);
        padding: 1.5rem 0;
        display: flex; justify-content: space-between; align-items: center;
        flex-wrap: wrap; gap: 12px;
    }
    .footer-brand {
        font-family: 'Syne', sans-serif;
        font-weight: 800; font-size: 15px;
        background: linear-gradient(135deg, var(--purple), var(--teal));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .footer-copy {
        font-size: 12px; color: var(--text3);
    }

    /* Status dot */
    .status-dot {
        display: inline-block;
        width: 8px; height: 8px; border-radius: 50%;
        margin-right: 6px;
    }
    .dot-green  { background: var(--green); box-shadow: 0 0 6px rgba(16,185,129,0.5); }
    .dot-amber  { background: var(--amber); box-shadow: 0 0 6px rgba(245,158,11,0.5); }
    .dot-red    { background: var(--red);   box-shadow: 0 0 6px rgba(239,68,68,0.5); }

    /* Analysis section card */
    .a-card {
        background: var(--bg2);
        border: 1px solid var(--border);
        border-radius: 16px; padding: 1.4rem;
        margin-bottom: 1rem;
    }

    /* Inline progress bar */
    .inline-bar-wrap {
        margin-bottom: 12px;
    }
    .inline-bar-top {
        display: flex; justify-content: space-between;
        margin-bottom: 5px;
    }
    .inline-bar-label { font-size: 13px; color: var(--text2); }
    .inline-bar-value { font-size: 13px; font-weight: 600; }
    .inline-bar-track {
        height: 8px; background: var(--bg3);
        border-radius: 4px; overflow: hidden;
    }
    .inline-bar-fill {
        height: 100%; border-radius: 4px;
        transition: width 1.2s ease;
    }

    /* FAQ accordion */
    .faq-item {
        background: var(--bg2); border: 1px solid var(--border);
        border-radius: 12px; margin-bottom: 8px; overflow: hidden;
    }

    </style>
    """, unsafe_allow_html=True)