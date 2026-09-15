# MVP Recommendation Agent

**File:** `agents/mvp_recommendation_agent.py`
**Type:** Rule-based / deterministic core (MoSCoW); LLM used ONLY to reword feature descriptions.

## Role
Recommends what to build first, using a fixed MoSCoW checklist
matched deterministically against the idea's business model -
never asks the LLM to freely decide priority.

## Input
- `extracted` (dict)

## Deterministic logic
- Classifies business model into `marketplace` / `subscription` /
  `generic` by keyword.
- Selects features from a fixed checklist (`_BASE_FEATURE_CHECKLIST`)
  whose `applies_if` matches `always` or the classified model type.
- Sorts by priority (Must > Should > Could > Won't (v1)).
- Timeline estimate is a fixed formula: `must_count * 1.5 +
  should_count * 1.0` weeks (range shown ± 2 weeks).

## LLM call (wording only)
```
For each feature below, rewrite the description to be specific to
this startup idea's domain, in 5-10 words. Do NOT change priorities,
add features, or remove features - only adapt the wording.
Return ONLY valid JSON: a list of strings, same length and order as input.

Startup idea: {idea_name} - {solution}

Features:
{feature_list}
```
A length check afterward rejects the rewrite (falls back to generic
wording) if the LLM didn't return exactly one string per feature.

## Output
```json
{"mvp_features": [{"priority", "feature"}], "estimated_timeline": "..."}
```
