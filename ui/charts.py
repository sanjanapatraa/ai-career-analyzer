# ui/charts.py
# ══════════════════════════════════════════════════════════════════════════
# All Plotly chart helpers — dark themed, premium styled.
# Every function returns a plotly Figure ready for st.plotly_chart()
# ══════════════════════════════════════════════════════════════════════════

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── Shared dark layout ─────────────────────────────────────────────────────
LAYOUT_BASE = dict(
    paper_bgcolor = "rgba(0,0,0,0)",
    plot_bgcolor  = "rgba(0,0,0,0)",
    font          = dict(family="DM Sans, sans-serif", color="#A8A8C0", size=12),
    margin        = dict(t=30, b=20, l=10, r=10),
    showlegend    = False,
)

GRID_COLOR  = "rgba(255,255,255,0.06)"
AXIS_STYLE  = dict(gridcolor=GRID_COLOR, zeroline=False, tickcolor="rgba(0,0,0,0)", linecolor=GRID_COLOR)
COLORS      = ["#6C63FF", "#00C9A7", "#3B82F6", "#F59E0B", "#EF4444", "#F97316", "#10B981"]


# ── Radar chart ───────────────────────────────────────────────────────────
def radar_chart(categories, values, title="Score Radar"):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r      = values + [values[0]],
        theta  = categories + [categories[0]],
        fill   = "toself",
        line   = dict(color="#6C63FF", width=2),
        fillcolor = "rgba(108,99,255,0.15)",
        name   = "Score",
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title = dict(text=title, font=dict(size=14, color="#F1F0FF", family="Syne, sans-serif"), x=0),
        polar = dict(
            bgcolor    = "rgba(255,255,255,0.02)",
            radialaxis = dict(range=[0,100], tickfont=dict(size=9), gridcolor=GRID_COLOR, linecolor=GRID_COLOR),
            angularaxis = dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR),
        ),
    )
    return fig


# ── Gauge / indicator chart ────────────────────────────────────────────────
def gauge_chart(value, title="Score", reference=70):
    if value >= 75:   bar_color = "#10B981"
    elif value >= 55: bar_color = "#6C63FF"
    elif value >= 40: bar_color = "#F59E0B"
    else:             bar_color = "#EF4444"

    fig = go.Figure(go.Indicator(
        mode  = "gauge+number+delta",
        value = value,
        delta = dict(reference=reference, increasing=dict(color="#10B981"), decreasing=dict(color="#EF4444")),
        title = dict(text=title, font=dict(size=14, color="#F1F0FF", family="Syne, sans-serif")),
        gauge = dict(
            axis       = dict(range=[0,100], tickwidth=1, tickcolor="#6B6B88"),
            bar        = dict(color=bar_color),
            bgcolor    = "rgba(255,255,255,0.04)",
            borderwidth= 0,
            steps = [
                dict(range=[0,40],   color="rgba(239,68,68,0.08)"),
                dict(range=[40,60],  color="rgba(245,158,11,0.08)"),
                dict(range=[60,80],  color="rgba(108,99,255,0.08)"),
                dict(range=[80,100], color="rgba(16,185,129,0.08)"),
            ],
            threshold = dict(line=dict(color="#A8A8C0", width=2), thickness=0.75, value=reference),
        ),
    ))
    fig.update_layout(**LAYOUT_BASE, height=260)
    return fig


# ── Horizontal bar chart ───────────────────────────────────────────────────
def hbar_chart(labels, values, title="", colors_list=None):
    clrs = colors_list or COLORS[:len(labels)]
    fig  = go.Figure(go.Bar(
        y           = labels,
        x           = values,
        orientation = "h",
        marker      = dict(color=clrs, line=dict(width=0)),
        text        = [f"{v}%" for v in values],
        textposition= "outside",
        textfont    = dict(size=11, color="#A8A8C0"),
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title  = dict(text=title, font=dict(size=14, color="#F1F0FF", family="Syne, sans-serif"), x=0),
        xaxis  = dict(**AXIS_STYLE, range=[0,115]),
        yaxis  = dict(tickcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)"),
        height = max(220, len(labels) * 48),
    )
    return fig


# ── Vertical bar chart ────────────────────────────────────────────────────
def vbar_chart(labels, values, title="", color="#6C63FF"):
    fig = go.Figure(go.Bar(
        x           = labels,
        y           = values,
        marker      = dict(
            color       = values,
            colorscale  = [[0,"#3B0764"],[0.5,"#6C63FF"],[1,"#00C9A7"]],
            line        = dict(width=0),
        ),
        text        = [f"{v}%" for v in values],
        textposition= "outside",
        textfont    = dict(size=11, color="#A8A8C0"),
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title  = dict(text=title, font=dict(size=14, color="#F1F0FF", family="Syne, sans-serif"), x=0),
        xaxis  = dict(tickcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)"),
        yaxis  = dict(**AXIS_STYLE, range=[0,115]),
        height = 280,
    )
    return fig


# ── Donut / pie chart ─────────────────────────────────────────────────────
def donut_chart(labels, values, title=""):
    fig = go.Figure(go.Pie(
        labels       = labels,
        values       = values,
        hole         = 0.62,
        marker       = dict(colors=COLORS[:len(labels)], line=dict(color="rgba(0,0,0,0)", width=0)),
        textinfo     = "none",
        hovertemplate= "<b>%{label}</b><br>%{value}%<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title      = dict(text=title, font=dict(size=14, color="#F1F0FF", family="Syne, sans-serif"), x=0),
        showlegend = True,
        legend     = dict(font=dict(size=11, color="#A8A8C0"), bgcolor="rgba(0,0,0,0)", orientation="v"),
        height     = 280,
    )
    return fig


# ── Line / trend chart ────────────────────────────────────────────────────
def line_chart(x, y, title="ATS Score Trend", y_label="Score"):
    fig = go.Figure()
    # Shaded area
    fig.add_trace(go.Scatter(
        x=x, y=y,
        fill="tozeroy",
        fillcolor="rgba(108,99,255,0.08)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False,
    ))
    # Main line
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode="lines+markers",
        line=dict(color="#6C63FF", width=2.5, shape="spline"),
        marker=dict(color="#6C63FF", size=7, line=dict(color="#1E1E35", width=2)),
        name=y_label,
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title  = dict(text=title, font=dict(size=14, color="#F1F0FF", family="Syne, sans-serif"), x=0),
        xaxis  = dict(**AXIS_STYLE),
        yaxis  = dict(**AXIS_STYLE, range=[0,110]),
        height = 220,
    )
    return fig


# ── Keyword density bar ───────────────────────────────────────────────────
def keyword_density_chart(data):
    """data: list of dicts with keys 'keyword', 'count', 'relevance'"""
    df = pd.DataFrame(data)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name        = "Frequency",
        y           = df["keyword"],
        x           = df["count"],
        orientation = "h",
        marker      = dict(color="#6C63FF", line=dict(width=0)),
        offsetgroup = 0,
    ))
    fig.add_trace(go.Bar(
        name        = "Relevance %",
        y           = df["keyword"],
        x           = df["relevance"],
        orientation = "h",
        marker      = dict(color="#00C9A7", line=dict(width=0)),
        offsetgroup = 1,
        visible     = "legendonly",
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        showlegend  = True,
        legend      = dict(font=dict(size=11, color="#A8A8C0"), bgcolor="rgba(0,0,0,0)", orientation="h", y=1.1),
        barmode     = "group",
        xaxis       = dict(**AXIS_STYLE),
        yaxis       = dict(tickcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)", tickfont=dict(size=11)),
        height      = 280,
        title       = dict(text="Keyword Density", font=dict(size=14, color="#F1F0FF", family="Syne, sans-serif"), x=0),
    )
    return fig


# ── Candidate comparison radar ────────────────────────────────────────────
def multi_radar(candidates_data, categories):
    """
    candidates_data: list of dicts {name: str, values: list[float]}
    categories: list of str
    """
    colors = ["#6C63FF","#00C9A7","#F59E0B","#EF4444"]
    fig = go.Figure()
    for i, c in enumerate(candidates_data):
        fig.add_trace(go.Scatterpolar(
            r     = c["values"] + [c["values"][0]],
            theta = categories + [categories[0]],
            name  = c["name"],
            fill  = "toself",
            line  = dict(color=colors[i % len(colors)], width=2),
            fillcolor = colors[i % len(colors)].replace(")", ",0.08)").replace("rgb(", "rgba(") if "rgb" in colors[i % len(colors)] else colors[i % len(colors)] + "14",
        ))
    fig.update_layout(
        **LAYOUT_BASE,
        showlegend = True,
        legend     = dict(font=dict(size=11, color="#A8A8C0"), bgcolor="rgba(0,0,0,0)"),
        polar      = dict(
            bgcolor     = "rgba(255,255,255,0.02)",
            radialaxis  = dict(range=[0,100], tickfont=dict(size=9), gridcolor=GRID_COLOR, linecolor=GRID_COLOR),
            angularaxis = dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR),
        ),
        height = 320,
        title  = dict(text="Candidate Comparison", font=dict(size=14, color="#F1F0FF", family="Syne, sans-serif"), x=0),
    )
    return fig


# ── Skill gap grouped bar ─────────────────────────────────────────────────
def skill_gap_chart(categories, have, need):
    fig = go.Figure()
    fig.add_trace(go.Bar(name="You have", x=categories, y=have, marker=dict(color="#6C63FF"), offsetgroup=0))
    fig.add_trace(go.Bar(name="Required", x=categories, y=need, marker=dict(color="rgba(255,255,255,0.1)",
                            line=dict(color="#A8A8C0", width=1.5, dash="dot")), offsetgroup=1))
    fig.update_layout(
        **LAYOUT_BASE,
        showlegend  = True,
        legend      = dict(font=dict(size=11, color="#A8A8C0"), bgcolor="rgba(0,0,0,0)", orientation="h", y=1.1),
        barmode     = "group",
        xaxis       = dict(tickcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)", tickfont=dict(size=11)),
        yaxis       = dict(**AXIS_STYLE, range=[0,110]),
        height      = 260,
        title       = dict(text="Skill Gap Analysis", font=dict(size=14, color="#F1F0FF", family="Syne, sans-serif"), x=0),
    )
    return fig