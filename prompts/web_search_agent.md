# Web Search Agent

**File:** `agents/web_search_agent.py`
**Type:** No LLM call in this agent - deterministic search + filtering.

## Role
Gathers the raw, live market/competitor context that most other
agents build on. Runs SEVERAL angled DuckDuckGo queries (not one
narrow query) so it isn't starved for results, then applies two
deterministic filtering passes before anything reaches the UI or
another agent.

## Input
- `structured_idea` (dict): output of the Idea Extraction Agent.
- `target_market` (str, optional): the founder's chosen location.

## Queries built (per run)
- `"{industry} startup competitors {idea_name} {target_market}"`
- `"{industry} market trends {target_market}"`
- `"{idea_name} reviews OR alternatives"`
- `"{industry} for {target_customer} {target_market}"`

## Filtering pipeline
1. **Relevance filtering with fallback** (`tools/validators.py`):
   scores every result by keyword overlap with the idea (idea-name
   keywords weighted 3x over generic category words). Keeps results
   scoring ≥ 0.20. If fewer than 5 clear that bar, backfills with the
   next-highest-scoring results below the threshold (tagged
   `below_threshold: True`) so downstream agents always have a
   reasonable minimum to work with instead of an empty list.
2. **Dead-link filtering** (`tools/link_validator.py`): drops URLs
   that don't actually load (HEAD, falling back to GET, 4s timeout).
   If this would remove every remaining result, falls back to the
   relevance-filtered set unchecked rather than returning nothing.

## Output
```json
{"query": "<queries used, joined by | >", "results": [{"url", "title", "content", "relevance", ...}]}
```
