"""
Idea Extraction Agent
------------------------
Extracts structured information from the user's raw startup idea text,
including a location/region field (new - per mentor feedback).
"""

from groq import Groq
import json
from app.config import GROQ_API_KEY, MODEL_NAME

client = Groq(api_key=GROQ_API_KEY)


def extract_idea(raw_idea: str) -> dict:
    prompt = f"""Extract the following structured fields from this startup idea.
Return ONLY valid JSON, no markdown, no explanation.
Fields: idea_name, problem, solution, target_customer, industry, business_model, location
For "location": if the idea mentions a specific country, city, or region, use that.
If no location is mentioned, infer the most likely target market based on context,
or use "Global" if truly unclear.
Startup idea: "{raw_idea}"
"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "")
    return json.loads(text)
