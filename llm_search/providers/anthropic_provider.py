from __future__ import annotations

from collections.abc import Iterator

from llm_search.providers.base import LLMProvider

try:
    import anthropic
except Exception:  # pragma: no cover - import guard
    anthropic = None  # type: ignore[assignment]


class AnthropicLLM(LLMProvider):
    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20240620",
        api_key: str | None = None,
        temperature: float = 0.0,
    ) -> None:
        if anthropic is None:
            raise RuntimeError("anthropic package not installed")
        self.model = model
        self.temperature = temperature
        self._client = anthropic.Anthropic(api_key=api_key)

    def generate(self, system: str, prompt: str) -> str:
        resp = self._client.messages.create(
            model=self.model,
            temperature=self.temperature,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )  # type: ignore[call-overload]
        return "".join(block.text for block in resp.content if hasattr(block, "text"))

    def stream(self, system: str, prompt: str) -> Iterator[str]:
        with self._client.messages.stream(
            model=self.model,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            yield from stream.text_stream
