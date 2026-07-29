"""
Competitor Agent
-------------------
Analyzes competitors found by the Web Search Agent, comparing
strengths/weaknesses and identifying market gaps.
"""

import json
from agents.idea_extraction_agent import client
from app.config import MODEL_NAME


def analyze_competitors(extracted: dict, search_results: dict) -> dict:
    results = search_results.get("results", [])[:5]
    context = [{"title": r.get("title", ""), "content": r.get("content", "")[:150]} for r in results]

    prompt = f"""
You are a competitive analyst. Based on this startup idea and the
search results below, identify likely competitors and market gaps.

Idea: {extracted.get('idea_name')}
Solution: {extracted.get('solution')}
Search context: {json.dumps(context)}

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
        return json.loads(text)
    except json.JSONDecodeError:
        return {"competitors": [], "market_gap": text}
