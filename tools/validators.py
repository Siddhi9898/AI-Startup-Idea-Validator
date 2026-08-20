"""
Validators & Deterministic Relevance Filtering
--------------------------------------------------
Pure functions, no LLM calls. Used by agents to validate inputs,
filter irrelevant search results, and detect malformed/empty data
before any LLM call is made.

FIX: the idea's specific name (e.g. "Panipuri") is now weighted more
heavily than generic category words (e.g. "food"). Previously, a
result matching only on a generic word like "food" scored just above
the old 0.08 threshold and incorrectly passed - this is exactly why
momos/generic-food-startup articles were showing up for a panipuri
idea. The threshold is also raised, and idea-name-specific keywords
must contribute meaningfully to the score.
"""

import re


def extract_keywords(text: str) -> set:
    if not text:
        return set()
    stopwords = {
        "a", "an", "the", "and", "or", "for", "to", "of", "in", "on",
        "with", "is", "are", "that", "this", "it", "as", "by", "be",
        "will", "can", "our", "their", "this", "that", "provide",
        "system", "solution", "startup", "app", "platform", "business",
    }
    tokens = re.findall(r"[a-zA-Z]+", text.lower())
    return {t for t in tokens if t not in stopwords and len(t) > 2}


def relevance_score(idea_keywords: set, result_text: str, idea_name_keywords: set = None) -> float:
    """
    Deterministic relevance score (0.0-1.0+). Idea-name-specific
    keywords (e.g. "panipuri") are weighted 3x more than general idea
    keywords (e.g. "food", "delivery"), so a result matching only on
    a generic category word no longer scores high enough to pass.
    """
    if not idea_keywords or not result_text:
        return 0.0
    result_keywords = extract_keywords(result_text)
    if not result_keywords:
        return 0.0

    idea_name_keywords = idea_name_keywords or set()
    overlap = idea_keywords.intersection(result_keywords)
    if not overlap:
        return 0.0

    weighted_score = 0.0
    for kw in overlap:
        weighted_score += 3.0 if kw in idea_name_keywords else 1.0

    max_possible = sum(3.0 if kw in idea_name_keywords else 1.0 for kw in idea_keywords)
    return round(weighted_score / max_possible, 3) if max_possible else 0.0


def filter_relevant_results(extracted: dict, search_results: list, min_relevance: float = 0.20) -> list:
    """
    Deterministically filters search results to only those relevant
    to the idea. Threshold raised from 0.08 to 0.20, and idea-name
    keywords are weighted 3x, so generic category-word matches (e.g.
    just "food") no longer pass, but genuine idea-specific matches
    (e.g. "panipuri", "vendors") do.
    """
    idea_name_keywords = extract_keywords(str(extracted.get("idea_name", "")))
    idea_text = " ".join([
        str(extracted.get("idea_name", "")),
        str(extracted.get("problem", "")),
        str(extracted.get("solution", "")),
        str(extracted.get("industry", "")),
    ])
    idea_keywords = extract_keywords(idea_text)

    scored = []
    for r in search_results:
        text = f"{r.get('title', '')} {r.get('content', '')}"
        score = relevance_score(idea_keywords, text, idea_name_keywords)
        if score >= min_relevance:
            r_copy = dict(r)
            r_copy["relevance"] = score
            scored.append(r_copy)

    scored.sort(key=lambda x: x["relevance"], reverse=True)
    return scored


def validate_extracted_idea(extracted: dict) -> dict:
    required = ["idea_name", "problem", "solution", "target_customer", "industry", "business_model"]
    missing = [f for f in required if not extracted.get(f) or not str(extracted.get(f)).strip()]
    return {"is_valid": len(missing) == 0, "missing_fields": missing}


def validate_search_results(results: list) -> dict:
    if not results:
        return {"is_valid": False, "reason": "empty_results", "count": 0}
    malformed = [r for r in results if not r.get("title") or not r.get("url")]
    return {
        "is_valid": len(malformed) < len(results),
        "reason": "all_malformed" if len(malformed) == len(results) else "ok",
        "count": len(results),
        "malformed_count": len(malformed),
    }


def deduplicate_by_domain(results: list) -> list:
    seen_domains = {}
    for r in results:
        url = r.get("url", "")
        domain = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
        existing = seen_domains.get(domain)
        if existing is None or r.get("relevance", 0) > existing.get("relevance", 0):
            seen_domains[domain] = r
    return list(seen_domains.values())
