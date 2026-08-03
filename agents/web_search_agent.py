"""
Web Search Agent (fixes P9, P10)
------------------------------------
- P9: filters out dead/404 links before returning results
- P10: catches network errors gracefully instead of hanging forever,
  returns an empty result set with a clear error flag instead of
  looping indefinitely
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web_search_agent"))

from tools.duckduckgo_tool import DuckDuckGoTool
from tools.link_validator import filter_dead_links
from query_planner import improve_query
from cleaner import clean_results

_tool = DuckDuckGoTool()


def search_market(structured_idea: dict) -> dict:
    industry = structured_idea.get("industry", "")
    idea_name = structured_idea.get("idea_name", "")
    location = structured_idea.get("location", "Global")

    base_query = f"{industry} startup competitors {idea_name} {location}"
    query = improve_query(base_query)

    try:
        raw_results = _tool.search(query)
    except Exception as e:
        # P10: network/connection failure - fail gracefully instead
        # of hanging or crashing the pipeline
        return {
            "query": query,
            "results": [],
            "error": f"Search failed - please check your internet connection. ({e})",
        }

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

    # P9: remove dead/404 links before returning
    results = filter_dead_links(results)

    return {
        "query": query,
        "results": results,
    }
