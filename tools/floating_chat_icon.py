"""
Floating Advisor Icon (bottom-right, Infosys-style chatbot widget)
------------------------------------------------------------------------
Single circular icon, fixed bottom-right corner, matching the style
of a typical corporate website chatbot widget - visible from every
tab since it's rendered once, outside the tabs structure, with fixed
positioning. Two small CSS-animated "eyes" blink periodically, giving
it a friendly "I'm watching and waiting for your question" feel
(fixes: "the chatbot should close and open its eyes like it's
eagerly waiting for your questions"). Clicking it opens the
Conversational Advisor chat panel. Uses st.popover() (native
Streamlit component - reliable, no fragile JS needed).
"""

import streamlit as st


def render_floating_assistant(result: dict):
    st.markdown(
        """
        <style>
        div[data-testid="stPopover"] {
            position: fixed;
            bottom: 26px;
            right: 26px;
            z-index: 9999;
        }
        div[data-testid="stPopover"] > div > button {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background-color: #6D28D9 !important;
            color: white !important;
            box-shadow: 0 6px 16px rgba(0,0,0,0.35);
            border: none !important;
            font-size: 0 !important;
            background-image: none !important;
            position: relative;
            transition: transform 0.15s ease, background-color 0.15s ease;
        }
        div[data-testid="stPopover"] > div > button:hover {
            background-color: #7C3AED !important;
            transform: scale(1.06);
        }
        /* Two blinking "eyes" with pupils (fixes: chatbot that looks
           like it's eagerly watching and waiting for your question) -
           pure CSS via radial-gradient (a dark pupil ringed by white),
           no images/JS/extra DOM elements needed. */
        div[data-testid="stPopover"] > div > button::before,
        div[data-testid="stPopover"] > div > button::after {
            content: "";
            position: absolute;
            top: 19px;
            width: 13px;
            height: 13px;
            background: radial-gradient(circle at center, #1E1B4B 0 3.5px, #FFFFFF 4px 100%);
            border-radius: 50%;
            animation: chatbot-blink 4s ease-in-out infinite;
        }
        div[data-testid="stPopover"] > div > button::before { left: 14px; }
        div[data-testid="stPopover"] > div > button::after { right: 14px; }
        @keyframes chatbot-blink {
            0%, 88%, 100% { transform: scaleY(1); }
            92%, 96% { transform: scaleY(0.12); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.popover("", use_container_width=False, help="Ask me anything about your report - I'm waiting for your questions!"):
        st.markdown("**Ask the Advisor**")
        st.caption("Remembers earlier questions in this session.")

        from agents.conversational_advisor import ask_advisor, _HISTORY_KEY
        from tools.chat_ui import render_chat_history

        if _HISTORY_KEY in st.session_state:
            render_chat_history(st.session_state[_HISTORY_KEY])

        with st.form(key="floating_advisor_form", clear_on_submit=True):
            question = st.text_input("Your question:", label_visibility="collapsed", placeholder="Ask about your report...")
            submitted = st.form_submit_button("Send")

        if submitted and question.strip():
            with st.spinner("Thinking..."):
                ask_advisor(question, result, st.session_state.get("current_validation_id"))
            st.rerun()