"""
SWOT & Risk Agent
--------------------
Generates a SWOT analysis and estimates execution risk for the idea,
using the extracted idea, market analysis, and competitor data.
"""

import json
from agents.idea_extraction_agent import client
from app.config import MODEL_NAME


def analyze_swot(extracted: dict, market_analysis: dict, competitors: dict) -> dict:
    prompt = f"""
You are a strategy consultant. Based on this startup idea, market
analysis, and competitor data, produce a SWOT analysis and a risk score.

Idea: {extracted.get('idea_name')}
Problem: {extracted.get('problem')}
Solution: {extracted.get('solution')}
Market growth trend: {market_analysis.get('growth_trend', 'unknown')}
Competitor gap: {competitors.get('market_gap', 'unknown')}

Return ONLY valid JSON with this format:
{{
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "opportunities": ["...", "..."],
  "threats": ["...", "..."],
  "risk_score": <number 0-10, where 10 = very low risk>
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
        return {
            "strengths": [], "weaknesses": [], "opportunities": [],
            "threats": [], "risk_score": 5.0,
        }
