from groq import Groq
import os, json
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_idea(raw_idea: str) -> dict:
    prompt = f"""Extract the following structured fields from this startup idea.
Return ONLY valid JSON, no markdown, no explanation.

Fields: idea_name, problem, solution, target_customer, industry, business_model

Startup idea: "{raw_idea}"
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "")
    return json.loads(text)