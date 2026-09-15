"""
Link Validator
-----------------
Deterministically checks whether search result URLs actually load
(not 404, not dead), before showing them to the user. Fixes P9.
Uses short timeouts so this never hangs the pipeline (also helps P10).
"""

import requests


def is_link_alive(url: str, timeout: float = 3.0) -> bool:
    """
    Deterministic check: does this URL return a successful response?
    Uses HEAD first (cheap), falls back to GET if HEAD isn't supported.
    Any exception (timeout, connection error, DNS failure) = not alive.
    """
    if not url:
        return False
    try:
        resp = requests.head(url, timeout=timeout, allow_redirects=True)
        if resp.status_code < 400:
            return True
        # Some sites don't support HEAD properly - try GET as fallback
        resp = requests.get(url, timeout=timeout, allow_redirects=True, stream=True)
        return resp.status_code < 400
    except requests.RequestException:
        return False


def filter_alive_links(results: list, timeout: float = 3.0) -> list:
    """
    Filters a list of search results down to only those whose URLs
    are actually reachable right now. Deterministic given the same
    network state; drops dead/404 links so the user never clicks
    through to a broken page.
    """
    alive = []
    for r in results:
        if is_link_alive(r.get("url", ""), timeout=timeout):
            alive.append(r)
    return alive
