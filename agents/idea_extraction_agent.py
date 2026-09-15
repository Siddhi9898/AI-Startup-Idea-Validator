"""
Idea Extraction Agent (adds feasibility/ethics gate - fixes P11, P12, P13)
------------------------------------------------------------------------------
Before running the full expensive pipeline, this now validates:
- P11: the input isn't gibberish/meaningless (numbers, random chars, too short)
- P12: the idea is at least minimally realistic (not sci-fi impossible)
- P13: the idea isn't clearly unethical/illegal

If validation fails, extract_idea returns a dict with an "invalid"
flag and a reason, so the UI can show a clear message instead of
running the rest of the pipeline on garbage input.
"""

from groq import Groq
import json
from app.config import GROQ_API_KEY, MODEL_NAME

client = Groq(api_key=GROQ_API_KEY)


def _basic_input_check(raw_idea: str) -> str | None:
    """Cheap, fast checks before spending an LLM call. Returns an
    error message if invalid, or None if it passes."""
    text = raw_idea.strip()
    if len(text) < 10:
        return "Please enter a valid input - your idea is too short to evaluate."
    # crude check: does it contain at least a few real alphabetic words
    words = [w for w in text.split() if w.isalpha() and len(w) > 2]
    if len(words) < 3:
        return "Please enter a valid input - this doesn't look like a startup idea description."
    return None


def extract_idea(raw_idea: str) -> dict:
    basic_error = _basic_input_check(raw_idea)
    if basic_error:
        return {"invalid": True, "reason": basic_error}

    prompt = f"""You are evaluating a submitted startup idea for a validation tool.

First, judge two things:
1. Is this a coherent, realistic startup idea a real founder could
   plausibly pursue (not physically impossible, not nonsense text)?
2. Is this idea free of clearly unethical, illegal, or harmful intent
   (e.g. not a scam, not designed to harm people)?

If either check fails, respond with ONLY this JSON:
{{"invalid": true, "reason": "one sentence explaining why, phrased politely to the user"}}

If both checks pass, extract the following structured fields and
respond with ONLY this JSON (no markdown, no explanation):
{{"invalid": false, "idea_name": "...", "problem": "...", "solution": "...",
"target_customer": "...", "industry": "...", "business_model": "...",
"location": "..."}}
For "location": if the idea mentions a specific country, city, or region, use that.
If no location is mentioned, infer the most likely target market, or use "Global".

Startup idea: "{raw_idea}"
"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"invalid": True, "reason": "Please enter a valid input - could not process this idea."}
