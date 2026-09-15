# Orchestrator Agent

**File:** `app/orchestrator.py`
**Type:** No LLM call itself - pure coordination logic.

## Role
Owns the `SharedState` object (`state/memory.py`) and calls every
other agent in the correct order, passing each agent's output into
the next. This is the "pipeline" referenced elsewhere in this repo -
also exposed as a standalone CLI in `pipeline.py` for running
outside Streamlit.

## Sequencing
1. Idea Extraction → validate
2. Web Search → validate
3. Market Analysis **and** Competitor Research, concurrently
   (`concurrent.futures.ThreadPoolExecutor`) - neither depends on the
   other's output, so running them in parallel cuts real wall-clock
   time on the two slowest deep-search steps.
4. SWOT & Risk (needs both of the above)
5. MVP Recommendation (needs SWOT)
6. GTM Strategy (needs Market Analysis)
7. Viability Score (needs everything above)
8. Insight Layer (blind spots, honest summary, elevator pitch, funding paths)
9. Report Agent (compiles the Markdown report)
10. Summary Agent (condenses everything into one quick briefing)

Every step logs its deterministic validation outcome via
`state.log_step(...)`, which shows up in the report's "Pipeline
Execution Log" section - so every run is traceable end to end.

## Output
`state.to_dict()` - the full result dict every downstream consumer
(Streamlit UI, `pipeline.py`, `db/database.py`) reads from.
