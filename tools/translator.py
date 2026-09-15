"""
tools/translator.py
-----------------------
Fixes: "remove the multi-language selection - even if the user
enters a different language, give the output in English."

There is no language picker in the UI. This module's only job is to
silently normalize whatever the founder typed into English BEFORE it
reaches the (English-tuned) pipeline, so every agent's output is
always in English regardless of what language the idea was written
in. The UI only calls this when the input actually contains
non-ASCII characters (a cheap, zero-cost way to skip the LLM call
entirely for input that's already plain English).
"""

from agents.idea_extraction_agent import client
from app.config import MODEL_NAME


def translate_to_english(text: str) -> str:
    """Translates founder-written idea text into English. Returns the
    original text unchanged if translation fails, so a translation
    hiccup never blocks the pipeline from running."""
    if not text or not text.strip():
        return text
    prompt = f"""
Translate the following text to English. Keep it natural and
faithful to the original meaning - this describes a startup idea, so
preserve every specific detail (numbers, names, features). Respond
with ONLY the translated text, nothing else.

Text: "{text}"
"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return text
