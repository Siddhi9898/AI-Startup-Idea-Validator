# Agent Prompts & Roles

This folder documents every agent in the pipeline: what it's
responsible for, what it takes as input, what it hands off, and
(where the agent calls an LLM) the actual prompt template it uses.

It exists so a new contributor - or anyone reviewing the project -
can understand each agent's job and its exact prompt without reading
every `.py` file in `agents/`.

## Pipeline order

The Orchestrator Agent (`app/orchestrator.py`) runs the agents in
this order. Market Analysis and Competitor Research run concurrently
since neither depends on the other's output; everything else runs
sequentially because each step genuinely needs the previous ones.

1. [idea_extraction_agent](./idea_extraction_agent.md)
2. [web_search_agent](./web_search_agent.md)
3. [market_analysis_agent](./market_analysis_agent.md) + [competitor_agent](./competitor_agent.md) *(concurrent)*
4. [swot_risk_agent](./swot_risk_agent.md)
5. [mvp_recommendation_agent](./mvp_recommendation_agent.md)
6. [gtm_strategy_agent](./gtm_strategy_agent.md)
7. [viability_score_agent](./viability_score_agent.md)
8. [insight_agent](./insight_agent.md)
9. [report_agent](./report_agent.md)
10. [summary_agent](./summary_agent.md)
11. [conversational_advisor](./conversational_advisor.md) *(runs on-demand, after the report exists)*

## A note on "deterministic vs LLM" agents

Several agents (SWOT, MVP, GTM, Viability Score) compute their core
output with fixed, rule-based logic and use the LLM only,
optionally, to smooth the wording of an already-decided answer. This
is intentional: it keeps identical inputs producing identical (or
near-identical) outputs, and stops the LLM from inventing numbers or
facts it has no real data for. Each agent's file below says clearly
which category it falls into.
