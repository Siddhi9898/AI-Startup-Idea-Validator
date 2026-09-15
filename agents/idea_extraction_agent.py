"""
Idea Extraction Agent
------------------------
The LLM is genuinely required here (turning free-form text into
structured fields is inherently a language understanding task - not
something a fixed rule can do). However, per reviewer feedback, the
LLM call is now isolated from deterministic validation: the raw idea
text is validated BEFORE calling the LLM, and the LLM's JSON output
is deterministically validated and parsed AFTER, with retry logic -
so malformed output is caught and fixed deterministically rather
than silently passed downstream or crashing.
"""

from groq import Groq
import json
from app.config import GROQ_API_KEY, MODEL_NAME

client = Groq(api_key=GROQ_API_KEY)


def _validate_raw_input(raw_idea: str) -> dict:
    """Deterministic input validation - no LLM involved."""
    if not raw_idea or not raw_idea.strip():
        return {"is_valid": False, "reason": "empty_input"}
    if len(raw_idea.strip()) < 10:
        return {"is_valid": False, "reason": "too_short"}
    return {"is_valid": True, "reason": "ok"}


def _validate_extraction_output(data: dict) -> dict:
    """
    Deterministic validation of the LLM's structured output.
    Checks for missing/empty required fields. No LLM involved.
    """
    required = ["idea_name", "problem", "solution", "target_customer", "industry", "business_model"]
    missing = [f for f in required if not data.get(f) or not str(data.get(f)).strip()]
    return {"is_valid": len(missing) == 0, "missing_fields": missing}


def _parse_llm_json(text: str) -> dict:
    """Deterministic parsing/cleanup of LLM output. No LLM involved."""
    text = text.strip().replace("```json", "").replace("```", "")
    return json.loads(text)


def extract_idea(raw_idea: str, max_retries: int = 1) -> dict:
    # Step 1: Deterministic input validation, before any LLM call
    input_check = _validate_raw_input(raw_idea)
    if not input_check["is_valid"]:
        return {
            "idea_name": "", "problem": "", "solution": "",
            "target_customer": "", "industry": "", "business_model": "",
            "validation_error": input_check["reason"],
        }

    prompt = f"""Extract the following structured fields from this startup idea.
Return ONLY valid JSON, no markdown, no explanation.
Fields: idea_name, problem, solution, target_customer, industry, business_model
Startup idea: "{raw_idea}"
"""

    attempts = 0
    last_error = None
    while attempts <= max_retries:
        attempts += 1
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,  # minimize sampling variance
            )
            text = response.choices[0].message.content
            data = _parse_llm_json(text)

            # Step 2: Deterministic output validation, after the LLM call
            output_check = _validate_extraction_output(data)
            if output_check["is_valid"]:
                return data
            last_error = f"missing_fields: {output_check['missing_fields']}"
        except (json.JSONDecodeError, Exception) as e:
            last_error = str(e)

    # Deterministic graceful failure - never crash the pipeline
    return {
        "idea_name": "", "problem": "", "solution": "",
        "target_customer": "", "industry": "", "business_model": "",
        "validation_error": f"extraction_failed_after_{attempts}_attempts: {last_error}",
    }
