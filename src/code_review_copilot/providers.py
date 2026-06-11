from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol

from .config import ReviewConfig
from .prompts import SYSTEM_PROMPT


class ModelProvider(Protocol):
    def complete(self, prompt: str) -> str:
        """Return a model response for the given user prompt."""


@dataclass(frozen=True)
class MockProvider:
    """Deterministic provider used for learning, demos, and tests."""

    def complete(self, prompt: str) -> str:
        findings = []
        if re.search(r"^\+\s*print\(", prompt, flags=re.MULTILINE):
            findings.append(
                {
                    "severity": "low",
                    "file": "unknown",
                    "line": 1,
                    "title": "Debug print added",
                    "details": "A committed print statement can leak noisy runtime output. Consider using structured logging or removing it.",
                }
            )
        if re.search(r"password|secret|api[_-]?key", prompt, flags=re.IGNORECASE):
            findings.append(
                {
                    "severity": "high",
                    "file": "unknown",
                    "line": 1,
                    "title": "Possible secret in change",
                    "details": "The diff contains text that looks like a credential. Verify it is not a real secret before committing.",
                }
            )
        summary = "Mock review completed. This provider uses simple rules instead of an AI model."
        return json.dumps({"summary": summary, "findings": findings})


@dataclass(frozen=True)
class OllamaProvider:
    model: str = "qwen2.5-coder:3b"
    api_base: str = "http://localhost:11434"

    def complete(self, prompt: str) -> str:
        url = f"{self.api_base.rstrip('/')}/api/chat"
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "format": "json",
        }
        response = _post_json(url, payload, headers={})
        try:
            return response["message"]["content"]
        except KeyError as exc:
            raise ProviderError(f"unexpected Ollama response shape: {response}") from exc


@dataclass(frozen=True)
class OpenAICompatibleProvider:
    model: str
    api_key: str
    api_base: str = "https://api.openai.com/v1"

    def complete(self, prompt: str) -> str:
        url = f"{self.api_base.rstrip('/')}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = _post_json(url, payload, headers=headers)
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise ProviderError(f"unexpected API response shape: {response}") from exc


class ProviderError(RuntimeError):
    """Raised when a model provider fails."""


def create_provider(config: ReviewConfig) -> ModelProvider:
    if config.provider == "mock":
        return MockProvider()

    if config.provider == "ollama":
        return OllamaProvider(
            model=config.model or "qwen2.5-coder:3b",
            api_base=config.api_base or "http://localhost:11434",
        )

    if config.provider == "openai-compatible":
        api_key = os.getenv(config.api_key_env)
        if not api_key:
            raise ProviderError(
                f"missing API key. Set {config.api_key_env} or pass --api-key-env."
            )
        return OpenAICompatibleProvider(
            model=config.model or "gpt-4.1-mini",
            api_key=api_key,
            api_base=config.api_base or "https://api.openai.com/v1",
        )

    raise ProviderError(f"unsupported provider: {config.provider}")


def _post_json(url: str, payload: dict, headers: dict[str, str]) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            **headers,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise ProviderError(f"provider HTTP error {exc.code}: {details}") from exc
    except urllib.error.URLError as exc:
        raise ProviderError(f"provider connection error: {exc.reason}") from exc
