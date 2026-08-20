"""
SWOT & Risk Agent (Rule-Based / Deterministic)
----------------------------------------------------
Refactored per reviewer feedback: SWOT points and the risk_score are
now derived from fixed rules applied to structured signals already
present in the shared context (competitor count, market_size_score,
idea completeness) - not invented freely by the LLM. The LLM is used
only, optionally, to smooth the wording of already-decided points.
"""

from agents.idea_extraction_agent import client
from app.config import MODEL_NAME


def _derive_swot_points(extracted: dict, market_analysis: dict, competitors: dict) -> dict:
    """
    Deterministic rule-based SWOT derivation. Identical input always
    produces identical output - no LLM involved in this function.
    """
    strengths = []
    weaknesses = []
    opportunities = []
    threats = []

    competitor_count = len(competitors.get("competitors", []))
    market_score = market_analysis.get("market_size_score", 5.0)

    # Rule: clearly defined problem/solution = strength
    if extracted.get("problem") and len(extracted.get("problem", "")) > 20:
        strengths.append("Clearly defined problem statement")
    if extracted.get("solution") and len(extracted.get("solution", "")) > 20:
        strengths.append("Clearly articulated solution approach")

    # Rule: low competitor count = opportunity (market gap);
    # high competitor count = threat (crowded market)
    if competitor_count == 0:
        opportunities.append("Low documented competition found - potential underexplored niche")
    elif competitor_count >= 4:
        threats.append("Multiple existing competitors identified in the same space")
    else:
        opportunities.append("Moderate competition suggests validated demand with room to differentiate")

    # Rule: market score thresholds
    if market_score >= 7:
        opportunities.append("Retrieved data indicates active market interest in this space")
    elif market_score <= 4:
        weaknesses.append("Limited retrieved evidence of existing market activity for this idea")

    # Rule: missing business model = weakness
    if not extracted.get("business_model"):
        weaknesses.append("Business model not clearly defined")

    # Rule: always-applicable structural threat for early-stage ideas
    threats.append("Execution risk typical of early-stage ventures (funding, timing, team)")

    return {
        "strengths": strengths or ["Idea has a defined target customer"],
        "weaknesses": weaknesses or ["No major structural weaknesses identified from available data"],
        "opportunities": opportunities or ["Opportunity assessment limited by available data"],
        "threats": threats,
    }


def _deterministic_risk_score(swot_points: dict, market_analysis: dict) -> float:
    """
    Deterministic risk score (0-10, 10 = low risk), computed from
    fixed rules based on the SWOT point counts and market score.
    No LLM involved.
    """
    score = 5.0
    score += 0.5 * len(swot_points["strengths"])
    score += 0.3 * len(swot_points["opportunities"])
    score -= 0.5 * len(swot_points["weaknesses"])
    score -= 0.5 * len(swot_points["threats"])
    score += (market_analysis.get("market_size_score", 5.0) - 5.0) * 0.3
    return round(max(0.0, min(10.0, score)), 1)


def analyze_swot(extracted: dict, market_analysis: dict, competitors: dict) -> dict:
    # Deterministic derivation first - this IS the agent's core logic
    swot_points = _derive_swot_points(extracted, market_analysis, competitors)
    risk_score = _deterministic_risk_score(swot_points, market_analysis)

    # LLM used ONLY, optionally, to smooth wording of ALREADY-DECIDED
    # points - it cannot add, remove, or invent new points.
    try:
        prompt = f"""
Rewrite each of these already-determined points in clearer, more
natural business language. Do NOT add, remove, or invent new points -
only rephrase what is given. Return ONLY valid JSON with the same
structure and same number of items per list.

{swot_points}
"""
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        import json
        text = response.choices[0].message.content.strip().replace("```json", "").replace("```", "")
        reworded = json.loads(text)
        # Safety check: only accept if structure matches (same keys, same counts)
        if all(k in reworded and len(reworded[k]) == len(swot_points[k]) for k in swot_points):
            swot_points = reworded
    except Exception:
        pass  # fall back to the deterministic, rule-based wording - never fail the pipeline

    return {
        **swot_points,
        "risk_score": risk_score,
    }
