"""
Deep Search Tool
-------------------
A reusable "deep search" helper any agent can use: runs an initial
targeted search, checks if results are too shallow (too few hits),
and if so runs one refined follow-up search with a broader/adjusted
query. This is shared across agents so each one gets its own
targeted, thorough search instead of only reusing one shared result.
"""

from tools.duckduckgo_tool import DuckDuckGoTool

_tool = DuckDuckGoTool()


def deep_search(primary_query: str, fallback_query: str, max_results: int = 5, min_results: int = 2) -> list:
    """
    Runs primary_query first. If it returns fewer than min_results,
    runs fallback_query as a refined second attempt and combines both.
    """
    results = _tool.search(primary_query, max_results=max_results)

    if len(results) < min_results:
        results += _tool.search(fallback_query, max_results=max_results)

    return results
