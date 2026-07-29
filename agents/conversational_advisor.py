"""
Conversational Advisor Agent
---------------------------------
Allows the user to ask follow-up questions about their validation
report, without rerunning the full pipeline.
"""

from agents.idea_extraction_agent import client
from app.config import MODEL_NAME


def ask_advisor(question: str, state_dict: dict) -> str:
    context = f"""
Idea: {state_dict.get('extracted', {}).get('idea_name', '')}
Viability Score: {state_dict.get('viability_score', {}).get('overall_score', '')}/100
Honest Summary: {state_dict.get('honest_summary', '')}
Blind Spots: {state_dict.get('blind_spots', [])}
"""
    prompt = f"""
You are a startup mentor. The founder already received this
validation report:

{context}

The founder now asks: "{question}"

Answer directly and concisely in plain text, using the report
context above. Do not repeat the whole report back to them.
"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()
