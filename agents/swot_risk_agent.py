"""
SWOT & Risk Agent (Deep Search version)
--------------------------------------------
Now runs its own targeted deep search specifically for industry
risks and common startup failure patterns, instead of only
reasoning over Market Analysis and Competitor outputs.
"""

import json
from agents.idea_extraction_agent import client
from app.config import MODEL_NAME
from tools.deep_search import deep_search


def analyze_swot(extracted: dict, market_analysis: dict, competitors: dict) -> dict:
    industry = extracted.get("industry", "")
    location = extracted.get("location", "Global")

    primary_query = f"{industry} startup risks challenges {location}"
    fallback_query = f"why {industry} startups fail common mistakes"
    risk_search_results = deep_search(primary_query, fallback_query)
    risk_context = [r.get("title", "") for r in risk_search_results][:5]

    prompt = f"""
You are a strategy consultant. Based on this startup idea, market
analysis, competitor data, and real-world risk search context below,
produce a SWOT analysis and a risk score.

Idea: {extracted.get('idea_name')}
Problem: {extracted.get('problem')}
Solution: {extracted.get('solution')}
Location/Market: {location}
Market growth trend: {market_analysis.get('growth_trend', 'unknown')}
Competitor gap: {competitors.get('market_gap', 'unknown')}
Real-world risk context found online: {risk_context}

Return ONLY valid JSON with this format:
{{
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "opportunities": ["...", "..."],
  "threats": ["...", "..."],
  "risk_score": <number 0-10, where 10 = very low risk>
}}
"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "")
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        result = {
            "strengths": [], "weaknesses": [], "opportunities": [],
            "threats": [], "risk_score": 5.0,
        }

    result["risk_search_sources"] = [
        {"title": r.get("title", ""), "url": r.get("url", "")}
        for r in risk_search_results[:5]
    ]
    return result
