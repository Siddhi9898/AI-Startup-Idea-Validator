# Report Agent

**File:** `agents/report_agent.py`
**Type:** Fully deterministic - no LLM call, pure string formatting.

## Role
Compiles the full shared state into the Markdown validation report
(also the source data for the PDF export - see `tools/pdf_generator.py`).
Includes the full Pipeline Execution Log so every step's
deterministic validation outcome is visible and traceable.

## Input
- `state_dict`: the full shared-state dict.

## Output
A single Markdown string with sections: Executive Summary, Startup
Idea, Viability Score, Market Analysis, Competitor Analysis, SWOT
Analysis, MVP Recommendation, Go-To-Market Strategy, Blind Spots,
Elevator Pitch, Suggested Funding Paths, Pipeline Execution Log.

## PDF export
`tools/pdf_generator.py:build_report_pdf(state_dict)` renders the
SAME shared-state dict as a real, formatted PDF (headings, tables,
bullet lists, a color-coded score) using `reportlab`, so the
Markdown report and the downloadable PDF can never drift out of
sync with each other - both read from the same data.
