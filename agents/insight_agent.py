"""
Insight Agent
-------------
Generates the mentor-style layer of the report: blind spots, honest
summary, elevator pitch, and funding suggestions. (Moved into agents/
per architecture doc; logic unchanged from the working version.)
"""

import json
from agents.idea_extraction_agent import client
from app.config import MODEL_NAME


def _call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()


def find_blind_spots(extracted: dict) -> dict:
    prompt = f"""
You are a experienced startup mentor reviewing this idea:

Problem: {extracted.get('problem')}
Solution: {extracted.get('solution')}
Target Customer: {extracted.get('target_customer')}
Business Model: {extracted.get('business_model')}
Industry: {extracted.get('industry')}

Identify 1-2 important things this founder has NOT addressed
(e.g., customer acquisition, pricing, regulation, competition moat).
Phrase each as a direct, honest question back to the founder.
Respond ONLY as a JSON list of strings, nothing else. Example:
["You haven't mentioned how you'll acquire your first 10 customers - what's your plan?"]
"""
    raw = _call_llm(prompt)
    try:
        questions = json.loads(raw)
    except json.JSONDecodeError:
        questions = [raw]
    return {"blind_spots": questions}


def generate_honest_summary(extracted: dict, search_results: dict, viability: dict) -> dict:
    competitor_count = len(search_results.get("results", [])) if search_results else 0

    prompt = f"""
You are a blunt but supportive startup mentor. Based on the following,
write a 2-3 sentence honest closing summary for the founder. Mention
realistic expectations (e.g., time to traction) and whether this is
worth pursuing right now. Avoid generic hype language.

Idea: {extracted.get('idea_name')}
Industry: {extracted.get('industry')}
Viability Score: {viability.get('overall_score')}/100
Verdict: {viability.get('verdict')}
Number of similar competitors found: {competitor_count}

Respond with plain text only, no headers or bullet points.
"""
    summary = _call_llm(prompt)
    return {"honest_summary": summary}


def generate_elevator_pitch(extracted: dict) -> dict:
    prompt = f"""
Based on this startup idea, write:
1. A punchy one-sentence elevator pitch (like a Y Combinator application)
2. A short 3-5 word tagline

Idea Name: {extracted.get('idea_name')}
Problem: {extracted.get('problem')}
Solution: {extracted.get('solution')}
Target Customer: {extracted.get('target_customer')}

Respond ONLY as JSON in this exact format, nothing else:
{{"elevator_pitch": "...", "tagline": "..."}}
"""
    raw = _call_llm(prompt)
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {"elevator_pitch": raw, "tagline": ""}
    return result


def suggest_funding_paths(extracted: dict, viability: dict) -> dict:
    prompt = f"""
Based on this startup idea, suggest the most realistic funding path(s)
from these options: Angel Investor, Venture Capital, Government Grant,
Bootstrapping, Crowdfunding. Pick 1-2 most realistic options and give
a one-line reason for each.

Idea Name: {extracted.get('idea_name')}
Industry: {extracted.get('industry')}
Business Model: {extracted.get('business_model')}
Viability Score: {viability.get('overall_score')}/100

Respond ONLY as a JSON list of objects, nothing else. Example:
[{{"funding_type": "Bootstrapping", "reason": "Low capital needs and can start with a small MVP"}}]
"""
    raw = _call_llm(prompt)
    try:
        suggestions = json.loads(raw)
    except json.JSONDecodeError:
        suggestions = [{"funding_type": "Unknown", "reason": raw}]
    return {"funding_suggestions": suggestions}
