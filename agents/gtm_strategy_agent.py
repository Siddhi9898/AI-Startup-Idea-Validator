"""
GTM Strategy Agent (Deterministic Channel Selection)
------------------------------------------------------------
Refactored per reviewer feedback: marketing channels and pricing
strategy type are now selected deterministically from a fixed
decision table based on business_model and target_customer keywords,
instead of asking the LLM to invent them freely. The LLM is used
only, optionally, to phrase the positioning statement - grounded
strictly in the already-decided, deterministic inputs.
"""

from agents.idea_extraction_agent import client
from app.config import MODEL_NAME

# Fixed deterministic decision table - the core business logic
_CHANNEL_RULES = [
    {"keyword": "marketplace", "channels": ["SEO/content marketing", "Referral program", "Local partnerships"]},
    {"keyword": "subscription", "channels": ["Content marketing", "Paid social ads", "Email marketing"]},
    {"keyword": "b2b", "channels": ["LinkedIn outreach", "Industry events", "Direct sales"]},
    {"keyword": "restaurant", "channels": ["Local partnerships", "Trade shows", "Direct outreach"]},
]
_DEFAULT_CHANNELS = ["Social media marketing", "Content marketing", "Word of mouth / referrals"]

_PRICING_RULES = [
    {"keyword": "subscription", "pricing": "Recurring subscription pricing (monthly/annual tiers)"},
    {"keyword": "commission", "pricing": "Commission-based pricing on transactions"},
    {"keyword": "marketplace", "pricing": "Commission-based pricing on transactions"},
    {"keyword": "freemium", "pricing": "Freemium model with paid upgrade tiers"},
]
_DEFAULT_PRICING = "Flat-rate pricing (to be validated with early customers)"


def _select_channels_deterministically(business_model: str, target_customer: str) -> list:
    """Deterministic rule matching. No LLM involved."""
    combined = f"{business_model} {target_customer}".lower()
    for rule in _CHANNEL_RULES:
        if rule["keyword"] in combined:
            return rule["channels"]
    return _DEFAULT_CHANNELS


def _select_pricing_deterministically(business_model: str) -> str:
    """Deterministic rule matching. No LLM involved."""
    bm = (business_model or "").lower()
    for rule in _PRICING_RULES:
        if rule["keyword"] in bm:
            return rule["pricing"]
    return _DEFAULT_PRICING


def _build_launch_checklist_deterministically() -> list:
    """
    Fixed, deterministic checklist - standard early-stage launch
    steps, not LLM-invented.
    """
    return [
        "Validate core value proposition with 10-20 target customers",
        "Build and test MVP with a small user group",
        "Set up analytics to track key usage metrics",
        "Launch to a limited initial market/segment",
        "Collect feedback and iterate before wider rollout",
    ]


def generate_gtm_strategy(extracted: dict, market_analysis: dict) -> dict:
    business_model = extracted.get("business_model", "")
    target_customer = extracted.get("target_customer", "")

    # Deterministic selection - this IS the agent's core logic
    channels = _select_channels_deterministically(business_model, target_customer)
    pricing = _select_pricing_deterministically(business_model)
    checklist = _build_launch_checklist_deterministically()

    # LLM used ONLY, optionally, to phrase the positioning statement,
    # grounded strictly in the already-decided deterministic inputs
    try:
        prompt = f"""
Based ONLY on this information (do not invent additional facts), write
one sentence positioning statement for this startup.

Idea: {extracted.get('idea_name')}
Target Customer: {target_customer}
Solution: {extracted.get('solution')}

Respond with plain text only, one sentence.
"""
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        positioning = response.choices[0].message.content.strip()
    except Exception:
        positioning = f"Positioning statement unavailable; deterministic fallback: targeting {target_customer or 'the identified customer segment'}."

    return {
        "positioning_statement": positioning,
        "marketing_channels": channels,
        "pricing_strategy": pricing,
        "launch_checklist": checklist,
    }
