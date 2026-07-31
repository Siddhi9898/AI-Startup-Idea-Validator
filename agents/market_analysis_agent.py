"""
Market Analysis Agent (Deep Search version)
-----------------------------------------------
Instead of only reusing the Web Search Agent's shared results, this
agent now runs its OWN targeted search specifically for market size
and trend data, then does a follow-up "deep search" if the first
result looks too generic. This gives more accurate, market-specific
signal instead of leftover competitor search results.
"""

import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web_search_agent"))

from tools.duckduckgo_tool import DuckDuckGoTool
from agents.idea_extraction_agent import client
from app.config import MODEL_NAME

_tool = DuckDuckGoTool()


def _deep_search(industry: str, location: str) -> list:
    """
    Runs an initial market-specific search, then a refined follow-up
    search if the first pass returned too few results - this is the
    "deep search" pattern: search, check, search again if needed.
    """
    query_1 = f"{industry} market size trends {location}"
    results = _tool.search(query_1, max_results=5)

    if len(results) < 2:
        # First search too shallow - refine and try again
        query_2 = f"{industry} industry growth report {location} 2026"
        results += _tool.search(query_2, max_results=5)

    return results


def analyze_market(extracted: dict, search_results: dict) -> dict:
    industry = extracted.get("industry", "")
    location = extracted.get("location", "Global")

    # Agent does its OWN targeted search, instead of only reusing
    # the shared Web Search Agent results
    market_search_results = _deep_search(industry, location)
    market_context = [r.get("title", "") for r in market_search_results][:5]

    prompt = f"""
You are a market research analyst. Based on this startup idea and the
market-specific search context below, estimate the market opportunity.

Idea: {extracted.get('idea_name')}
Industry: {industry}
Location/Target Market: {location}
Problem: {extracted.get('problem')}
Target Customer: {extracted.get('target_customer')}
Market search context: {market_context}

Return ONLY valid JSON with these fields:
{{
  "tam_estimate": "short description of Total Addressable Market",
  "sam_estimate": "short description of Serviceable Available Market",
  "som_estimate": "short description of Serviceable Obtainable Market",
  "growth_trend": "one sentence on industry growth trend in this location",
  "customer_segments": ["segment1", "segment2"],
  "market_size_score": <number 0-10, where 10 = very large/growing market>
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
            "tam_estimate": text, "sam_estimate": "", "som_estimate": "",
            "growth_trend": "", "customer_segments": [], "market_size_score": 5.0,
        }

    # Include the market-specific search sources used, for transparency
    result["market_search_sources"] = [
        {"title": r.get("title", ""), "url": r.get("url", "")}
        for r in market_search_results[:5]
    ]
    return result
