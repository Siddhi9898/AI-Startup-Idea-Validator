"""
DuckDuckGo Tool
-----------------
Raw search wrapper - no business logic, no query building, no
result shaping. Just takes a query string and returns raw search
hits. This matches the "tools/" layer described in the architecture
doc: tools do one narrow technical job, agents decide how to use them.
"""

from ddgs import DDGS


class DuckDuckGoTool:
    def search(self, query: str, max_results: int = 5):
        results = []
        try:
            with DDGS() as ddgs:
                response = ddgs.text(query, max_results=max_results)
                for item in response:
                    results.append({
                        "title": item.get("title"),
                        "url": item.get("href"),
                        "snippet": item.get("body"),
                    })
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
        return results
