"""
MVP Recommendation Agent (Deterministic - MoSCoW Prioritization)
-----------------------------------------------------------------------
Refactored per reviewer's specific feedback on this module. Instead
of asking the LLM "what should I build first" (fully probabilistic),
we use a fixed MoSCoW-style checklist of standard feature categories,
deterministically matched against the idea's business_model and
industry keywords. The LLM is used only, optionally, to improve the
wording of feature descriptions - never to decide priority.
"""

from agents.idea_extraction_agent import client
from app.config import MODEL_NAME

# Fixed, deterministic feature checklist. This is the core business
# logic - not LLM-generated. Extend this list to cover more domains
# over time; the matching logic itself never changes.
_BASE_FEATURE_CHECKLIST = [
    {"feature": "User registration and authentication", "priority": "Must", "applies_if": "always"},
    {"feature": "Core value-proposition workflow (the single main action the product performs)", "priority": "Must", "applies_if": "always"},
    {"feature": "Basic user profile / dashboard", "priority": "Must", "applies_if": "always"},
    {"feature": "Search and discovery", "priority": "Should", "applies_if": "marketplace"},
    {"feature": "Payment / transaction processing", "priority": "Must", "applies_if": "marketplace"},
    {"feature": "Ratings and reviews", "priority": "Should", "applies_if": "marketplace"},
    {"feature": "Messaging between users", "priority": "Should", "applies_if": "marketplace"},
    {"feature": "Subscription billing", "priority": "Must", "applies_if": "subscription"},
    {"feature": "Usage analytics dashboard", "priority": "Should", "applies_if": "subscription"},
    {"feature": "Notifications (email/push)", "priority": "Could", "applies_if": "always"},
    {"feature": "Admin moderation panel", "priority": "Could", "applies_if": "marketplace"},
    {"feature": "Advanced AI/personalization features", "priority": "Won't (v1)", "applies_if": "always"},
]

_PRIORITY_ORDER = {"Must": 0, "Should": 1, "Could": 2, "Won't (v1)": 3}
_PRIORITY_DISPLAY = {"Must": "High", "Should": "Medium", "Could": "Low", "Won't (v1)": "Future"}


def _classify_business_model(business_model: str) -> str:
    """Deterministic keyword-based classification. No LLM involved."""
    bm = (business_model or "").lower()
    if "marketplace" in bm or "commission" in bm:
        return "marketplace"
    if "subscription" in bm:
        return "subscription"
    return "generic"


def _select_features_deterministically(extracted: dict) -> list:
    """
    Deterministic feature selection using the fixed checklist and
    the idea's classified business model. Identical input always
    produces identical output.
    """
    model_type = _classify_business_model(extracted.get("business_model", ""))
    selected = [
        f for f in _BASE_FEATURE_CHECKLIST
        if f["applies_if"] == "always" or f["applies_if"] == model_type
    ]
    selected.sort(key=lambda f: _PRIORITY_ORDER[f["priority"]])
    return selected


def _estimate_timeline_deterministically(selected: list) -> str:
    """
    Deterministic timeline estimate based purely on feature count
    per priority tier - a fixed rule, not an LLM guess.
    """
    must_count = sum(1 for f in selected if f["priority"] == "Must")
    should_count = sum(1 for f in selected if f["priority"] == "Should")
    weeks = must_count * 1.5 + should_count * 1.0
    return f"Estimated {int(weeks)}-{int(weeks) + 2} weeks for Must-have features; Should-have features add incrementally after."


def recommend_mvp(extracted: dict, swot: dict) -> dict:
    # Deterministic selection - this IS the agent's core logic
    selected = _select_features_deterministically(extracted)
    timeline = _estimate_timeline_deterministically(selected)

    mvp_features = [
        {"priority": _PRIORITY_DISPLAY[f["priority"]], "feature": f["feature"]}
        for f in selected
    ]

    # LLM used ONLY, optionally, to adapt generic feature wording to
    # this specific idea's domain language - priorities are NOT
    # changed by the LLM, only the descriptive text.
    try:
        prompt = f"""
For each feature below, rewrite the description to be specific to
this startup idea's domain, in 5-10 words. Do NOT change priorities,
add features, or remove features - only adapt the wording.
Return ONLY valid JSON: a list of strings, same length and order as input.

Startup idea: {extracted.get('idea_name')} - {extracted.get('solution')}

Features:
{[f['feature'] for f in mvp_features]}
"""
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        import json
        text = response.choices[0].message.content.strip().replace("```json", "").replace("```", "")
        reworded = json.loads(text)
        if len(reworded) == len(mvp_features):
            for i, desc in enumerate(reworded):
                mvp_features[i]["feature"] = desc
    except Exception:
        pass  # fall back to the deterministic, generic wording - never fail the pipeline

    return {
        "mvp_features": mvp_features,
        "estimated_timeline": timeline,
    }
