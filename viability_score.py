"""
Viability Score Agent
----------------------
Computes a single weighted score (0-100) summarizing how promising a
startup idea looks, based on outputs from the other agents.

Works today with just extraction + search agent outputs.
Designed to automatically use richer signals (market analysis, SWOT,
competitor data) once those agents are built, without breaking.
"""

from typing import Optional


def _score_competition_density(search_results: dict) -> float:
    """
    Fewer, weaker-matching competitor results suggest more white space.
    More, highly relevant results suggest a crowded market.
    Returns a 0-10 score where 10 = low competition (good), 0 = saturated.
    """
    results = search_results.get("results", []) if search_results else []
    if not results:
        return 7.0  # no data found could mean underexplored niche; treat as mildly positive

    count = len(results)
    avg_relevance = sum(r.get("score", 0) for r in results) / count

    # More results + higher relevance scores => more direct competition
    density_penalty = min(count / 10, 1.0) * 5  # 0-5 penalty from volume
    relevance_penalty = min(avg_relevance * 10, 5)  # 0-5 penalty from relevance

    score = 10 - density_penalty - relevance_penalty
    return max(0.0, min(10.0, score))


def _score_idea_clarity(extracted: dict) -> float:
    """
    Rewards ideas with a clearly defined problem, solution, and target
    customer. Penalizes vague or missing fields.
    Returns a 0-10 score.
    """
    if not extracted:
        return 0.0

    required_fields = [
        "problem", "solution", "target_customer",
        "industry", "business_model",
    ]
    present = 0
    for field in required_fields:
        value = extracted.get(field) or extracted.get(field.replace("_", " "))
        if value and isinstance(value, str) and len(value.strip()) > 15:
            present += 1

    return round((present / len(required_fields)) * 10, 1)


def _score_market_analysis(market_analysis: Optional[dict]) -> float:
    """
    Placeholder scoring hook for the future Market Analysis Agent.
    Expects market_analysis to eventually include a 'market_size_score'
    or similar signal (0-10). Falls back to a neutral score if absent.
    """
    if not market_analysis:
        return 5.0  # neutral until this agent exists
    return float(market_analysis.get("market_size_score", 5.0))


def _score_swot(swot: Optional[dict]) -> float:
    """
    Placeholder scoring hook for the future SWOT & Risk Agent.
    Expects swot to eventually include a 'risk_score' (0-10, where
    10 = low risk). Falls back to a neutral score if absent.
    """
    if not swot:
        return 5.0  # neutral until this agent exists
    return float(swot.get("risk_score", 5.0))


def calculate_viability_score(
    extracted: dict,
    search_results: dict,
    market_analysis: Optional[dict] = None,
    swot: Optional[dict] = None,
) -> dict:
    """
    Combines available signals into a single weighted viability score.

    Weights (sum to 100%):
      - Idea clarity:         20%
      - Competition density:  30%
      - Market analysis:      30%  (neutral 5/10 until agent exists)
      - SWOT / risk:          20%  (neutral 5/10 until agent exists)

    Returns a dict with the overall score, a letter-style verdict,
    and the individual component breakdown (useful for the dashboard
    and for explaining the score to the user).
    """
    clarity = _score_idea_clarity(extracted)
    competition = _score_competition_density(search_results)
    market = _score_market_analysis(market_analysis)
    risk = _score_swot(swot)

    weighted = (
        clarity * 0.20
        + competition * 0.30
        + market * 0.30
        + risk * 0.20
    )
    overall_score = round(weighted * 10, 1)  # scale 0-10 -> 0-100

    if overall_score >= 75:
        verdict = "Strong potential — worth pursuing"
    elif overall_score >= 55:
        verdict = "Moderate potential — needs refinement"
    else:
        verdict = "High risk — significant rework needed"

    return {
        "overall_score": overall_score,
        "verdict": verdict,
        "breakdown": {
            "idea_clarity": clarity,
            "competition_density": competition,
            "market_analysis": market,
            "swot_risk": risk,
        },
    }
