# Competitor Research Agent

**File:** `agents/competitor_agent.py`
**Type:** LLM output forced through a validated Pydantic schema (`CompetitorResearch`).

## Role
Finds direct and indirect competitors, assesses competitive
intensity, and identifies a market gap - strictly from retrieved
web context, never invented company names.

## Input
- `extracted` (dict): structured idea.

## Search
Runs its own multi-query search (independent of the Web Search
Agent, so it can target competitor-specific angles):
- `"{industry} startups competitors"`
- `"best apps for {target_customer} {industry}"`
- `"{idea_name} alternatives"`
- `"{industry} market players"`

Results are deterministically relevance-filtered (with the same
fallback-to-minimum-results logic as the Web Search Agent, floor of
6) BEFORE they ever reach the LLM - this is what stops irrelevant
results (e.g. momos results for a panipuri idea) from being seen by
the model at all.

## Prompt template
System prompt:
```
You are a competitive research analyst.

Given a startup idea and web search context, identify direct and
indirect competitors, assess competitive intensity, and identify a
market gap.

IMPORTANT: Base your answer ONLY on the search context provided. If
the search context does not contain relevant information about real
competitors, say so honestly in market_gap rather than inventing
company names. Do not use any information not present in the search
context or the idea description.

Return ONLY valid JSON matching this schema:
{
  "direct_competitors": [{"name", "strength", "weakness", "source_url"}],
  "indirect_competitors": [{"name", "strength", "weakness", "source_url"}],
  "market_gap": "...",
  "competitive_intensity": "low" | "medium" | "high" | "unknown"
}
```
User prompt: idea name/industry/target customer + up to 10 filtered
search hits (300 chars each) + "Based ONLY on the above, produce the
competitor research JSON."

## Output
```json
{"competitors": [{"name","strength","weakness","url"}], "market_gap", "competitive_intensity"}
```
