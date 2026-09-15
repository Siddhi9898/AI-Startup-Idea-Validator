"""
Web Search Agent
-------------------
Uses the DuckDuckGoTool (tools/duckduckgo_tool.py) to fetch raw
results across SEVERAL targeted queries (not one narrow query -
a single query was the reason this agent used to come back with
only 0-1 results), applies query improvement and cleaning logic,
then applies TWO layers of filtering before returning results:

1. Deterministic RELEVANCE filtering with fallback
   (tools/validators.py) - drops results that aren't actually about
   the idea's topic (this is the fix for the panipuri/momos problem:
   momos results get dropped here, deterministically, based on
   keyword overlap with the idea). The fallback variant guarantees a
   reasonable minimum number of results survive instead of leaving
   every downstream agent with almost nothing to work with, as long
   as SOME topical overlap exists.

2. Dead/404 link filtering (fixes P9) - drops URLs that don't
   actually load. If this ever removes everything (e.g. a flaky
   network / overly strict timeout), we fall back to the relevance-
   filtered results unchecked rather than returning an empty list.

Both are deterministic and applied BEFORE results are shown to the
user in the "Web Search" tab or passed to any other agent.
"""

import sys
import os
import concurrent.futures

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web_search_agent"))

from tools.duckduckgo_tool import DuckDuckGoTool
from tools.link_validator import is_link_alive
from tools.validators import filter_relevant_results_with_fallback, deduplicate_by_domain
from query_planner import improve_query
from cleaner import clean_results

_tool = DuckDuckGoTool()


def _filter_alive_concurrently(results: list, timeout: float = 4.0) -> list:
    if not results:
        return []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(10, len(results))) as executor:
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


def _build_queries(structured_idea: dict, target_market: str) -> list:
    """Several angled queries instead of one narrow query, matching
    the same multi-query pattern used by the competitor agent - this
    is the main fix for the "only 0-1 results" complaint."""
    industry = structured_idea.get("industry", "")
    idea_name = structured_idea.get("idea_name", "")
    target_customer = structured_idea.get("target_customer", "")
    location_suffix = f" {target_market}" if target_market else ""

    queries = [
        f"{industry} startup competitors {idea_name}{location_suffix}",
        f"{industry} market trends{location_suffix}",
        f"{idea_name} reviews OR alternatives",
        f"{industry} for {target_customer}{location_suffix}".strip(),
    ]
    # de-dupe while preserving order, drop empty/near-empty queries
    seen = set()
    unique_queries = []
    for q in queries:
        q = improve_query(q)
        key = q.lower().strip()
        if key and key not in seen and len(key) > 3:
            seen.add(key)
            unique_queries.append(q)
    return unique_queries


def search_market(structured_idea: dict, target_market: str = "") -> dict:
    queries = _build_queries(structured_idea, target_market)

    raw_results = []
    for search_response in _tool.multi_search(queries, max_results_per_query=7):
        raw_results.extend(search_response.hits)

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
    results = deduplicate_by_domain(results)

    # STEP 1 (the actual fix): deterministically drop results that
    # aren't relevant to the idea's actual topic, with a fallback so
    # a handful of near-miss results don't get thrown away entirely -
    # this is what prevents momos results showing up for a panipuri
    # idea, while still giving downstream agents enough to work with.
    relevant_results = filter_relevant_results_with_fallback(
        structured_idea, results, min_relevance=0.20, min_results=5
    )

    # STEP 2: deterministically drop dead/404 links (fixes P9). If
    # this happens to remove every candidate (flaky network / overly
    # strict timeout), fall back to the relevance-filtered results
    # unchecked rather than showing the user an empty tab.
    alive_results = _filter_alive_concurrently(relevant_results)
    if not alive_results and relevant_results:
        alive_results = relevant_results

    return {
        "query": " | ".join(queries),
        "results": alive_results,
    }
