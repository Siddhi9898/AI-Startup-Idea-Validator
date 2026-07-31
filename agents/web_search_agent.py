"""
Web Search Agent
-------------------
Uses the DuckDuckGoTool to fetch raw results, applies Niharika's
query improvement and cleaning logic, and reshapes the output.
Now includes location in the search query (per mentor feedback).
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
    location = structured_idea.get("location", "Global")

    base_query = f"{industry} startup competitors {idea_name} {location}"
    query = improve_query(base_query)

    raw_results = _tool.search(query)

    for_cleaning = [
        {
            "title": r.get("title", ""),
            "link": r.get("url", ""),
            "description": r.get("snippet", ""),
        }
        for r in raw_results
    ]
    cleaned = clean_results(for_cleaning)

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
