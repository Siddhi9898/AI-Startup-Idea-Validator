"""
Summary Agent
----------------
Fixes P2: instead of making the founder read every single agent's
full output to piece together the picture, this condenses everything
into one up-front summary. Deterministic facts are pulled directly
from already-computed data across EVERY agent (not just viability/
competitors/swot/mvp as before); the LLM is used only to phrase them
into readable prose - not to invent new analysis.

Update: the summary was judged "too thin" - it only ever pulled from
4 of the ~10 agents' outputs. It now also draws on market analysis
(growth trend, market size), GTM positioning, the elevator pitch,
funding suggestions, and blind spots, and produces a fuller
paragraph (6-8 sentences) covering idea, market, competition, risk,
what to build first, how to go to market, and how to fund it -
still strictly grounded in already-computed facts, nothing invented.
"""

from agents.idea_extraction_agent import client
from app.config import MODEL_NAME


def _gather_facts(state_dict: dict) -> dict:
    extracted = state_dict.get("extracted", {})
    viability = state_dict.get("viability_score", {})
    competitors = state_dict.get("competitors", {})
    swot = state_dict.get("swot", {})
    mvp = state_dict.get("mvp", {})
    market = state_dict.get("market_analysis", {})
    gtm = state_dict.get("gtm", {})
    pitch = state_dict.get("elevator_pitch", {})
    funding = state_dict.get("funding_suggestions", [])
    blind_spots = state_dict.get("blind_spots", [])

    # Deterministic facts pulled from EVERY already-computed agent
    # output - nothing here is invented, just gathered.
    return {
        "idea_name": extracted.get("idea_name", "this idea"),
        "industry": extracted.get("industry", ""),
        "score": viability.get("overall_score"),
        "verdict": viability.get("verdict"),
        "competitor_count": len(competitors.get("competitors", [])),
        "market_gap": competitors.get("market_gap", ""),
        "growth_trend": market.get("growth_trend", ""),
        "market_size_score": market.get("market_size_score"),
        "top_strength": (swot.get("strengths") or ["none identified"])[0],
        "top_weakness": (swot.get("weaknesses") or ["none identified"])[0],
        "risk_score": swot.get("risk_score"),
        "top_mvp_feature": (mvp.get("mvp_features") or [{}])[0].get("feature", "not determined"),
        "mvp_timeline": mvp.get("estimated_timeline", ""),
        "positioning": gtm.get("positioning_statement", ""),
        "pricing_strategy": gtm.get("pricing_strategy", ""),
        "tagline": pitch.get("tagline", ""),
        "top_funding_path": (funding[0].get("funding_type") if funding else "not determined"),
        "blind_spot_count": len(blind_spots),
    }


def generate_quick_summary(state_dict: dict) -> str:
    facts = _gather_facts(state_dict)

    prompt = f"""
Write a clear, scannable summary (6-8 sentences, one paragraph) of
this startup validation, using ONLY the facts below - do not add
new analysis, numbers, or claims beyond what's given here. Cover, in
order: (1) what the idea is and its viability verdict, (2) what the
market/competitive picture looks like, (3) the single biggest
strength and biggest weakness, (4) what to build first and roughly
how long it takes, (5) the recommended go-to-market angle, and (6)
the most realistic funding path. End with how many open questions
("blind spots") the founder still needs to answer.

Idea: {facts['idea_name']} ({facts['industry']})
Viability Score: {facts['score']}/100 - {facts['verdict']}
Competitors found: {facts['competitor_count']} | Market gap note: {facts['market_gap']}
Market growth trend: {facts['growth_trend']} | Market size score: {facts['market_size_score']}/10
Top strength: {facts['top_strength']}
Top weakness: {facts['top_weakness']}
Risk score: {facts['risk_score']}/10
Top MVP priority: {facts['top_mvp_feature']} | Estimated build time: {facts['mvp_timeline']}
GTM positioning: {facts['positioning']} | Pricing approach: {facts['pricing_strategy']}
Tagline: {facts['tagline']}
Most realistic funding path: {facts['top_funding_path']}
Number of unresolved blind spots: {facts['blind_spot_count']}

Write it as a briefing a busy founder could read in under 30 seconds
instead of reading every section below, but dense enough that they
walk away actually informed, not just reassured.
"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        # Deterministic fallback if the LLM call fails - still pulls
        # from every agent, just without LLM phrasing.
        return (
            f"{facts['idea_name']} ({facts['industry']}) scored {facts['score']}/100 "
            f"({facts['verdict']}). {facts['competitor_count']} competitors found; "
            f"market growth trend: {facts['growth_trend'] or 'not determined'}. "
            f"Top strength: {facts['top_strength']}. Top weakness: {facts['top_weakness']} "
            f"(risk score {facts['risk_score']}/10). "
            f"Build first: {facts['top_mvp_feature']} ({facts['mvp_timeline']}). "
            f"GTM: {facts['positioning'] or 'not determined'}. "
            f"Most realistic funding path: {facts['top_funding_path']}. "
            f"{facts['blind_spot_count']} open blind spot(s) remain."
        )