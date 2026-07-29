"""
Idea Extraction Agent
------------------------
Extracts structured information from the user's raw startup idea text.
(Moved from the original extraction_agent.py into agents/, per the
architecture doc's folder structure.)
"""

from groq import Groq
import json
from app.config import GROQ_API_KEY, MODEL_NAME

client = Groq(api_key=GROQ_API_KEY)


def extract_idea(raw_idea: str) -> dict:
    prompt = f"""Extract the following structured fields from this startup idea.
Return ONLY valid JSON, no markdown, no explanation.
Fields: idea_name, problem, solution, target_customer, industry, business_model
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
