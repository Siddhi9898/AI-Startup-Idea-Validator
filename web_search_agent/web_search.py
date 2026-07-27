from ddgs import DDGS
from query_planner import improve_query


def search_web(query):
    results = []

    try:
        # Improve the user's search query
        query = improve_query(query)

        # Search using DuckDuckGo
        with DDGS() as ddgs:
            search_results = ddgs.text(query, max_results=5)

            # Store only required fields
            for result in search_results:
                results.append({
                    "title": result.get("title", ""),
                    "link": result.get("href", ""),
                    "description": result.get("body", "")
                })

    except Exception as e:
        print("Error:", e)

    return results


# Test the module directly
if __name__ == "__main__":
    results = search_web("AI Startup")

    print(f"\nFound {len(results)} results\n")

    for i, result in enumerate(results, start=1):
        print(f"Result {i}")
        print(result)