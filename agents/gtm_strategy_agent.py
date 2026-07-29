"""
GTM Strategy Agent
----------------------
Generates a go-to-market strategy: positioning, channels, pricing.
"""

import json
from agents.idea_extraction_agent import client
from app.config import MODEL_NAME


def generate_gtm_strategy(extracted: dict, market_analysis: dict) -> dict:
    prompt = f"""
You are a go-to-market strategist. Based on this startup idea and
market analysis, recommend a GTM strategy.

Idea: {extracted.get('idea_name')}
Target Customer: {extracted.get('target_customer')}
Customer segments: {market_analysis.get('customer_segments', [])}
Business Model: {extracted.get('business_model')}

Return ONLY valid JSON with this format:
{{
  "positioning_statement": "one sentence positioning statement",
  "marketing_channels": ["channel1", "channel2"],
  "pricing_strategy": "short description",
  "launch_checklist": ["step1", "step2", "step3"]
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
            "positioning_statement": text, "marketing_channels": [],
            "pricing_strategy": "", "launch_checklist": [],
        }
