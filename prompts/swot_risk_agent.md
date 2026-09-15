# SWOT & Risk Agent

**File:** `agents/swot_risk_agent.py`
**Type:** Rule-based / deterministic core; LLM used ONLY, optionally, to reword.

## Role
Derives Strengths / Weaknesses / Opportunities / Threats and a
`risk_score` from fixed rules applied to signals already present in
shared state - never freely invented by an LLM.

## Input
- `extracted`, `market_analysis`, `competitors`

## Deterministic rules (examples)
- A well-described `problem`/`solution` (> 20 chars) → strength.
- 0 competitors found → opportunity ("underexplored niche"); ≥ 4 →
  threat ("crowded market"); in between → moderate opportunity.
- `market_size_score` ≥ 7 → opportunity; ≤ 4 → weakness.
- Missing `business_model` → weakness.
- Always adds one structural threat: "Execution risk typical of
  early-stage ventures."
- `risk_score` (0-10, 10 = low risk): starts at 5.0, +0.5 per
  strength, +0.3 per opportunity, -0.5 per weakness, -0.5 per threat,
  ± up to 1.5 based on market score.

## LLM call (rewording only)
The model is given the ALREADY-DECIDED points and told only to
rephrase them - a safety check afterward rejects the rewrite and
falls back to the deterministic wording if the LLM changed the
number of items in any list.

```
Rewrite each of these already-determined points in clearer, more
natural business language. Do NOT add, remove, or invent new points -
only rephrase what is given. Return ONLY valid JSON with the same
structure and same number of items per list.

{swot_points}
```

## Output
```json
{"strengths": [...], "weaknesses": [...], "opportunities": [...], "threats": [...], "risk_score": <float>}
```
