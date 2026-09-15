"""
MVP Recommendation Agent (Deep Search version)
----------------------------------------------------
Now runs its own targeted deep search for similar products' feature
sets and common MVP patterns in this industry, instead of only
reasoning from the SWOT weaknesses alone.
"""

import json
from agents.idea_extraction_agent import client
from app.config import MODEL_NAME
from tools.deep_search import deep_search


def recommend_mvp(extracted: dict, swot: dict) -> dict:
    industry = extracted.get("industry", "")
    location = extracted.get("location", "Global")

    primary_query = f"MVP features {industry} apps {location}"
    fallback_query = f"core features successful {industry} startups"
    mvp_search_results = deep_search(primary_query, fallback_query)
    mvp_context = [r.get("title", "") for r in mvp_search_results][:5]

    prompt = f"""
You are a product manager. Based on this startup idea, its SWOT
analysis, and real-world context on similar products below,
recommend a prioritized MVP feature set.

Idea: {extracted.get('idea_name')}
Solution: {extracted.get('solution')}
Target Customer: {extracted.get('target_customer')}
Key weaknesses to address: {swot.get('weaknesses', [])}
Similar product context found online: {mvp_context}

Return ONLY valid JSON with this format:
{{
  "mvp_features": [
    {{"priority": "High", "feature": "..."}},
    {{"priority": "Medium", "feature": "..."}},
    {{"priority": "Low", "feature": "..."}}
  ],
  "estimated_timeline": "short estimate, e.g. '6-8 weeks for MVP'"
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
        result = {"mvp_features": [], "estimated_timeline": text}

    result["mvp_search_sources"] = [
        {"title": r.get("title", ""), "url": r.get("url", "")}
        for r in mvp_search_results[:5]
    ]
    return result
