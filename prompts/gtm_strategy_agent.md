# GTM Strategy Agent

**File:** `agents/gtm_strategy_agent.py`
**Type:** Rule-based / deterministic core; LLM used ONLY for the one-sentence positioning statement.

## Role
Recommends marketing channels, pricing strategy, and a launch
checklist using a fixed decision table keyed on business-model /
target-customer keywords.

## Input
- `extracted`, `market_analysis`

## Deterministic logic
- `_CHANNEL_RULES`: keyword → channel list (e.g. `marketplace` →
  SEO/content, referral, local partnerships; `b2b` → LinkedIn
  outreach, industry events, direct sales). Falls back to a default
  channel set if no keyword matches.
- `_PRICING_RULES`: keyword → pricing model (subscription,
  commission, marketplace, freemium). Falls back to flat-rate.
- `_build_launch_checklist_deterministically()`: a fixed 5-step
  early-stage launch checklist, identical for every idea.

## LLM call (positioning statement only)
```
Based ONLY on this information (do not invent additional facts), write
one sentence positioning statement for this startup.

Idea: {idea_name}
Target Customer: {target_customer}
Solution: {solution}

Respond with plain text only, one sentence.
```

## Output
```json
{"positioning_statement", "marketing_channels": [...], "pricing_strategy", "launch_checklist": [...]}
```
