"""
Floating Advisor Icon (bottom-right, Infosys-style chatbot widget)
------------------------------------------------------------------------
Single circular icon, fixed bottom-right corner, matching the style
<<<<<<< HEAD
of a typical corporate website chatbot widget - visible from every
tab since it's rendered once, outside the tabs structure, with fixed
positioning. Two small CSS-animated "eyes" blink periodically, giving
it a friendly "I'm watching and waiting for your question" feel
(fixes: "the chatbot should close and open its eyes like it's
eagerly waiting for your questions"). Clicking it opens the
=======
of a typical corporate website chatbot widget. Clicking it opens the
>>>>>>> 14d1a88d30347689a3f1a51ab41d371192e50019
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
<<<<<<< HEAD
            background-image: none !important;
            position: relative;
=======
            background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'><path d='M12 2C6.48 2 2 6.02 2 11c0 2.72 1.36 5.15 3.5 6.8V22l4.03-2.2c.8.14 1.62.2 2.47.2 5.52 0 10-4.02 10-9S17.52 2 12 2zm-1 12H8v-2h3v2zm5-3h-8v-2h8v2zm0-3h-8V8h8v2z'/></svg>");
            background-repeat: no-repeat;
            background-position: center;
            background-size: 30px 30px;
>>>>>>> 14d1a88d30347689a3f1a51ab41d371192e50019
            transition: transform 0.15s ease, background-color 0.15s ease;
        }
        div[data-testid="stPopover"] > div > button:hover {
            background-color: #7C3AED !important;
            transform: scale(1.06);
        }
<<<<<<< HEAD
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
=======
>>>>>>> 14d1a88d30347689a3f1a51ab41d371192e50019
        </style>
        """,
        unsafe_allow_html=True,
    )

<<<<<<< HEAD
    with st.popover("", use_container_width=False, help="Ask me anything about your report - I'm waiting for your questions!"):
=======
    with st.popover("", use_container_width=False):
>>>>>>> 14d1a88d30347689a3f1a51ab41d371192e50019
        st.markdown("**Ask the Advisor**")
        st.caption("Remembers earlier questions in this session.")

        from agents.conversational_advisor import ask_advisor, _HISTORY_KEY
<<<<<<< HEAD
        from tools.chat_ui import render_chat_history

        if _HISTORY_KEY in st.session_state:
            render_chat_history(st.session_state[_HISTORY_KEY])
=======

        if _HISTORY_KEY in st.session_state:
            for msg in st.session_state[_HISTORY_KEY]:
                if msg["role"] == "user":
                    st.write(f"**You:** {msg['content']}")
                elif msg["role"] == "assistant":
                    st.write(f"**Advisor:** {msg['content']}")
>>>>>>> 14d1a88d30347689a3f1a51ab41d371192e50019

        with st.form(key="floating_advisor_form", clear_on_submit=True):
            question = st.text_input("Your question:", label_visibility="collapsed", placeholder="Ask about your report...")
            submitted = st.form_submit_button("Send")

        if submitted and question.strip():
            with st.spinner("Thinking..."):
                ask_advisor(question, result, st.session_state.get("current_validation_id"))
            st.rerun()