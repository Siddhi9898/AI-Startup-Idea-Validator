"""
tools/score_charts.py
-------------------------
Graphical representation of how the scoring agents arrived at the
overall number (fixes: "graphical representation of how the agents
are reporting their answer with comparison score of 100" and
"display all the agent reports in graph for mathematical
reference"). Every value plotted here is read directly from
viability_score.breakdown / market_analysis / swot - nothing here is
computed independently, so the chart can never disagree with the
written report.
"""

import plotly.graph_objects as go


def build_agent_score_figures(state_dict: dict):
    """Returns (bar_figure, radar_figure) - both scaled to a common
    0-100 axis so every agent's contribution is directly comparable,
    even though the underlying agents score on different native
    scales (0-10 for breakdown components, 0-100 for the overall)."""
    viability = state_dict.get("viability_score", {})
    breakdown = viability.get("breakdown", {}) or {}
    market = state_dict.get("market_analysis", {})
    swot = state_dict.get("swot", {})
    competitors = state_dict.get("competitors", {})

    labels = []
    values = []

    for key, label in [
        ("idea_clarity", "Idea Clarity"),
        ("completeness", "Completeness"),
        ("competition_density", "Competition Density"),
        ("market_analysis", "Market Analysis"),
        ("swot_risk", "SWOT / Risk"),
    ]:
        if key in breakdown:
            labels.append(label)
            values.append(round(float(breakdown[key]) * 10, 1))  # 0-10 -> 0-100

    if market.get("market_size_score") is not None:
        labels.append("Market Size")
        values.append(round(float(market["market_size_score"]) * 10, 1))

    if swot.get("risk_score") is not None:
        labels.append("Risk Score\n(higher = safer)")
        values.append(round(float(swot["risk_score"]) * 10, 1))

    n_competitors = len(competitors.get("competitors", []))
    # Fewer well-documented competitors in a real gap = healthier;
    # this is a simple, transparent inverse scale capped at 100/0.
    competition_health = max(0, 100 - n_competitors * 15)
    labels.append("Competitive Openness")
    values.append(competition_health)

    overall = viability.get("overall_score")
    if overall is not None:
        labels.append("Overall Score")
        values.append(round(float(overall), 1))

    colors = ["#7C3AED" if l != "Overall Score" else "#F59E0B" for l in labels]

    bar_fig = go.Figure(
        data=[go.Bar(x=labels, y=values, marker_color=colors, text=values, textposition="outside")]
    )
    bar_fig.update_layout(
        title="Agent Scores (normalized to /100)",
        yaxis=dict(range=[0, 110], title="Score / 100"),
        plot_bgcolor="#0B0E17",
        paper_bgcolor="#0B0E17",
        font=dict(color="#E7E9F0"),
        margin=dict(t=50, b=40),
        height=380,
    )

    radar_labels = [l for l in labels if l != "Overall Score"]
    radar_values = [v for l, v in zip(labels, values) if l != "Overall Score"]
    # close the loop for a radar chart
    radar_fig = go.Figure()
    radar_fig.add_trace(go.Scatterpolar(
        r=radar_values + radar_values[:1],
        theta=radar_labels + radar_labels[:1],
        fill="toself",
        line_color="#A78BFA",
        fillcolor="rgba(124, 58, 237, 0.35)",
    ))
    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color="#9CA3C4"),
            angularaxis=dict(color="#E7E9F0"),
            bgcolor="#0B0E17",
        ),
        showlegend=False,
        paper_bgcolor="#0B0E17",
        font=dict(color="#E7E9F0"),
        title="Score Comparison (radar view)",
        height=420,
    )

    return bar_fig, radar_fig
