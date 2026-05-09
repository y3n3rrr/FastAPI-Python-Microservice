from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any
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

    def generate_tool_plan(
        self,
        *,
        user_prompt: str,
        conversation_context: str,
        tool_definitions: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        provider = self.settings.assistant_llm_provider.strip().lower()
        if provider != "ollama":
            return None

        prompt = (
            "You are a planner agent for an ecommerce assistant.\n"
            "Output ONLY valid JSON with this schema:\n"
            "{\n"
            '  "intent": "string",\n'
            '  "steps": [{"tool": "string", "arguments": {"key": "value"}}]\n'
            "}\n"
            "Do not include markdown.\n"
            "Only use tools from this registry:\n"
            f"{json.dumps(tool_definitions, ensure_ascii=True)}\n\n"
            "Rules:\n"
            "- Keep steps minimal.\n"
            "- Use null when a filter is unknown.\n"
            "- If no tool is needed, return empty steps.\n\n"
            f"Conversation context:\n{conversation_context}\n\n"
            f"User message:\n{user_prompt}\n"
        )
        raw = self._generate_raw_via_ollama(prompt=prompt)
        if raw is None:
            return None
        parsed = _extract_json_object(raw)
        if not isinstance(parsed, dict):
            return None
        return parsed

    def generate_answer_from_tool_results(
        self,
        *,
        user_prompt: str,
        plan: dict[str, Any],
        results: list[dict[str, Any]],
        validation_issues: list[str],
    ) -> str | None:
        provider = self.settings.assistant_llm_provider.strip().lower()
        if provider != "ollama":
            return None
        prompt = (
            "You are an answer agent for an ecommerce assistant.\n"
            "Use tool execution results only. Do not invent data.\n"
            "If no results, say what is missing and suggest the next precise input.\n"
            "Keep the answer concise.\n\n"
            f"User message:\n{user_prompt}\n\n"
            f"Planner output:\n{json.dumps(plan, ensure_ascii=True)}\n\n"
            f"Tool results:\n{json.dumps(results, ensure_ascii=True)}\n\n"
            f"Validation issues:\n{json.dumps(validation_issues, ensure_ascii=True)}\n"
        )
        raw = self._generate_raw_via_ollama(prompt=prompt)
        if raw is None:
            return None
        answer = raw.strip()
        return answer or None

    def _generate_raw_via_ollama(self, *, prompt: str) -> str | None:
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
            return str(data.get("response", ""))
        except (error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            logger.warning("ollama call failed for agentic step: %s", exc)
            return None

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


def _extract_json_object(raw_text: str) -> dict[str, Any] | None:
    text = raw_text.strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end < 0 or end <= start:
            return None
        candidate = text[start : end + 1]
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            return None
    if not isinstance(parsed, dict):
        return None
    return parsed
