"""
Conversational Advisor Agent (with real LLM conversation context)
--------------------------------------------------------------------------
Implements the context/history concept exactly as described: without
memory, the model has to be re-told everything on every question
(like meeting someone for the first time, every time). The fix is
to maintain a growing list of message dicts (history = [{"role":
"user"/"assistant", "content": "..."}]) and pass the FULL list to
the model on every call, so it has real memory of the conversation
so far.

BUGFIX: the advisor was silently failing to answer. The previous
version ran the ENTIRE function - including all st.session_state
reads/writes - inside a worker thread via run_with_timeout(). Only
the main Streamlit script thread has a valid ScriptRunContext;
touching st.session_state from a background thread is unreliable
(it can silently no-op or raise), so the history was never actually
being populated with the model's answer, which is why the advisor
looked like it "wasn't giving an answer". The fix: keep every
st.session_state read/write on the main thread, and ONLY put the
actual network call (the slow, potentially-hanging part) inside the
timeout-guarded worker thread.

The UI call signature is unchanged: ask_advisor(question, result).
History is maintained internally via Streamlit's session_state, so
nothing in the UI needs to change to get real multi-turn memory.
"""

import streamlit as st
from agents.idea_extraction_agent import client
from app.config import MODEL_NAME
from tools.timeout_utils import run_with_timeout

_HISTORY_KEY = "advisor_llm_history"


def _call_llm_only(history: list) -> str:
    """
    The ONLY part of the advisor flow allowed to run inside the
    timeout-guarded worker thread - a plain network call with no
    Streamlit session_state access at all.
    """
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=history,
        temperature=0.0,  # deterministic per reviewer instruction
    )
    return response.choices[0].message.content.strip()


def _build_system_context(state_dict: dict) -> dict:
    """The first message in the history - establishes the report
    context once, so it doesn't need to be repeated on every turn."""
    context = f"""
You are a startup mentor. The founder received this validation report:

Idea: {state_dict.get('extracted', {}).get('idea_name', '')}
Viability Score: {state_dict.get('viability_score', {}).get('overall_score', '')}/100
Honest Summary: {state_dict.get('honest_summary', '')}
Blind Spots: {state_dict.get('blind_spots', [])}

Answer the founder's follow-up questions directly and concisely,
using this report as context. Remember earlier questions and
answers in this conversation when answering new ones - do not ask
the founder to repeat information already given.
"""
    return {"role": "system", "content": context}


def ask_advisor(question: str, state_dict: dict) -> str:
    # Initialize + mutate history on the MAIN thread only.
    if _HISTORY_KEY not in st.session_state:
        st.session_state[_HISTORY_KEY] = [_build_system_context(state_dict)]

    history = st.session_state[_HISTORY_KEY]
    history.append({"role": "user", "content": question})

    try:
        # Only the network call runs in the timeout-guarded thread -
        # it receives a plain list (a snapshot), not st.session_state
        # itself, so there's no cross-thread session access at all.
        answer = run_with_timeout(
            _call_llm_only, args=(list(history),), timeout_seconds=20.0
        )
    except Exception as e:
        answer = f"Sorry, I couldn't get an answer right now (possible connection issue: {e}). Please try again."
        # Don't leave a dangling user turn with no reply in history.
        history.append({"role": "assistant", "content": answer})
        st.session_state[_HISTORY_KEY] = history
        return answer

    # Save the model's answer into history too, so the NEXT question
    # has access to it - this is what makes multi-turn memory work
    history.append({"role": "assistant", "content": answer})
    st.session_state[_HISTORY_KEY] = history

    return answer


def reset_advisor_memory():
    """Call this when a NEW idea is validated, so the advisor doesn't
    carry over context from a previous, unrelated idea."""
    if _HISTORY_KEY in st.session_state:
        del st.session_state[_HISTORY_KEY]