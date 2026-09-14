"""
Suggestion Agent
-------------------
Fixes: "after the input is displayed there should be a suggestion
box where the user can get AI suggestions to improve this
particular idea."

Distinct from the Insight Agent's blind_spots (which are posed as
open QUESTIONS the founder hasn't answered) - this produces direct,
actionable RECOMMENDATIONS grounded in what's already been computed
(weaknesses, risk score, market gap, verdict) - not new invented
analysis.
"""

import json

from agents.idea_extraction_agent import client
from app.config import MODEL_NAME


def generate_improvement_suggestions(state_dict: dict) -> list:
    extracted = state_dict.get("extracted", {})
    swot = state_dict.get("swot", {})
    viability = state_dict.get("viability_score", {})
    competitors = state_dict.get("competitors", {})
    market = state_dict.get("market_analysis", {})

    facts = {
        "idea_name": extracted.get("idea_name", ""),
        "verdict": viability.get("verdict", ""),
        "weaknesses": swot.get("weaknesses", []),
        "threats": swot.get("threats", []),
        "risk_score": swot.get("risk_score"),
        "market_gap": competitors.get("market_gap", ""),
        "growth_trend": market.get("growth_trend", ""),
    }

    prompt = f"""
Based ONLY on the facts below (do not invent new facts), write 3-5
short, concrete, actionable suggestions for how this founder could
improve their startup idea's viability. Each suggestion should be
one sentence, specific enough to actually act on (not generic advice
like "do more research"). Ground every suggestion in one of the
facts given.

Idea: {facts['idea_name']}
Current verdict: {facts['verdict']}
Weaknesses identified: {facts['weaknesses']}
Threats identified: {facts['threats']}
Risk score: {facts['risk_score']}/10
Market gap: {facts['market_gap']}
Market growth trend: {facts['growth_trend']}

Respond ONLY as a JSON list of strings, nothing else.
"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.lower().startswith("json"):
                content = content[4:].strip()
        suggestions = json.loads(content)
        if isinstance(suggestions, list) and suggestions:
            return [str(s) for s in suggestions][:5]
    except Exception:
        pass

    # Deterministic fallback - still grounded in the same facts,
    # just without LLM phrasing, so the suggestion box is never empty.
    fallback = []
    for w in facts["weaknesses"][:2]:
        fallback.append(f"Address this weakness directly: {w}")
    if facts["market_gap"]:
        fallback.append(f"Lean into the identified market gap: {facts['market_gap']}")
    if not fallback:
        fallback.append("Validate demand with 10-15 real conversations with your target customer before building.")
    return fallback
