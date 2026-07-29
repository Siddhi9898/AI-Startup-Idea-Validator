"""
Market Analysis Agent
------------------------
Estimates market opportunity (TAM/SAM/SOM), growth trends, and
customer segments for the startup idea, using the extracted idea
and search results as context.
"""

import json
from agents.idea_extraction_agent import client
from app.config import MODEL_NAME


def analyze_market(extracted: dict, search_results: dict) -> dict:
    competitor_titles = [r.get("title", "") for r in search_results.get("results", [])][:5]

    prompt = f"""
You are a market research analyst. Based on this startup idea and
related search context, estimate the market opportunity.

Idea: {extracted.get('idea_name')}
Industry: {extracted.get('industry')}
Problem: {extracted.get('problem')}
Target Customer: {extracted.get('target_customer')}
Related market context found online: {competitor_titles}

Return ONLY valid JSON with these fields:
{{
  "tam_estimate": "short description of Total Addressable Market",
  "sam_estimate": "short description of Serviceable Available Market",
  "som_estimate": "short description of Serviceable Obtainable Market",
  "growth_trend": "one sentence on industry growth trend",
  "customer_segments": ["segment1", "segment2"],
  "market_size_score": <number 0-10, where 10 = very large/growing market>
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
            "tam_estimate": text, "sam_estimate": "", "som_estimate": "",
            "growth_trend": "", "customer_segments": [], "market_size_score": 5.0,
        }
