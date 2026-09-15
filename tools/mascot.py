"""
tools/mascot.py
-------------------
A single walking companion that crosses the input box from left to
right while the pipeline runs, so the founder has a clear, honest
sense of "how long has this been going" instead of a bare spinner
(fixes: "the previous single-mascot version, not the emoji parade -
one character walking left to right on top of the input box, with a
changeable character, showing how long it's been waiting").

Movement is a genuine left-to-right walk tied to elapsed time - not a
looping parade. Since the true remaining time isn't knowable in
advance, the walk is asymptotic: it moves briskly at first and slows
as it approaches the right edge, so it visually communicates "still
going" for an arbitrarily long wait without ever claiming to be
finished before it actually is. It reaches the far right and stops
there only once the caller passes done=True.

Note on the character: Crayon Shin-chan is copyrighted character
art/likeness, so it isn't reproduced here. The options below are
generic, freely-usable emoji "walkers" instead - pick whichever one
you like from the sidebar. If you have your own licensed image asset
for a specific character, set CUSTOM_MASCOT_IMAGE_URL below (or per
-option, see MASCOT_OPTIONS) and it renders instead of the emoji.
"""

import math

MASCOT_OPTIONS = {
    "Walking Explorer": "\U0001F6B6",        # 🚶
    "Cartoon Kid": "\U0001F9D2",              # 🧒 (generic kid, not the copyrighted character)
    "Astronaut": "\U0001F9D1\u200D\U0001F680",  # 🧑‍🚀
    "Robot": "\U0001F916",                    # 🤖
    "Cat": "\U0001F408",                      # 🐱
    "Dinosaur": "\U0001F996",                 # 🦖
    "Ghost": "\U0001F47B",                    # 👻
}

# Optional: point this at your own licensed character sprite (a small
# transparent PNG works best) to use it instead of an emoji for EVERY
# choice above. Left empty by default since no such asset ships with
# this project - see the module docstring for why.
CUSTOM_MASCOT_IMAGE_URL = ""


def _progress_percent(elapsed_seconds: float, soft_ceiling_seconds: float = 35.0) -> float:
    """Asymptotic left-to-right progress: moves briskly at first,
    slows near the edge, never claims 100% until the caller says the
    job is actually done."""
    pct = 94 * (1 - math.exp(-elapsed_seconds / soft_ceiling_seconds))
    return max(2.0, min(pct, 94.0))


def render_progress_mascot(elapsed_seconds: float, mascot_name: str = "Walking Explorer", done: bool = False) -> str:
    """Returns an HTML snippet (for st.markdown(..., unsafe_allow_html=True))
    showing the chosen mascot's left-to-right position based on
    elapsed time, plus a live elapsed-time caption. Returns "" once
    done=True - the caller stops showing this entirely at that point."""
    if done:
        return ""

    pct = _progress_percent(elapsed_seconds)
    sprite = (
        f'<img src="{CUSTOM_MASCOT_IMAGE_URL}" style="height:28px; transform:scaleX(-1);" />'
        if CUSTOM_MASCOT_IMAGE_URL
        else f'<span style="font-size:26px; display:inline-block; transform:scaleX(-1);">'
             f'{MASCOT_OPTIONS.get(mascot_name, MASCOT_OPTIONS["Walking Explorer"])}</span>'
    )
    # scaleX(-1) flips a "walking left" emoji glyph to visually face
    # rightward, matching the actual left-to-right direction of travel.

    status_text = f"Working on it... {elapsed_seconds:.0f}s elapsed"

    return f"""
    <div style="margin: 6px 0 14px 0;">
        <div style="position: relative; height: 34px; width: 100%;
                    background: linear-gradient(90deg, #1E1B4B 0%, #312E81 100%);
                    border-radius: 999px; overflow: hidden; border: 1px solid #4C1D95;">
            <div style="position: absolute; top: 3px; left: calc({pct}% - 14px);
                        transition: left 1s linear;">
                {sprite}
            </div>
        </div>
        <div style="font-size: 12px; color: #A78BFA; margin-top: 4px;">
            {status_text}
        </div>
    </div>
    """
