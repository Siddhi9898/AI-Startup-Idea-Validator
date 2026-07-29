"""
MVP Recommendation Agent
----------------------------
Recommends a prioritized set of MVP features for the startup idea.
"""

import json
from agents.idea_extraction_agent import client
from app.config import MODEL_NAME


def recommend_mvp(extracted: dict, swot: dict) -> dict:
    prompt = f"""
You are a product manager. Based on this startup idea and its SWOT
analysis, recommend a prioritized MVP feature set.

Idea: {extracted.get('idea_name')}
Solution: {extracted.get('solution')}
Target Customer: {extracted.get('target_customer')}
Key weaknesses to address: {swot.get('weaknesses', [])}

Return ONLY valid JSON with this format:
{{
  "mvp_features": [
    {{"priority": "High", "feature": "..."}},
    {{"priority": "Medium", "feature": "..."}},
    {{"priority": "Low", "feature": "..."}}
  ],
  "estimated_timeline": "short estimate, e.g. '6-8 weeks for MVP'"
}}
"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"mvp_features": [], "estimated_timeline": text}
