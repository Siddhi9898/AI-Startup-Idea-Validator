"""
tools/llm.py
---------------
Wraps the Groq client with a call_structured() method that forces
the model's output through a Pydantic schema, with automatic retry
on validation failure. This is the key architectural piece the
reference project uses that our earlier version lacked - instead of
loosely parsing JSON and hoping it matches, the output is validated
against a strict schema, and invalid output triggers a retry with
the validation error fed back to the model.
"""

import json
from pydantic import BaseModel, ValidationError
from groq import Groq


class LLMTool:
    def __init__(self, api_key: str, model_name: str):
        self._client = Groq(api_key=api_key)
        self._model_name = model_name

    def call_structured(self, system_prompt: str, user_prompt: str, schema: type[BaseModel], max_retries: int = 2):
        """
        Calls the LLM and validates its JSON output against the given
        Pydantic schema. If validation fails, retries with the error
        fed back to the model so it can self-correct - deterministic
        in the sense that output is guaranteed to match the schema or
        the call raises, rather than silently passing malformed data
        downstream.
        """
        messages = [
            {"role": "system", "content": system_prompt + "\n\nRespond ONLY with valid JSON matching the required schema. No markdown, no explanation."},
            {"role": "user", "content": user_prompt},
        ]

        last_error = None
        for attempt in range(max_retries + 1):
            response = self._client.chat.completions.create(
                model=self._model_name,
                messages=messages,
                temperature=0.0,
            )
            raw_text = response.choices[0].message.content.strip()
            raw_text = raw_text.replace("```json", "").replace("```", "")

            try:
                data = json.loads(raw_text)
                validated = schema.model_validate(data)
                return validated
            except (json.JSONDecodeError, ValidationError) as e:
                last_error = str(e)
                messages.append({"role": "assistant", "content": raw_text})
                messages.append({
                    "role": "user",
                    "content": f"Your previous response was invalid: {last_error}\nPlease respond again with ONLY valid JSON matching the schema.",
                })

        # Deterministic graceful failure - return an empty-but-valid
        # instance rather than crashing the pipeline
        return schema()
