# Market Analysis Agent

**File:** `agents/market_analysis_agent.py`
**Type:** Mostly deterministic; LLM used only for one grounded sentence.

## Role
Estimates how "documented" and active the market looks based on
actual retrieved search data - never asked to invent a TAM/SAM/SOM
figure it has no real source for.

## Input
- `extracted` (dict): structured idea.
- `search_results` (dict): output of the Web Search Agent.

## Deterministic logic
- `market_size_score` (0-10): scaled by how many *relevant* results
  were found (0 → 3.0, 1-2 → 5.0, 3-4 → 7.0, 5+ → 8.0, plateaus).
- `customer_segments`: split directly from the idea's
  `target_customer` field - no invention.
- TAM/SAM/SOM: explicitly reported as *not estimable* rather than a
  fabricated number, unless a verified source is ever wired in.

## LLM call (growth trend only)
Runs only if relevant results exist. Grounded strictly in up to 6
retrieved snippets (300 chars each).

```
Based ONLY on the retrieved information below, write one sentence
describing the market/industry trend relevant to this startup idea.
Do NOT invent specific market size figures (TAM/SAM/SOM) - only
describe qualitative trend, based strictly on what is retrieved.
If the retrieved information does not clearly indicate a trend, say so.

Idea industry: {industry}
Retrieved information:
{context_snippets}
```

## Output
```json
{"tam_estimate", "sam_estimate", "som_estimate", "growth_trend",
 "customer_segments", "market_size_score", "data_quality"}
```
