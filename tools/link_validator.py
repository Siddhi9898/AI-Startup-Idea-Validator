"""
Link Validator (fixes P9)
----------------------------
Lightweight check to filter out dead/404 links from search results
before showing them to the user. Uses a short timeout and fails
silently (skips the link) rather than blocking the whole pipeline.
"""

import requests


def is_link_alive(url: str, timeout: float = 2.5) -> bool:
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code < 400
    except Exception:
        return False


def filter_dead_links(results: list) -> list:
    """
    Filters out results whose URL is unreachable or returns an
    error status. Best-effort - if the check itself fails (e.g. no
    internet), the original list is returned unfiltered rather than
    blocking the pipeline.
    """
    filtered = []
    for r in results:
        url = r.get("url", "")
        if not url:
            continue
        try:
            if is_link_alive(url):
                filtered.append(r)
        except Exception:
            # If validation itself breaks, keep the result rather
            # than losing data entirely
            filtered.append(r)
    return filtered if filtered else results
