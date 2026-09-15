"""
Competitor Agent (Deep Search version)
-------------------------------------------
Now runs its own targeted deep search specifically for named
competitors, instead of only reusing the Web Search Agent's
general market/competitor results.
"""

import json
from agents.idea_extraction_agent import client
from app.config import MODEL_NAME
from tools.deep_search import deep_search


def analyze_competitors(extracted: dict, search_results: dict) -> dict:
    idea_name = extracted.get("idea_name", "")
    industry = extracted.get("industry", "")
    location = extracted.get("location", "Global")

    primary_query = f"top competitors {idea_name} {industry} {location}"
    fallback_query = f"companies similar to {industry} startups {location}"
    competitor_search_results = deep_search(primary_query, fallback_query)

    context = [
        {"title": r.get("title", ""), "content": r.get("snippet", "")[:150]}
        for r in competitor_search_results
    ]

    prompt = f"""
You are a competitive analyst. Based on this startup idea and the
targeted competitor search results below, identify likely competitors
and market gaps.

Idea: {idea_name}
Solution: {extracted.get('solution')}
Location/Market: {location}
Competitor search context: {json.dumps(context)}

Return ONLY valid JSON with this format:
{{
  "competitors": [
    {{"name": "...", "strength": "...", "weakness": "..."}}
  ],
  "market_gap": "one sentence describing an opportunity gap this startup could exploit"
}}
If the search context does not clearly name specific companies, infer
plausible competitor types instead (e.g. "established players in X category").
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
        result = {"competitors": [], "market_gap": text}

    result["competitor_search_sources"] = [
        {"title": r.get("title", ""), "url": r.get("url", "")}
        for r in competitor_search_results[:5]
    ]
    return result
