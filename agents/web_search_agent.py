"""
Web Search Agent
-------------------
Uses the DuckDuckGoTool (tools/duckduckgo_tool.py) to fetch raw
results, applies query improvement and cleaning logic, then applies
TWO layers of filtering before returning results:

1. Deterministic RELEVANCE filtering (tools/validators.py) - drops
   results that aren't actually about the idea's topic (this is the
   direct fix for the panipuri/momos problem: momos results get
   dropped here, deterministically, based on keyword overlap with
   the idea - not based on the LLM "deciding" what's relevant).

2. Dead/404 link filtering (fixes P9) - drops URLs that don't
   actually load.

Both are deterministic and applied BEFORE results are shown to the
user in the "Web Search" tab or passed to any other agent.
"""

import sys
import os
import concurrent.futures

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web_search_agent"))

from tools.duckduckgo_tool import DuckDuckGoTool
from tools.link_validator import is_link_alive
from tools.validators import filter_relevant_results
from query_planner import improve_query
from cleaner import clean_results

_tool = DuckDuckGoTool()


def _filter_alive_concurrently(results: list, timeout: float = 2.5) -> list:
    if not results:
        return []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(8, len(results))) as executor:
        futures = {executor.submit(is_link_alive, r.get("url", ""), timeout): r for r in results}
        alive = []
        for future in concurrent.futures.as_completed(futures):
            r = futures[future]
            try:
                if future.result():
                    alive.append(r)
            except Exception:
                continue
    return alive


def search_market(structured_idea: dict, target_market: str = "") -> dict:
    industry = structured_idea.get("industry", "")
    idea_name = structured_idea.get("idea_name", "")
    base_query = f"{industry} startup competitors {idea_name}"
    if target_market:
        base_query += f" {target_market}"

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

    # STEP 1 (the actual fix): deterministically drop results that
    # aren't relevant to the idea's actual topic - this is what
    # prevents momos results showing up for a panipuri idea.
    relevant_results = filter_relevant_results(structured_idea, results)

    # STEP 2: deterministically drop dead/404 links (fixes P9)
    alive_results = _filter_alive_concurrently(relevant_results)

    return {
        "query": query,
        "results": alive_results,
    }
