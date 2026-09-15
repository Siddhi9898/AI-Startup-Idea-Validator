"""
tools/chat_ui.py
--------------------
Shared, aesthetic chat-bubble rendering used by BOTH the floating
bottom-right advisor widget and the full "Advisor Chat" tab, so the
two look consistent everywhere the founder can chat with the AI
(fixes: "user input in one color, AI output in another, both
aesthetic").

User messages: right-aligned, violet bubble (matches the app's
accent color used throughout style_block.py).
AI messages: left-aligned, dark slate bubble with a subtle border,
easy to tell apart from the user's bubble at a glance.
"""

import html

import streamlit as st


def render_chat_message(role: str, content: str):
    """Renders one chat turn as a styled bubble. role is 'user' or
    'assistant'."""
    safe_content = html.escape(content or "").replace("\n", "<br>")

    if role == "user":
        bubble_html = f"""
        <div style="display:flex; justify-content:flex-end; margin:8px 0;">
            <div style="background:linear-gradient(120deg, #7C3AED, #9F6BFF);
                        color:#FFFFFF; padding:10px 16px; border-radius:16px 16px 4px 16px;
                        max-width:82%; font-size:14px; line-height:1.4;
                        box-shadow:0 2px 8px rgba(124,58,237,0.25);">
                {safe_content}
            </div>
        </div>
        """
    else:
        bubble_html = f"""
        <div style="display:flex; justify-content:flex-start; margin:8px 0;">
            <div style="background:#1B2032; color:#E7E9F0; padding:10px 16px;
                        border-radius:16px 16px 16px 4px; max-width:82%; font-size:14px;
                        line-height:1.4; border:1px solid #2B3148;">
                {safe_content}
            </div>
        </div>
        """
    st.markdown(bubble_html, unsafe_allow_html=True)


def render_chat_history(history: list):
    """Renders a list of {"role", "content"} dicts as bubbles, in
    order. Skips any 'system' role entry (the advisor's hidden
    context-setting message isn't part of the visible conversation)."""
    for msg in history:
        if msg.get("role") in ("user", "assistant"):
            render_chat_message(msg["role"], msg.get("content", ""))
