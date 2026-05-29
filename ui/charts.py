import pandas as pd
import plotly.graph_objects as go


COLORS = ["#2563eb", "#059669", "#d97706", "#4f46e5", "#dc2626", "#0891b2"]
GRID = "rgba(17, 24, 39, 0.08)"


def _layout(height=300, showlegend=False):
    return dict(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", color="#344054", size=12),
        margin=dict(t=28, r=18, b=26, l=18),
        showlegend=showlegend,
        legend=dict(orientation="h", y=1.08, x=0, bgcolor="rgba(0,0,0,0)"),
    )


def gauge_chart(value, title="ATS Score", reference=70):
    value = max(0, min(100, float(value or 0)))
    color = "#059669" if value >= 80 else "#2563eb" if value >= 65 else "#d97706" if value >= 45 else "#dc2626"
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=value,
            delta=dict(reference=reference),
            title=dict(text=title, font=dict(size=14, color="#111827")),
            gauge=dict(
                axis=dict(range=[0, 100], tickwidth=0, tickcolor="#98a2b3"),
                bar=dict(color=color, thickness=.36),
                bgcolor="#eef2f7",
                borderwidth=0,
                steps=[
                    dict(range=[0, 45], color="#fef2f2"),
                    dict(range=[45, 65], color="#fffaeb"),
                    dict(range=[65, 80], color="#eff6ff"),
                    dict(range=[80, 100], color="#ecfdf3"),
                ],
                threshold=dict(line=dict(color="#111827", width=2), thickness=.72, value=reference),
            ),
        )
    )
    fig.update_layout(**_layout(height=278))
    return fig


def radar_chart(categories, values, title="Score Breakdown"):
    cats = list(categories)
    vals = [float(v or 0) for v in values]
    if cats and vals:
        cats = cats + [cats[0]]
        vals = vals + [vals[0]]
    fig = go.Figure(
        go.Scatterpolar(
            r=vals,
            theta=cats,
            fill="toself",
            line=dict(color="#2563eb", width=2),
            fillcolor="rgba(37, 99, 235, .14)",
        )
    )
    fig.update_layout(
        **_layout(height=320),
        title=dict(text=title, x=0, font=dict(size=14, color="#111827")),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 100], gridcolor=GRID, linecolor=GRID),
            angularaxis=dict(gridcolor=GRID, linecolor=GRID),
        ),
    )
    return fig


def hbar_chart(labels, values, title=""):
    labels = list(labels)
    values = [float(v or 0) for v in values]
    fig = go.Figure(
        go.Bar(
            y=labels,
            x=values,
            orientation="h",
            marker=dict(color=COLORS[: len(labels)]),
            text=[f"{v:.0f}%" for v in values],
            textposition="outside",
        )
    )
    fig.update_layout(
        **_layout(height=max(250, len(labels) * 42)),
        title=dict(text=title, x=0, font=dict(size=14, color="#111827")),
        xaxis=dict(range=[0, 110], gridcolor=GRID, zeroline=False),
        yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)"),
    )
    return fig


def donut_chart(labels, values, title=""):
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=.62,
            marker=dict(colors=COLORS[: len(labels)], line=dict(width=0)),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>%{value}<extra></extra>",
        )
    )
    fig.update_layout(
        **_layout(height=300, showlegend=True),
        title=dict(text=title, x=0, font=dict(size=14, color="#111827")),
    )
    return fig


def line_chart(x, y, title="Trend"):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines+markers",
            line=dict(color="#2563eb", width=3, shape="spline"),
            marker=dict(size=7, color="#2563eb"),
            fill="tozeroy",
            fillcolor="rgba(37, 99, 235, .10)",
        )
    )
    fig.update_layout(
        **_layout(height=260),
        title=dict(text=title, x=0, font=dict(size=14, color="#111827")),
        xaxis=dict(gridcolor=GRID, zeroline=False),
        yaxis=dict(range=[0, 100], gridcolor=GRID, zeroline=False),
    )
    return fig


def keyword_density_chart(data):
    df = pd.DataFrame(data or [], columns=["keyword", "count", "relevance"])
    if df.empty:
        df = pd.DataFrame({"keyword": ["No keywords"], "count": [0], "relevance": [0]})
    fig = go.Figure(
        go.Bar(
            y=df["keyword"],
            x=df["relevance"],
            orientation="h",
            marker=dict(color="#2563eb"),
            text=[f"{v:.0f}%" for v in df["relevance"]],
            textposition="outside",
        )
    )
    fig.update_layout(
        **_layout(height=max(240, len(df) * 42)),
        title=dict(text="Keyword Relevance", x=0, font=dict(size=14, color="#111827")),
        xaxis=dict(range=[0, 110], gridcolor=GRID, zeroline=False),
        yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)"),
    )
    return fig


def skill_gap_chart(categories, have, need):
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Candidate", x=categories, y=have, marker=dict(color="#2563eb")))
    fig.add_trace(go.Bar(name="Target", x=categories, y=need, marker=dict(color="#d0d5dd")))
    fig.update_layout(
        **_layout(height=290, showlegend=True),
        barmode="group",
        title=dict(text="Skill Gap Analysis", x=0, font=dict(size=14, color="#111827")),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(range=[0, 100], gridcolor=GRID, zeroline=False),
    )
    return fig
