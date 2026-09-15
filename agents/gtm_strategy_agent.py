"""
GTM Strategy Agent (Deep Search version)
----------------------------------------------
Now runs its own targeted deep search for marketing channels and
customer acquisition strategies used in this industry/location,
instead of only reasoning from Market Analysis alone.
"""

import json
from agents.idea_extraction_agent import client
from app.config import MODEL_NAME
from tools.deep_search import deep_search


def generate_gtm_strategy(extracted: dict, market_analysis: dict) -> dict:
    industry = extracted.get("industry", "")
    location = extracted.get("location", "Global")

    primary_query = f"customer acquisition strategy {industry} {location}"
    fallback_query = f"marketing channels {industry} startups use"
    gtm_search_results = deep_search(primary_query, fallback_query)
    gtm_context = [r.get("title", "") for r in gtm_search_results][:5]

    prompt = f"""
You are a go-to-market strategist. Based on this startup idea, market
analysis, and real-world context on customer acquisition below,
recommend a GTM strategy.

Idea: {extracted.get('idea_name')}
Target Customer: {extracted.get('target_customer')}
Customer segments: {market_analysis.get('customer_segments', [])}
Business Model: {extracted.get('business_model')}
Location/Market: {location}
Acquisition context found online: {gtm_context}

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
        result = json.loads(text)
    except json.JSONDecodeError:
        result = {
            "positioning_statement": text, "marketing_channels": [],
            "pricing_strategy": "", "launch_checklist": [],
        }

    result["gtm_search_sources"] = [
        {"title": r.get("title", ""), "url": r.get("url", "")}
        for r in gtm_search_results[:5]
    ]
    return result
