# ui/components.py
# ══════════════════════════════════════════════════════════════════════════
# Reusable HTML component helpers.
# Every function returns an HTML string rendered via st.markdown(..., unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════════════════════

import streamlit as st


# ── Brand logo ─────────────────────────────────────────────────────────────
def render_brand(size="normal"):
    fs = "20px" if size == "normal" else "16px"
    st.markdown(f"""
    <div class="brand">
        <div class="brand-icon">R</div>
        <span class="brand-name" style="font-size:{fs}">ResumeIQ</span>
    </div>
    """, unsafe_allow_html=True)


# ── Section heading ────────────────────────────────────────────────────────
def section_head(title, subtitle="", accent="#6C63FF"):
    sub_html = f'<p style="font-size:12px;color:var(--text2);margin:2px 0 0 14px">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div class="section-head">
        <div class="accent-bar" style="background:linear-gradient(180deg,{accent},var(--teal))"></div>
        <div>
            <h3 style="font-family:Syne,sans-serif;font-size:16px;font-weight:700;color:var(--text);margin:0">{title}</h3>
            {sub_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Big ATS score hero ─────────────────────────────────────────────────────
def render_score_hero(score, grade, label):
    grade_colors = {
        "A":  ("#10B981", "#34d399"),
        "B+": ("#6C63FF", "#a5b4fc"),
        "B":  ("#3B82F6", "#60a5fa"),
        "C+": ("#F59E0B", "#fbbf24"),
        "C":  ("#F97316", "#fb923c"),
        "D":  ("#EF4444", "#f87171"),
        "F":  ("#EF4444", "#f87171"),
    }
    bg, fg = grade_colors.get(grade, ("#6C63FF", "#a5b4fc"))
    st.markdown(f"""
    <div class="score-hero">
        <span class="score-number">{score}</span>
        <div class="score-label">ATS Score</div>
        <span class="score-grade" style="background:rgba(108,99,255,0.15);color:{fg};border:1px solid {bg}40">
            {grade} — {label}
        </span>
    </div>
    """, unsafe_allow_html=True)


# ── Metric mini card ───────────────────────────────────────────────────────
def metric_card(label, value, icon, color, delta_text=""):
    delta_html = f'<div class="mc-delta" style="color:{color}">{delta_text}</div>' if delta_text else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="mc-accent" style="background:{color}"></div>
        <div style="padding-left:8px">
            <div class="mc-icon">{icon}</div>
            <div class="mc-value" style="color:{color}">{value}</div>
            <div class="mc-label">{label}</div>
            {delta_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Skill chips ────────────────────────────────────────────────────────────
def render_chips(skills, chip_type="present"):
    chips = "".join(f'<span class="chip chip-{chip_type}">{s}</span>' for s in skills)
    st.markdown(f'<div style="line-height:2.2">{chips}</div>', unsafe_allow_html=True)


# ── Inline progress bar ────────────────────────────────────────────────────
def progress_bar(label, value, color="#6C63FF"):
    st.markdown(f"""
    <div class="inline-bar-wrap">
        <div class="inline-bar-top">
            <span class="inline-bar-label">{label}</span>
            <span class="inline-bar-value" style="color:{color}">{value}%</span>
        </div>
        <div class="inline-bar-track">
            <div class="inline-bar-fill" style="width:{value}%;background:{color}"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Improvement checklist row ──────────────────────────────────────────────
def improvement_row(text, priority="Medium"):
    cls = {"High": "priority-high", "Medium": "priority-medium", "Low": "priority-low"}.get(priority, "priority-medium")
    icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(priority, "🟡")
    st.markdown(f"""
    <div class="imp-row">
        <span style="font-size:16px">{icon}</span>
        <span style="flex:1;font-size:13px;color:var(--text2);line-height:1.5">{text}</span>
        <span class="imp-priority {cls}">{priority}</span>
    </div>
    """, unsafe_allow_html=True)


# ── Candidate ranking row ──────────────────────────────────────────────────
def candidate_row(rank, name, ats_score, skills_count, exp, education, rec):
    initials = "".join(p[0] for p in name.split()[:2]).upper()
    rec_cls  = {"Strong Hire": "rec-strong", "Hire": "rec-hire", "Maybe": "rec-maybe", "No Hire": "rec-no"}.get(rec, "rec-maybe")
    bar_w    = ats_score
    bar_col  = "#10B981" if ats_score >= 75 else ("#F59E0B" if ats_score >= 55 else "#EF4444")
    st.markdown(f"""
    <div class="cand-row">
        <div style="font-family:Syne,sans-serif;font-weight:800;font-size:16px;color:var(--text3);width:24px;text-align:center">
            #{rank}
        </div>
        <div class="cand-avatar">{initials}</div>
        <div style="flex:1;min-width:0">
            <div style="font-size:14px;font-weight:600;color:var(--text)">{name}</div>
            <div style="font-size:11px;color:var(--text3)">{exp} · {education}</div>
        </div>
        <div style="width:130px">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                <span style="font-size:11px;color:var(--text3)">ATS</span>
                <span style="font-size:12px;font-weight:700;color:{bar_col}">{ats_score}%</span>
            </div>
            <div style="height:5px;background:var(--bg3);border-radius:3px;overflow:hidden">
                <div style="height:100%;width:{bar_w}%;background:{bar_col};border-radius:3px"></div>
            </div>
        </div>
        <div style="font-size:12px;color:var(--text2);text-align:center;min-width:60px">{skills_count} skills</div>
        <span class="rec-badge {rec_cls}">{rec}</span>
    </div>
    """, unsafe_allow_html=True)


# ── Section analysis status row ───────────────────────────────────────────
def section_status_row(section, status, note):
    dot_cls  = {"good": "dot-green", "warn": "dot-amber", "bad": "dot-red"}.get(status, "dot-amber")
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;padding:9px 0;border-bottom:1px solid var(--border)">
        <span class="status-dot {dot_cls}"></span>
        <div style="flex:1">
            <div style="font-size:13px;font-weight:500;color:var(--text)">{section}</div>
            <div style="font-size:11px;color:var(--text3)">{note}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Divider with text ──────────────────────────────────────────────────────
def divider(text=""):
    if text:
        st.markdown(f'<div class="divider-text"><span>{text}</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="s-sep"></div>', unsafe_allow_html=True)


# ── Alert / info banner ────────────────────────────────────────────────────
def info_banner(text, type_="info"):
    colors = {
        "info":    ("#3B82F6", "rgba(59,130,246,0.12)"),
        "success": ("#10B981", "rgba(16,185,129,0.12)"),
        "warning": ("#F59E0B", "rgba(245,158,11,0.12)"),
        "error":   ("#EF4444", "rgba(239,68,68,0.12)"),
    }
    c, bg = colors.get(type_, colors["info"])
    icons  = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
    icon   = icons.get(type_, "ℹ️")
    st.markdown(f"""
    <div style="background:{bg};border:1px solid {c}30;border-radius:12px;padding:12px 16px;
                display:flex;align-items:flex-start;gap:10px;margin-bottom:12px">
        <span style="font-size:16px">{icon}</span>
        <span style="font-size:13px;color:var(--text2);line-height:1.5">{text}</span>
    </div>
    """, unsafe_allow_html=True)


# ── Career prediction bar ──────────────────────────────────────────────────
def career_prediction_row(rank, career, confidence):
    is_top  = rank == 1
    bar_col = "linear-gradient(90deg,#6C63FF,#00C9A7)" if is_top else "rgba(108,99,255,0.5)"
    st.markdown(f"""
    <div style="margin-bottom:12px">
        <div style="display:flex;justify-content:space-between;margin-bottom:5px;align-items:center">
            <span style="font-size:13px;font-weight:{'700' if is_top else '400'};color:var(--text)">
                {'🏆 ' if is_top else ''}{career}
            </span>
            <span style="font-size:13px;font-weight:700;
                background:linear-gradient(135deg,#6C63FF,#00C9A7);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent">
                {confidence:.1f}%
            </span>
        </div>
        <div style="height:7px;background:var(--bg3);border-radius:4px;overflow:hidden">
            <div style="height:100%;width:{confidence}%;background:{bar_col};border-radius:4px;transition:width 1.2s ease"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)