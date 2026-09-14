"""
tools/mascot.py
-------------------
A walking progress "mascot" that visually crosses the top of the
input box while the pipeline runs, so the founder has something to
watch and a live elapsed-time readout instead of staring at a bare
spinner with no sense of how long it's been (fixes: "the user
doesn't know how much time it's taken").

Note on the character: the request that inspired this asked for the
Crayon Shin-chan character specifically. That's copyrighted character
art/likeness, so it isn't reproduced here. Instead this renders a
small set of generic, freely-usable emoji "walkers" the founder can
pick between (persisted in st.session_state), which delivers the
same feature - a walking companion that's "waiting" for the result
right along with you. If you have your own licensed image asset for
a specific character, drop its file path/URL into
CUSTOM_MASCOT_IMAGE_URL below and it'll be used instead of the emoji.
"""

import math

MASCOT_OPTIONS = {
    "Walking Explorer": "\U0001F6B6",       # 🚶
    "Astronaut": "\U0001F9D1\u200D\U0001F680",  # 🧑‍🚀
    "Robot": "\U0001F916",                  # 🤖
    "Cat": "\U0001F408",                    # 🐱
    "Dinosaur": "\U0001F996",               # 🦖
    "Ghost": "\U0001F47B",                  # 👻
}

# Optional: point this at your own licensed character sprite (a small
# transparent PNG works best) to use it instead of an emoji. Left
# empty by default since no such asset ships with this project.
CUSTOM_MASCOT_IMAGE_URL = ""


def _progress_percent(elapsed_seconds: float, soft_ceiling_seconds: float = 35.0) -> float:
    """
    Asymptotic progress: creeps toward ~95% but never claims 100%
    until the caller says the job is actually done (there's no way
    to know the true remaining time in advance, so a fake linear bar
    that hits 100% early and then sits there would be more
    misleading than an honestly-asymptotic one).
    """
    pct = 95 * (1 - math.exp(-elapsed_seconds / soft_ceiling_seconds))
    return max(2.0, min(pct, 95.0))


def render_progress_mascot(elapsed_seconds: float, mascot_name: str, done: bool = False) -> str:
    """Returns an HTML snippet (for st.markdown(..., unsafe_allow_html=True))
    showing a small track with the mascot's horizontal position based
    on elapsed time, plus a live elapsed-time caption."""
    pct = 100.0 if done else _progress_percent(elapsed_seconds)
    sprite = CUSTOM_MASCOT_IMAGE_URL and f'<img src="{CUSTOM_MASCOT_IMAGE_URL}" style="height:28px;" />' \
        or f'<span style="font-size:26px;">{MASCOT_OPTIONS.get(mascot_name, MASCOT_OPTIONS["Walking Explorer"])}</span>'

    status_text = "Done!" if done else f"Working on it... {elapsed_seconds:.0f}s elapsed"

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
