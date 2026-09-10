"""
Viability Score Agent (Fully Deterministic)
-----------------------------------------------
No LLM calls anywhere in this file - pure rule-based scoring, as
requested by the reviewer. Expanded with an explicit completeness
score component alongside the existing clarity/competition/market/
risk components, all combined with fixed weights.
"""

from typing import Optional


def _score_completeness(extracted: dict) -> float:
    """
    Deterministic completeness score: fraction of expected fields
    that are present and non-trivial. Distinct from clarity (which
    also checks minimum length) - this checks raw presence.
    """
    if not extracted:
        return 0.0
    fields = ["idea_name", "problem", "solution", "target_customer", "industry", "business_model"]
    present = sum(1 for f in fields if extracted.get(f))
    return round((present / len(fields)) * 10, 1)


def _score_idea_clarity(extracted: dict) -> float:
    if not extracted:
        return 0.0
    required_fields = ["problem", "solution", "target_customer", "industry", "business_model"]
    present = 0
    for field in required_fields:
        value = extracted.get(field)
        if value and isinstance(value, str) and len(value.strip()) > 15:
            present += 1
    return round((present / len(required_fields)) * 10, 1)


def _score_competition_density(search_results: dict) -> float:
    results = search_results.get("results", []) if search_results else []
    if not results:
        return 7.0
    count = len(results)
    avg_relevance = sum(r.get("relevance", r.get("score", 0)) for r in results) / count
    density_penalty = min(count / 10, 1.0) * 5
    relevance_penalty = min(avg_relevance * 10, 5)
    score = 10 - density_penalty - relevance_penalty
    return max(0.0, min(10.0, score))


def _score_market_analysis(market_analysis: Optional[dict]) -> float:
    if not market_analysis:
        return 5.0
    return float(market_analysis.get("market_size_score", 5.0))


def _score_swot(swot: Optional[dict]) -> float:
    if not swot:
        return 5.0
    return float(swot.get("risk_score", 5.0))


def calculate_viability_score(
    extracted: dict,
    search_results: dict,
    market_analysis: Optional[dict] = None,
    swot: Optional[dict] = None,
) -> dict:
    """
    Fully deterministic weighted score. Weights (sum to 100%):
      - Completeness:          10%
      - Idea clarity:          15%
      - Competition density:   25%
      - Market analysis:       30%
      - SWOT / risk:           20%
    """
    completeness = _score_completeness(extracted)
    clarity = _score_idea_clarity(extracted)
    competition = _score_competition_density(search_results)
    market = _score_market_analysis(market_analysis)
    risk = _score_swot(swot)

    weighted = (
        completeness * 0.10
        + clarity * 0.15
        + competition * 0.25
        + market * 0.30
        + risk * 0.20
    )
    overall_score = round(weighted * 10, 1)

    if overall_score >= 75:
        verdict = "Strong potential - worth pursuing"
    elif overall_score >= 55:
        verdict = "Moderate potential - needs refinement"
    else:
        verdict = "High risk - significant rework needed"

    return {
        "overall_score": overall_score,
        "verdict": verdict,
        "breakdown": {
            "completeness": completeness,
            "idea_clarity": clarity,
            "competition_density": competition,
            "market_analysis": market,
            "swot_risk": risk,
        },
    }
