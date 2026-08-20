"""
Input Validator
------------------
Deterministic checks to reject gibberish/meaningless idea input
before it reaches any agent (fixes P11), and a basic rule-based
sensitive-content check (fixes P13, best-effort).
"""

import re

# Common English words - if an input has almost none of these,
# it's very likely gibberish/random characters, not a real sentence.
_COMMON_WORDS = {
    "a", "an", "the", "is", "are", "for", "to", "of", "and", "or",
    "that", "with", "in", "on", "app", "platform", "startup", "users",
    "people", "business", "service", "product", "help", "connect",
    "who", "want", "need", "using", "based", "will", "can", "our",
    "their", "this", "that", "provide", "system", "solution",
}

_SENSITIVE_KEYWORDS = {
    "weapon", "explosive", "bomb", "drug trafficking", "narcotics",
    "gambling", "casino", "adult content", "pornographic", "escort",
    "surveillance without consent", "hacking service", "counterfeit",
    "human trafficking", "self-harm", "suicide", "extremist",
}


def validate_idea_text(raw_text: str) -> dict:
    """
    Deterministic validation. Returns {"is_valid": bool, "reason": str}.
    No LLM involved - pure rule-based checks, so identical input
    always produces identical output.
    """
    text = (raw_text or "").strip()

    if not text:
        return {"is_valid": False, "reason": "Please enter your startup idea."}

    if len(text) < 15:
        return {"is_valid": False, "reason": "Please enter a valid input. Your idea is too short to evaluate."}

    # Reject if it's mostly non-alphabetic (numbers, symbols, emojis, random chars)
    letters = re.findall(r"[a-zA-Z]", text)
    if len(letters) < len(text) * 0.5:
        return {"is_valid": False, "reason": "Please enter a valid input. This doesn't look like a real startup idea description."}

    words = re.findall(r"[a-zA-Z]+", text.lower())
    if len(words) < 4:
        return {"is_valid": False, "reason": "Please enter a valid input. Describe your idea in at least a full sentence."}

    # Reject if there's no recognizable common English structure at all
    # (catches strings of random letters like "avojdh kqpz xnrto")
    real_word_count = sum(1 for w in words if w in _COMMON_WORDS or len(w) >= 3)
    if real_word_count / len(words) < 0.3:
        return {"is_valid": False, "reason": "Please enter a valid input. This doesn't look like a coherent sentence."}

    return {"is_valid": True, "reason": ""}


def check_sensitive_content(raw_text: str) -> dict:
    """
    Basic rule-based check for clearly disallowed idea categories.
    This is a best-effort keyword filter, not a comprehensive safety
    system - deterministic and transparent about its limitation.
    """
    text = (raw_text or "").lower()
    for keyword in _SENSITIVE_KEYWORDS:
        if keyword in text:
            return {
                "is_sensitive": True,
                "reason": "This idea involves a category we can't provide validation for. Please describe a different business idea.",
            }
    return {"is_sensitive": False, "reason": ""}


def check_plausibility(raw_text: str) -> dict:
    """
    Best-effort heuristic for obviously implausible ideas (e.g.
    extreme timelines combined with extreme physical/technical
    scope). This is NOT a guarantee - genuinely hard to detect
    deterministically - but catches the most obvious cases.
    """
    text = (raw_text or "").lower()
    extreme_scope = any(kw in text for kw in ["mars", "moon colony", "teleportation", "time travel"])
    extreme_timeline = bool(re.search(r"within\s+(one|1|two|2)\s+(day|week|month|year)", text))
    if extreme_scope and extreme_timeline:
        return {
            "is_plausible": False,
            "reason": "This idea combines an extremely ambitious scope with an unrealistic timeline. Please enter a more realistic startup idea, or remove the specific timeline claim.",
        }
    return {"is_plausible": True, "reason": ""}
