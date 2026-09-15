"""
tools/mascot.py
-------------------
<<<<<<< HEAD
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
=======
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
>>>>>>> 14d1a88d30347689a3f1a51ab41d371192e50019
"""

import math

MASCOT_OPTIONS = {
<<<<<<< HEAD
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
=======
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
>>>>>>> 14d1a88d30347689a3f1a51ab41d371192e50019
CUSTOM_MASCOT_IMAGE_URL = ""


def _progress_percent(elapsed_seconds: float, soft_ceiling_seconds: float = 35.0) -> float:
<<<<<<< HEAD
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
=======
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
>>>>>>> 14d1a88d30347689a3f1a51ab41d371192e50019

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
