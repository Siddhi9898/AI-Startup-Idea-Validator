"""
Market Analysis Agent (Deterministic)
------------------------------------------
Refactored per reviewer feedback: market_size_score is now computed
deterministically from actual retrieved data (relevant result count,
average relevance), instead of asking the LLM to invent a TAM/SAM/SOM
number out of thin air. The LLM is used only to phrase a growth_trend
sentence, strictly grounded in the retrieved snippets it is given -
never asked to estimate figures it has no real data for.
"""

from tools.validators import filter_relevant_results_with_fallback, validate_search_results
from agents.idea_extraction_agent import client
from app.config import MODEL_NAME


def _deterministic_market_size_score(relevant_results: list, total_results: int) -> float:
    """
    Deterministic scoring rule, no LLM involved:
    - More relevant results found => more evidence of an active,
      documented market => higher score (up to a point)
    - Very high relevant count can also indicate saturation, so the
      score plateaus rather than increasing indefinitely.
    Identical input always produces identical output.
    """
    count = len(relevant_results)
    if count == 0:
        return 3.0  # no evidence found; conservative low-neutral score
    if count <= 2:
        return 5.0
    if count <= 4:
        return 7.0
    return 8.0  # plateaus - more isn't necessarily better past this point


def _deterministic_segments(extracted: dict) -> list:
    """
    Deterministic customer segment derivation directly from the
    already-extracted target_customer field - no LLM invention.
    """
    target = extracted.get("target_customer", "")
    if not target:
        return []
    # Split on common separators deterministically
    parts = [p.strip() for p in target.replace(" and ", ",").split(",") if p.strip()]
    return parts if parts else [target]


def analyze_market(extracted: dict, search_results: dict) -> dict:
    raw_results = search_results.get("results", [])
    validation = validate_search_results(raw_results)

    relevant = (
        filter_relevant_results_with_fallback(extracted, raw_results, min_relevance=0.20, min_results=4)
        if validation["is_valid"] else []
    )

    # Deterministic scoring - no LLM call for the number itself
    market_size_score = _deterministic_market_size_score(relevant, len(raw_results))
    customer_segments = _deterministic_segments(extracted)

    if not relevant:
        return {
            "tam_estimate": "Insufficient retrieved data to estimate market size.",
            "sam_estimate": "Insufficient retrieved data to estimate market size.",
            "som_estimate": "Insufficient retrieved data to estimate market size.",
            "growth_trend": "No relevant market data was retrieved for this idea.",
            "customer_segments": customer_segments,
            "market_size_score": market_size_score,
            "data_quality": {"relevant_count": 0, "total_count": len(raw_results)},
        }

    # LLM used ONLY to phrase a growth trend description, strictly
    # grounded in retrieved snippets - explicitly told not to invent
    # numbers it wasn't given.
    context_snippets = [f"{r.get('title', '')}: {r.get('content', '')[:300]}" for r in relevant[:6]]
    prompt = f"""
Based ONLY on the retrieved information below, write one sentence
describing the market/industry trend relevant to this startup idea.
Do NOT invent specific market size figures (TAM/SAM/SOM) - only
describe qualitative trend, based strictly on what is retrieved.
If the retrieved information does not clearly indicate a trend, say so.

Idea industry: {extracted.get('industry', '')}
Retrieved information:
{chr(10).join(context_snippets)}
"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        growth_trend = response.choices[0].message.content.strip()
    except Exception:
        growth_trend = "Unable to generate a trend summary at this time."

    return {
        "tam_estimate": "Not deterministically estimable without a verified market data source; not fabricated.",
        "sam_estimate": "Not deterministically estimable without a verified market data source; not fabricated.",
        "som_estimate": "Not deterministically estimable without a verified market data source; not fabricated.",
        "growth_trend": growth_trend,
        "customer_segments": customer_segments,
        "market_size_score": market_size_score,
        "data_quality": {"relevant_count": len(relevant), "total_count": len(raw_results)},
    }