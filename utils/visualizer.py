"""
visualizer.py
Build Plotly charts for the Resume Screener UI.
"""

from typing import Set, Dict, Optional
import plotly.graph_objects as go
import plotly.express as px

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY    = "#0B1D3A"
BLUE    = "#1A56DB"
SKY     = "#EFF6FF"
SLATE   = "#64748B"
GREEN   = "#059669"
AMBER   = "#D97706"
RED     = "#DC2626"
WHITE   = "#FFFFFF"

PLOT_BG   = "rgba(0,0,0,0)"
PAPER_BG  = "rgba(0,0,0,0)"
FONT_FAM  = "DM Sans, sans-serif"


def _score_color(score: int) -> str:
    if score >= 70:
        return GREEN
    if score >= 45:
        return AMBER
    return RED


# ── Gauge ─────────────────────────────────────────────────────────────────────

def create_score_gauge(score: int) -> go.Figure:
    """Semicircular gauge showing the overall match score."""
    color = _score_color(score)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%", "font": {"size": 36, "color": NAVY, "family": FONT_FAM}},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": "#CBD5E1",
                "tickfont": {"size": 10, "color": SLATE},
            },
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": SKY,
            "borderwidth": 0,
            "steps": [
                {"range": [0,  45], "color": "#FEE2E2"},
                {"range": [45, 70], "color": "#FEF3C7"},
                {"range": [70, 100], "color": "#D1FAE5"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.8,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=10),
        height=200,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font={"family": FONT_FAM},
    )
    return fig


# ── Radar ─────────────────────────────────────────────────────────────────────

def create_skills_radar(
    resume_skills: Set[str],
    jd_skills: Set[str],
    max_skills: int = 10,
) -> Optional[go.Figure]:
    """Radar chart comparing resume skills to JD skills."""
    if not jd_skills:
        return None

    # Use the JD skills as the axes (capped for readability)
    axes = sorted(jd_skills)[:max_skills]
    resume_lower = {s.lower() for s in resume_skills}

    jd_vals     = [1.0] * len(axes)
    resume_vals = [1.0 if ax.lower() in resume_lower else 0.0 for ax in axes]

    # Close the polygon
    axes_closed        = axes + [axes[0]]
    jd_vals_closed     = jd_vals + [jd_vals[0]]
    resume_vals_closed = resume_vals + [resume_vals[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=jd_vals_closed,
        theta=axes_closed,
        fill="toself",
        name="Required",
        fillcolor="rgba(26,86,219,0.12)",
        line=dict(color=BLUE, width=2),
    ))
    fig.add_trace(go.Scatterpolar(
        r=resume_vals_closed,
        theta=axes_closed,
        fill="toself",
        name="Your Resume",
        fillcolor="rgba(5,150,105,0.18)",
        line=dict(color=GREEN, width=2, dash="dot"),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor=SKY,
            radialaxis=dict(visible=False, range=[0, 1.2]),
            angularaxis=dict(
                tickfont=dict(size=10, color=NAVY, family=FONT_FAM),
                linecolor="#DBEAFE",
            ),
        ),
        showlegend=True,
        legend=dict(font=dict(size=11, family=FONT_FAM, color=NAVY), x=0.8, y=1.1),
        margin=dict(l=50, r=50, t=30, b=30),
        height=300,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
    )
    return fig


# ── Score breakdown bar ───────────────────────────────────────────────────────

def create_skills_breakdown_chart(scores: Dict[str, int]) -> go.Figure:
    """Horizontal bar chart of the four sub-scores."""
    categories = ["Skills Match", "Experience Fit", "Education Fit", "TF-IDF Similarity"]
    values     = [scores["skills"], scores["experience"], scores["education"], scores["tfidf"]]
    colors     = [_score_color(v) for v in values]

    fig = go.Figure(go.Bar(
        x=values,
        y=categories,
        orientation="h",
        marker_color=colors,
        marker_line_width=0,
        text=[f"{v}%" for v in values],
        textposition="inside",
        insidetextfont=dict(color=WHITE, size=12, family=FONT_FAM),
        width=0.5,
    ))

    # Background "track" bars
    fig.add_trace(go.Bar(
        x=[100] * len(categories),
        y=categories,
        orientation="h",
        marker_color="#EFF6FF",
        marker_line_width=0,
        width=0.5,
        showlegend=False,
        hoverinfo="skip",
    ))

    fig.update_layout(
        barmode="overlay",
        xaxis=dict(
            range=[0, 100],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
        ),
        yaxis=dict(
            tickfont=dict(size=12, family=FONT_FAM, color=NAVY),
            showgrid=False,
        ),
        margin=dict(l=10, r=20, t=10, b=10),
        height=200,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
    )
    return fig
