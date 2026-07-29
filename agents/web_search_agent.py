"""
Web Search Agent
-------------------
Uses the DuckDuckGoTool (tools/duckduckgo_tool.py) to fetch raw
results, then applies Niharika's query improvement logic
(web_search_agent/query_planner.py) and deduplication/cleaning
(web_search_agent/cleaner.py), and reshapes the output into the
shared format used across the pipeline.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web_search_agent"))

from tools.duckduckgo_tool import DuckDuckGoTool
from query_planner import improve_query
from cleaner import clean_results

_tool = DuckDuckGoTool()


def search_market(structured_idea: dict) -> dict:
    industry = structured_idea.get("industry", "")
    idea_name = structured_idea.get("idea_name", "")
    base_query = f"{industry} startup competitors {idea_name}"

    # Reuse Niharika's query improvement logic
    query = improve_query(base_query)

    # Fetch raw results via the tool
    raw_results = _tool.search(query)

    # Reshape tool output (title/url/snippet) to cleaner.py's expected
    # shape (title/link/description) before deduplicating
    for_cleaning = [
        {
            "title": r.get("title", ""),
            "link": r.get("url", ""),
            "description": r.get("snippet", ""),
        }
        for r in raw_results
    ]
    cleaned = clean_results(for_cleaning)

    # Reshape into the format viability_score_agent.py and
    # insight_agent.py expect
    results = [
        {
            "url": r.get("link", ""),
            "title": r.get("title", ""),
            "content": r.get("description", ""),
            "score": 0.5,
            "raw_content": None,
        }
        for r in cleaned
    ]

    return {
        "query": query,
        "results": results,
    }
