import streamlit as st


def inject_css():
    st.markdown(
        """
<style>
:root {
  --bg: #f5f7fb;
  --surface: #ffffff;
  --surface-2: #f9fafc;
  --surface-3: #eef2f7;
  --text: #111827;
  --muted: #667085;
  --faint: #98a2b3;
  --line: #e4e7ec;
  --line-strong: #d0d5dd;
  --blue: #2563eb;
  --blue-dark: #1d4ed8;
  --green: #059669;
  --amber: #d97706;
  --red: #dc2626;
  --indigo: #4f46e5;
  --shadow-sm: 0 1px 2px rgba(16, 24, 40, .06);
  --shadow-md: 0 14px 36px rgba(16, 24, 40, .10);
  --radius: 8px;
  --font: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

* { box-sizing: border-box; }
html, body, .stApp, [class*="css"] {
  font-family: var(--font) !important;
  color: var(--text);
}
.stApp { background: var(--bg) !important; }
#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
  display: none !important;
}
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stSidebar"] {
  background: #0f172a !important;
  border-right: 1px solid rgba(255,255,255,.08);
  min-width: 264px !important;
  max-width: 264px !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }
[data-testid="stSidebarNav"] { display: none !important; }

.shell {
  width: min(1440px, 100%);
  margin: 0 auto;
  padding: 28px 32px 56px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 22px;
}
.page-header h1 {
  margin: 0;
  font-size: 30px;
  line-height: 1.16;
  letter-spacing: 0;
  font-weight: 760;
}
.page-header p {
  margin: 8px 0 0;
  color: var(--muted);
  max-width: 720px;
  font-size: 15px;
  line-height: 1.65;
}
.eyebrow {
  margin: 0 0 8px !important;
  color: var(--blue) !important;
  font-size: 12px !important;
  line-height: 1 !important;
  font-weight: 740 !important;
  text-transform: uppercase;
  letter-spacing: .08em;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  height: 64px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 0 32px;
  background: rgba(255,255,255,.86);
  backdrop-filter: blur(18px);
  border-bottom: 1px solid var(--line);
}
.topbar-title { font-size: 15px; font-weight: 760; }
.topbar-subtitle { font-size: 12px; color: var(--muted); margin-top: 2px; }
.topbar-actions { display: flex; align-items: center; gap: 10px; }
.topbar-badge {
  display: inline-flex;
  align-items: center;
  height: 30px;
  padding: 0 11px;
  border-radius: 999px;
  border: 1px solid #bfdbfe;
  color: #1e40af;
  background: #eff6ff;
  font-size: 12px;
  font-weight: 700;
}

.sb {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 18px 12px;
}
.sb-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #fff;
  font-size: 18px;
  font-weight: 800;
  padding: 6px 6px 20px;
}
.sb-mark {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 8px;
  background: #fff;
  color: #0f172a;
  font-size: 13px;
  letter-spacing: 0;
}
.sb-section {
  color: #94a3b8;
  font-size: 11px;
  font-weight: 760;
  letter-spacing: .08em;
  text-transform: uppercase;
  padding: 8px 8px 6px;
}
.sb-foot {
  margin-top: auto;
  border-top: 1px solid rgba(255,255,255,.10);
  color: #94a3b8;
  font-size: 12px;
  line-height: 1.65;
  padding: 16px 8px 4px;
}
.sb-foot strong { display: block; color: #fff; margin-bottom: 6px; }

.stButton > button {
  border-radius: var(--radius) !important;
  min-height: 40px;
  font-weight: 700 !important;
  transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease, background .16s ease;
}
.stButton > button:hover { transform: translateY(-1px); box-shadow: var(--shadow-sm); }
.stButton > button[kind="primary"] {
  background: var(--blue) !important;
  border: 1px solid var(--blue) !important;
  color: #fff !important;
}
.stButton > button[kind="primary"]:hover { background: var(--blue-dark) !important; }
.stButton > button[kind="secondary"] {
  background: #fff !important;
  border: 1px solid var(--line-strong) !important;
  color: var(--text) !important;
}
[data-testid="stSidebar"] .stButton > button {
  justify-content: flex-start;
  min-height: 38px;
  border-radius: 7px !important;
  box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: #e0edff !important;
  border-color: #e0edff !important;
  color: #0f172a !important;
}
[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
  background: transparent !important;
  border-color: transparent !important;
  color: #cbd5e1 !important;
}
[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
  background: rgba(255,255,255,.07) !important;
  color: #fff !important;
}

.panel {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  padding: 20px;
  margin-bottom: 18px;
  animation: fadeUp .28s ease both;
}
.panel-tight { padding: 16px; }
.panel-muted { background: var(--surface-2); }
.section-title { margin-bottom: 14px; }
.section-title h2 { margin: 0; font-size: 16px; font-weight: 760; }
.section-title p { margin: 5px 0 0; color: var(--muted); font-size: 13px; line-height: 1.55; }
.muted { color: var(--muted); font-size: 13px; line-height: 1.6; }

.metric-card {
  position: relative;
  min-height: 132px;
  padding: 18px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  animation: fadeUp .28s ease both;
}
.metric-card:before {
  content: "";
  position: absolute;
  inset: 0 0 auto 0;
  height: 3px;
  background: var(--blue);
}
.metric-card span {
  display: block;
  color: var(--muted);
  font-size: 12px;
  font-weight: 720;
  letter-spacing: .04em;
  text-transform: uppercase;
}
.metric-card strong {
  display: block;
  margin-top: 18px;
  font-size: 34px;
  line-height: 1;
  font-weight: 790;
}
.metric-card small {
  display: block;
  margin-top: 10px;
  color: var(--muted);
  font-size: 13px;
}
.tone-green:before, .metric-card.tone-green:before, .progress-track .tone-green { background: var(--green); }
.tone-amber:before, .metric-card.tone-amber:before, .progress-track .tone-amber { background: var(--amber); }
.tone-red:before, .metric-card.tone-red:before, .progress-track .tone-red { background: var(--red); }
.tone-indigo:before, .metric-card.tone-indigo:before, .progress-track .tone-indigo { background: var(--indigo); }
.tone-blue:before, .metric-card.tone-blue:before, .progress-track .tone-blue { background: var(--blue); }

.chip-row { display: flex; flex-wrap: wrap; gap: 8px; }
.chip {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  border-radius: 999px;
  padding: 0 11px;
  border: 1px solid var(--line);
  background: var(--surface-2);
  color: var(--text);
  font-size: 12px;
  font-weight: 650;
}
.chip-good { background: #ecfdf3; color: #067647; border-color: #abefc6; }
.chip-warn { background: #fffaeb; color: #b54708; border-color: #fedf89; }
.chip-blue { background: #eff6ff; color: #1d4ed8; border-color: #bfdbfe; }
.chip-red { background: #fef2f2; color: #b91c1c; border-color: #fecaca; }

.progress-row { padding: 11px 0; border-bottom: 1px solid var(--line); }
.progress-row:last-child { border-bottom: 0; }
.progress-row div:first-child { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 7px; }
.progress-row span { font-size: 13px; color: var(--text); font-weight: 650; }
.progress-row strong { font-size: 13px; color: var(--muted); }
.progress-track {
  height: 8px;
  background: var(--surface-3);
  border-radius: 999px;
  overflow: hidden;
}
.progress-track i {
  display: block;
  height: 100%;
  border-radius: inherit;
  transition: width .75s cubic-bezier(.22, 1, .36, 1);
}

.insight-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 0;
  border-bottom: 1px solid var(--line);
}
.insight-row:last-child { border-bottom: 0; }
.insight-row strong { display: block; font-size: 14px; }
.insight-row p { margin: 5px 0 0; color: var(--muted); font-size: 13px; line-height: 1.55; }
.insight-row span {
  border-radius: 999px;
  padding: 4px 9px;
  background: var(--surface-3);
  color: var(--muted);
  font-size: 11px;
  font-weight: 760;
  white-space: nowrap;
}

.landing {
  min-height: 100vh;
  background:
    linear-gradient(180deg, #ffffff 0%, #f5f7fb 72%),
    var(--bg);
}
.landing-nav {
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 44px;
  border-bottom: 1px solid var(--line);
  background: rgba(255,255,255,.88);
  backdrop-filter: blur(18px);
}
.brand { display: flex; align-items: center; gap: 10px; font-weight: 820; color: var(--text); }
.brand-mark {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  background: #0f172a;
  color: #fff;
  font-size: 12px;
}
.hero {
  padding: 74px 44px 28px;
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(420px, .95fr);
  gap: 42px;
  align-items: center;
  width: min(1280px, 100%);
  margin: 0 auto;
}
.hero h1 {
  margin: 0;
  font-size: clamp(42px, 5vw, 68px);
  line-height: 1.04;
  font-weight: 820;
  letter-spacing: 0;
}
.hero p {
  margin: 20px 0 0;
  color: var(--muted);
  font-size: 18px;
  line-height: 1.7;
  max-width: 680px;
}
.hero-actions { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 30px; }
.hero-board {
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--surface);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}
.board-head {
  display: flex;
  justify-content: space-between;
  padding: 15px 16px;
  border-bottom: 1px solid var(--line);
  color: var(--muted);
  font-size: 12px;
  font-weight: 730;
}
.pipeline { padding: 16px; display: grid; gap: 10px; }
.candidate {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 12px;
  align-items: center;
  padding: 13px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface-2);
}
.candidate strong { font-size: 14px; }
.candidate span { color: var(--muted); font-size: 12px; }
.score-pill {
  border-radius: 999px;
  background: #ecfdf3;
  color: #067647;
  border: 1px solid #abefc6;
  padding: 5px 9px;
  font-size: 12px;
  font-weight: 760;
}
.stats-band {
  width: min(1280px, 100%);
  margin: 34px auto 0;
  padding: 0 44px 52px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.empty-state {
  border: 1px dashed var(--line-strong);
  border-radius: var(--radius);
  background: var(--surface-2);
  padding: 26px;
  text-align: center;
}
.empty-state strong { display: block; font-size: 17px; }
.empty-state p { margin: 8px auto 0; max-width: 560px; color: var(--muted); line-height: 1.6; }

.stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] > div {
  border-radius: var(--radius) !important;
  border-color: var(--line-strong) !important;
  background: #fff !important;
}
[data-testid="stFileUploader"] {
  border: 1px dashed var(--line-strong);
  border-radius: var(--radius);
  background: var(--surface-2);
  padding: 12px;
}
[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 980px) {
  [data-testid="stSidebar"] { min-width: 220px !important; max-width: 220px !important; }
  .hero { grid-template-columns: 1fr; padding: 48px 22px 20px; }
  .stats-band { grid-template-columns: repeat(2, 1fr); padding: 0 22px 36px; }
  .landing-nav, .topbar { padding-left: 18px; padding-right: 18px; }
  .shell { padding: 22px 18px 44px; }
}
@media (max-width: 640px) {
  .stats-band { grid-template-columns: 1fr; }
  .page-header h1 { font-size: 24px; }
  .topbar-actions { display: none; }
}
</style>
""",
        unsafe_allow_html=True,
    )
