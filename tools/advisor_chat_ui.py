"""
Advisor Chat Renderer
----------------------
Shared rendering for the Conversational Advisor's Q&A history, used
by both the "Advisor Chat" tab and the floating chat widget so the
two stay visually identical.

Previously each turn was just st.write(f"**You:** ...") /
st.write(f"**Advisor:** ...") stacked one after another as plain
paragraphs - with no card, spacing, or side placement to separate
them, the question and the (often long, multi-paragraph) answer ran
together into one wall of text, making it hard to tell where your
input ended and the advisor's output began.

This renders each turn as a QUESTION (left column) / ANSWER (right
column) pair, each in its own labeled, colored card, so a founder
can scan straight down the left side to see what they asked and
across to the right to see what they got back.
"""

import html

import streamlit as st

_CARD_CSS = """
<style>
.advisor-card {
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 14px;
    height: 100%;
}
.advisor-card-you {
    background-color: #201A33;
    border-left: 4px solid #8B5CF6;
}
.advisor-card-advisor {
    background-color: #10241C;
    border-left: 4px solid #34D399;
}
.advisor-card-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
}
.advisor-card-you .advisor-card-label { color: #C4B5FD; }
.advisor-card-advisor .advisor-card-label { color: #6EE7B7; }
.advisor-card-body {
    color: #E5E7EB;
    font-size: 14.5px;
    line-height: 1.5;
    white-space: pre-wrap;
}
</style>
"""

_css_injected_key = "_advisor_chat_ui_css_injected"


def _inject_css_once():
    if not st.session_state.get(_css_injected_key):
        st.markdown(_CARD_CSS, unsafe_allow_html=True)
        st.session_state[_css_injected_key] = True


def _card(label: str, text: str, kind: str):
    safe_text = html.escape(text)
    st.markdown(
        f"""<div class="advisor-card advisor-card-{kind}">
                <div class="advisor-card-label">{label}</div>
                <div class="advisor-card-body">{safe_text}</div>
            </div>""",
        unsafe_allow_html=True,
    )


def render_advisor_history(history: list):
    """
    Renders a stored advisor history (list of {"role", "content"}
    dicts, as produced by agents.conversational_advisor) as
    question/answer pairs: question on the left, answer on the
    right of the same row.
    """
    _inject_css_once()

    pending_question = None
    for msg in history:
        role = msg.get("role")
        if role == "system":
            continue
        if role == "user":
            pending_question = msg.get("content", "")
        elif role == "assistant":
            q_col, a_col = st.columns(2)
            with q_col:
                _card("YOU ASKED", pending_question or "", "you")
            with a_col:
                _card("ADVISOR", msg.get("content", ""), "advisor")
            pending_question = None

    # A question that hasn't been answered yet (e.g. still in-flight,
    # or a rare edge case) still shows up on the left so it's never
    # silently dropped from view.
    if pending_question is not None:
        q_col, _ = st.columns(2)
        with q_col:
            _card("YOU ASKED", pending_question, "you")