class LLMClient:
    """Placeholder LLM adapter.

    This keeps the interface stable while provider integration is implemented.
    """

    def generate_answer(self, prompt: str) -> str:
        return f"Assistant: {prompt}"
