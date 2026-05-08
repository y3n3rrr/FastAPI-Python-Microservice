from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from urllib import error, request

from app.core.config import get_settings


logger = logging.getLogger("app")


@dataclass
class LLMResponse:
    answer: str
    model: str


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def generate_answer(
        self,
        *,
        user_prompt: str,
        database_context: str,
        conversation_context: str,
    ) -> LLMResponse:
        provider = self.settings.assistant_llm_provider.strip().lower()
        if provider != "ollama":
            return LLMResponse(answer=f"Assistant: {user_prompt}", model="mock-llm-v1")

        prompt = self._build_prompt(
            user_prompt=user_prompt,
            database_context=database_context,
            conversation_context=conversation_context,
        )
        return self._generate_via_ollama(prompt=prompt, user_fallback=user_prompt)

    def _build_prompt(self, *, user_prompt: str, database_context: str, conversation_context: str) -> str:
        return (
            "You are a backend shopping assistant.\n"
            "Use ONLY the provided database context for factual claims.\n"
            "If the answer cannot be found in context, say you could not find enough data.\n"
            "Keep answers concise and practical.\n\n"
            f"Conversation context:\n{conversation_context}\n\n"
            f"Database context:\n{database_context}\n\n"
            f"User question:\n{user_prompt}\n"
        )

    def _generate_via_ollama(self, *, prompt: str, user_fallback: str) -> LLMResponse:
        base = self.settings.assistant_ollama_base_url.rstrip("/")
        model = self.settings.assistant_ollama_model
        timeout = max(1, self.settings.assistant_ollama_timeout_seconds)
        endpoint = f"{base}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(endpoint, data=body, headers={"Content-Type": "application/json"}, method="POST")

        try:
            with request.urlopen(req, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            answer = str(data.get("response", "")).strip()
            if not answer:
                answer = "I could not generate an answer from the model response."
            return LLMResponse(answer=answer, model=str(data.get("model", model)))
        except (error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            logger.warning("ollama generation failed; fallback response will be used: %s", exc)
            return LLMResponse(answer=f"Assistant: {user_fallback}", model="mock-llm-v1")
