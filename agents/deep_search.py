"""
Deep Search Tool
-------------------
Runs an initial targeted search, checks if results are too shallow,
and if so runs one refined follow-up search. Now also applies
deterministic relevance filtering to whatever it returns, so any
agent using deep_search() gets only genuinely relevant results -
same fix as web_search_agent.py, applied here too since this is a
shared tool used by multiple agents.
"""

from tools.duckduckgo_tool import DuckDuckGoTool
from tools.validators import filter_relevant_results

_tool = DuckDuckGoTool()


def deep_search(primary_query: str, fallback_query: str, extracted_idea: dict = None, max_results: int = 5, min_results: int = 2) -> list:
    """
    Runs primary_query first. If it returns fewer than min_results,
    runs fallback_query as a refined second attempt and combines both.

    If extracted_idea is provided, results are deterministically
    filtered for relevance to the idea before being returned - this
    prevents topically unrelated results (e.g. momos results for a
    panipuri idea) from reaching any agent that calls this function.
    """
    results = _tool.search(primary_query, max_results=max_results)

    if len(results) < min_results:
        results += _tool.search(fallback_query, max_results=max_results)

    if extracted_idea:
        # Reshape to the {title, content, url} format filter_relevant_results expects
        reshaped = [{"title": r.get("title", ""), "content": r.get("snippet", ""), "url": r.get("url", "")} for r in results]
        filtered = filter_relevant_results(extracted_idea, reshaped)
        # Reshape back to the original {title, url, snippet} format callers expect
        results = [{"title": r["title"], "url": r["url"], "snippet": r["content"]} for r in filtered]

    return results
