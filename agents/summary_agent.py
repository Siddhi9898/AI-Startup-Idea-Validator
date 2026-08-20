"""
Summary Agent
----------------
Condenses the full validation run into ONE scannable executive
summary up front, so the founder isn't forced to read every single
agent's full output to piece the picture together.

Previously this only pulled 5 facts (score, verdict, competitor
count, top weakness, top MVP feature) into a single 3-4 sentence
paragraph - which meant market size, growth trend, competitive
intensity, GTM positioning, funding path, and most of the SWOT never
made it into the summary at all. This version pulls from every
agent's output and organizes it into labeled sections, so the
summary is genuinely comprehensive while still being quick to scan
(it's headers + short bullets, not a wall of text).

Every fact below is pulled directly from already-computed data; the
LLM is only used to phrase them into readable prose - never to
invent new analysis or numbers it wasn't given.
"""

from agents.idea_extraction_agent import client
from app.config import MODEL_NAME


def _top(items, n=2, default="none identified"):
    items = items or []
    return items[:n] if items else [default]


def generate_quick_summary(state_dict: dict) -> str:
    extracted = state_dict.get("extracted", {})
    viability = state_dict.get("viability_score", {})
    market = state_dict.get("market_analysis", {})
    competitors_data = state_dict.get("competitors", {})
    swot = state_dict.get("swot", {})
    mvp = state_dict.get("mvp", {})
    gtm = state_dict.get("gtm", {})
    funding = state_dict.get("funding_suggestions", [])
    blind_spots = state_dict.get("blind_spots", [])
    elevator = state_dict.get("elevator_pitch", {}) or {}

    breakdown = viability.get("breakdown", {})
    competitors_list = competitors_data.get("competitors", [])
    mvp_features = mvp.get("mvp_features", [])

    # Deterministic facts pulled directly from already-computed agent
    # outputs - the LLM only phrases these, it doesn't add to them.
    facts = {
        "idea_name": extracted.get("idea_name", "This idea"),
        "score": viability.get("overall_score"),
        "verdict": viability.get("verdict"),
        "breakdown": breakdown,
        "market_size_score": market.get("market_size_score"),
        "growth_trend": market.get("growth_trend"),
        "customer_segments": _top(market.get("customer_segments"), 2, "not determined"),
        "competitor_count": len(competitors_list),
        "top_competitors": [c.get("name") for c in competitors_list[:2] if c.get("name")],
        "market_gap": competitors_data.get("market_gap"),
        "competitive_intensity": competitors_data.get("competitive_intensity"),
        "top_strengths": _top(swot.get("strengths"), 2),
        "top_weaknesses": _top(swot.get("weaknesses"), 2),
        "top_opportunities": _top(swot.get("opportunities"), 1),
        "top_threat": _top(swot.get("threats"), 1),
        "risk_score": swot.get("risk_score"),
        "top_mvp_features": [f.get("feature") for f in mvp_features[:3] if f.get("feature")],
        "mvp_timeline": mvp.get("estimated_timeline"),
        "positioning": gtm.get("positioning_statement"),
        "top_channel": (gtm.get("marketing_channels") or ["not determined"])[0],
        "pricing_strategy": gtm.get("pricing_strategy"),
        "funding_pick": funding[0] if funding else None,
        "blind_spot_count": len(blind_spots),
        "tagline": elevator.get("tagline"),
    }

    prompt = f"""
Write a scannable executive summary of this startup validation for a
busy founder. Use ONLY the facts below - do not add new analysis,
numbers, or claims beyond what's given. If a fact is missing or says
"not determined", either omit it gracefully or say it's not yet
determined - never invent a substitute.

Format it with these short bold section headers, each followed by
1-3 sentences or bullet points (not long paragraphs):

**Bottom Line** - overall score/verdict and whether this is worth pursuing
**Market & Competition** - market size score, growth trend, competitor count, competitive intensity, market gap
**Strengths & Weaknesses** - top strengths and weaknesses from the SWOT, plus the risk score
**Next Steps** - top MVP features + timeline, GTM positioning + main channel, and the recommended funding path

Facts:
- Idea: {facts['idea_name']} ({facts['tagline'] or 'no tagline'})
- Viability Score: {facts['score']}/100 - {facts['verdict']}
- Score breakdown: {facts['breakdown']}
- Market size score: {facts['market_size_score']} | Growth trend: {facts['growth_trend']}
- Customer segments: {', '.join(facts['customer_segments'])}
- Competitors found: {facts['competitor_count']} (e.g. {', '.join(facts['top_competitors']) or 'none named'})
- Competitive intensity: {facts['competitive_intensity']} | Market gap: {facts['market_gap']}
- Top strengths: {', '.join(facts['top_strengths'])}
- Top weaknesses: {', '.join(facts['top_weaknesses'])}
- Top opportunity: {', '.join(facts['top_opportunities'])}
- Top threat: {', '.join(facts['top_threat'])}
- Risk score (0-10, higher = lower risk): {facts['risk_score']}
- Top MVP features to build first: {', '.join(facts['top_mvp_features']) or 'not determined'}
- Estimated MVP timeline: {facts['mvp_timeline']}
- GTM positioning: {facts['positioning']}
- Main marketing channel: {facts['top_channel']}
- Pricing strategy: {facts['pricing_strategy']}
- Recommended funding path: {facts['funding_pick']}
- Unaddressed blind spots flagged: {facts['blind_spot_count']}
"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        # Deterministic fallback if the LLM call fails - still
        # covers every section above, just without LLM phrasing.
        lines = [
            f"**Bottom Line**: {facts['score']}/100 ({facts['verdict']}) for {facts['idea_name']}.",
            "",
            "**Market & Competition**: "
            f"Market size score {facts['market_size_score']}, growth trend: {facts['growth_trend']}. "
            f"{facts['competitor_count']} competitors found "
            f"({', '.join(facts['top_competitors']) or 'none named'}), "
            f"competitive intensity: {facts['competitive_intensity']}. "
            f"Market gap: {facts['market_gap']}.",
            "",
            "**Strengths & Weaknesses**: "
            f"Strengths - {', '.join(facts['top_strengths'])}. "
            f"Weaknesses - {', '.join(facts['top_weaknesses'])}. "
            f"Risk score: {facts['risk_score']}/10.",
            "",
            "**Next Steps**: "
            f"Build first - {', '.join(facts['top_mvp_features']) or 'not determined'} "
            f"(timeline: {facts['mvp_timeline']}). "
            f"GTM: {facts['positioning']} via {facts['top_channel']}. "
            f"Funding path: {facts['funding_pick']}.",
        ]
        return "\n".join(lines)