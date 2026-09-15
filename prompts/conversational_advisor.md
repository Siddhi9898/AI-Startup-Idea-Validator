# Conversational Advisor Agent

**File:** `agents/conversational_advisor.py`
**Type:** LLM, multi-turn, with real conversation memory.

## Role
Answers the founder's follow-up questions about their own report,
remembering earlier questions/answers within the same session -
without re-explaining the whole report on every turn.

## How memory works
A running list of message dicts (`[{"role": "user"/"assistant",
"content": "..."}]`) is kept in `st.session_state`. The full list is
sent to the model on every call, so it has real memory of everything
asked/answered so far in this conversation. `reset_advisor_memory()`
is called whenever a NEW idea is validated, so the advisor never
carries over context from an unrelated previous idea.

## System context (first message in the history)
```
You are a startup mentor. The founder received this validation report:

Idea: {idea_name}
Viability Score: {score}/100
Honest Summary: {honest_summary}
Blind Spots: {blind_spots}

Answer the founder's follow-up questions directly and concisely,
using this report as context. Remember earlier questions and
answers in this conversation when answering new ones - do not ask
the founder to repeat information already given.
```

## Threading note (bugfix)
Only the plain network call runs inside the timeout-guarded worker
thread. Every `st.session_state` read/write happens on Streamlit's
main script thread - Streamlit's session state isn't reliably
accessible from a background thread, which was the root cause of the
advisor previously appearing to "not give an answer".

## Timeout
20 seconds, via `tools/timeout_utils.run_with_timeout` - on timeout
or any other exception, a plain-language error message is appended
to the conversation instead of leaving the founder with silence.
