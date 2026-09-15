# Viability Score Agent

**File:** `agents/viability_score_agent.py`
**Type:** Fully deterministic - no LLM call anywhere in this agent.

## Role
Combines every other agent's already-computed signals into one
overall 0-100 score and verdict, with a fixed, auditable formula so
identical input always produces identical output.

## Input
- `extracted`, `search_results`, `market_analysis` (optional), `swot` (optional)

## Weighted components (sum to 100%)
| Component            | Weight | Source |
|-----------------------|--------|--------|
| Completeness          | 10%    | fraction of the 6 required idea fields present |
| Idea clarity          | 15%    | fraction of fields present AND >15 chars |
| Competition density   | 25%    | penalized by result count + average relevance |
| Market analysis       | 30%    | `market_analysis.market_size_score` |
| SWOT / risk           | 20%    | `swot.risk_score` |

## Verdict thresholds
- ≥ 75 → "Strong potential - worth pursuing"
- ≥ 55 → "Moderate potential - needs refinement"
- else → "High risk - significant rework needed"

## Output
```json
{"overall_score": <float>, "verdict": "...", "breakdown": {...}}
```
