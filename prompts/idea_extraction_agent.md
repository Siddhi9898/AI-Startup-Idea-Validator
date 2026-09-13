# Idea Extraction Agent

**File:** `agents/idea_extraction_agent.py`
**Type:** LLM-required (turning free text into structured fields is
a genuine language-understanding task).

## Role
The very first step of the pipeline. Takes the founder's raw,
free-form idea description and turns it into structured fields the
rest of the pipeline can reason over deterministically.

## Input
- `raw_idea` (str): the founder's free-text description.

## Output
A dict with:
- `idea_name`, `problem`, `solution`, `target_customer`, `industry`,
  `business_model`

## Validation
- BEFORE the LLM call: rejects empty input or input under 10
  characters, no LLM involved.
- AFTER the LLM call: checks all six required fields are present and
  non-empty; retries once with the same prompt if not, then fails
  gracefully (returns empty fields + a `validation_error` note)
  rather than crashing the pipeline.

## Prompt template
```
Extract the following structured fields from this startup idea.
Return ONLY valid JSON, no markdown, no explanation.
Fields: idea_name, problem, solution, target_customer, industry, business_model
Startup idea: "{raw_idea}"
```
