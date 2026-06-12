from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewConfig:
    target: str = "working"
    base_branch: str = "main"
    provider: str = "mock"
    model: str | None = None
    api_base: str | None = None
    api_key_env: str = "AI_API_KEY"
    output_format: str = "markdown"
    max_diff_chars: int = 40_000
