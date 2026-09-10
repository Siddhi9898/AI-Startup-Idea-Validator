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

The UI call signature is unchanged: ask_advisor(question, result).
History is maintained internally via Streamlit's session_state, so
nothing in the UI needs to change to get real multi-turn memory.
"""

import streamlit as st
from agents.idea_extraction_agent import client
from app.config import MODEL_NAME
from tools.timeout_utils import run_with_timeout

_HISTORY_KEY = "advisor_llm_history"
_IDEA_KEY = "advisor_llm_idea_name"  # tracks which idea the stored history belongs to


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


def _call_llm(messages: list) -> str:
    """
    PURE network call - this is the part that gets handed off to a
    worker thread by run_with_timeout(). It must never touch
    st.session_state or any other Streamlit API.

    Why: Streamlit's session_state is only accessible from the thread
    that is actually running the script (it needs a ScriptRunContext
    to know which browser session it belongs to). A ThreadPoolExecutor
    worker thread doesn't have that context, so any session_state
    read/write inside it either raises or silently no-ops. That was
    the real bug here - the old version read AND wrote
    st.session_state from inside the timed-out thread, so the
    advisor's answer could be generated successfully by the LLM and
    still never show up in the chat (or get eaten by the except
    Exception fallback). Keeping this function to "messages in,
    string out" fixes that at the source.
    """
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.0,  # deterministic per reviewer instruction
    )
    return response.choices[0].message.content.strip()


def ask_advisor(question: str, state_dict: dict) -> str:
    idea_name = state_dict.get("extracted", {}).get("idea_name", "")

    # Start a fresh conversation if there's no history yet, OR if the
    # idea behind the current report has changed since the last
    # question. This is a safety net on top of reset_advisor_memory():
    # even if something forgets to call that explicitly, the advisor
    # will never silently answer using a different idea's context.
    if _HISTORY_KEY not in st.session_state or st.session_state.get(_IDEA_KEY) != idea_name:
        st.session_state[_HISTORY_KEY] = [_build_system_context(state_dict)]
        st.session_state[_IDEA_KEY] = idea_name

    history = st.session_state[_HISTORY_KEY]
    history.append({"role": "user", "content": question})

    # Send a COPY of the full history to the worker thread every time -
    # that's what gives the model real multi-turn memory. session_state
    # itself is only read/written here, on the main thread.
    try:
        answer = run_with_timeout(_call_llm, args=(list(history),), timeout_seconds=20.0)
    except Exception as e:
        # Roll back the user turn we just added so a failed question
        # doesn't leave a dangling, unanswered entry in the stored
        # conversation (and so the founder can just retry cleanly).
        history.pop()
        st.session_state[_HISTORY_KEY] = history
        return f"Sorry, I couldn't get an answer right now (possible connection issue: {e}). Please try again."

    # Save the model's answer into history too, so the NEXT question
    # has access to it - this is what makes multi-turn memory work.
    # It also persists in st.session_state until the idea changes
    # (handled above) or the page is refreshed (a new session).
    history.append({"role": "assistant", "content": answer})
    st.session_state[_HISTORY_KEY] = history

    return answer


def reset_advisor_memory():
    """Call this when a NEW idea is validated, so the advisor doesn't
    carry over context from a previous, unrelated idea."""
    if _HISTORY_KEY in st.session_state:
        del st.session_state[_HISTORY_KEY]
    if _IDEA_KEY in st.session_state:
        del st.session_state[_IDEA_KEY]
