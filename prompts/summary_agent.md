# Summary Agent

**File:** `agents/summary_agent.py`
**Type:** Deterministic fact-gathering + one LLM call to phrase it.

## Role
Condenses the ENTIRE pipeline's output into one up-front briefing so
a founder doesn't have to read every tab to get the gist. Pulls
facts from every agent that produced one (viability, competitors,
SWOT, MVP, market analysis, GTM, elevator pitch, funding, blind
spots) - the LLM only phrases these into prose, it never adds new
analysis or numbers.

## Input
- `state_dict`: the full shared-state dict (every agent's output so far).

## Facts gathered (deterministic)
idea name/industry, viability score + verdict, competitor count +
market gap, growth trend + market size score, top strength/weakness,
risk score, top MVP feature + timeline, GTM positioning + pricing,
tagline, top funding path, number of blind spots.

## Prompt template
```
Write a clear, scannable summary (6-8 sentences, one paragraph) of
this startup validation, using ONLY the facts below - do not add
new analysis, numbers, or claims beyond what's given here. Cover, in
order: (1) what the idea is and its viability verdict, (2) what the
market/competitive picture looks like, (3) the single biggest
strength and biggest weakness, (4) what to build first and roughly
how long it takes, (5) the recommended go-to-market angle, and (6)
the most realistic funding path. End with how many open questions
("blind spots") the founder still needs to answer.

{all gathered facts, one per line}

Write it as a briefing a busy founder could read in under 30 seconds
instead of reading every section below, but dense enough that they
walk away actually informed, not just reassured.
```

If the LLM call fails, a deterministic fallback paragraph is built
directly from the same gathered facts, so the summary is never blank.

## Output
A single string (the paragraph), stored as `quick_summary`.
