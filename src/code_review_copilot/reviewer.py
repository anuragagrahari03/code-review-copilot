from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from .config import ReviewConfig
from .git_utils import collect_diff, truncate_diff
from .prompts import build_review_prompt
from .providers import ModelProvider, ProviderError


class ReviewError(RuntimeError):
    """Raised when a review cannot be completed."""


@dataclass(frozen=True)
class Finding:
    severity: str
    file: str
    line: int | None
    title: str
    details: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Finding":
        severity = str(data.get("severity", "medium")).lower()
        if severity not in {"low", "medium", "high"}:
            severity = "medium"

        line = data.get("line")
        if not isinstance(line, int):
            line = None

        return cls(
            severity=severity,
            file=str(data.get("file") or "unknown"),
            line=line,
            title=str(data.get("title") or "Untitled finding"),
            details=str(data.get("details") or ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "file": self.file,
            "line": self.line,
            "title": self.title,
            "details": self.details,
        }


@dataclass(frozen=True)
class ReviewResult:
    summary: str
    findings: list[Finding]
    diff_truncated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "diff_truncated": self.diff_truncated,
            "findings": [finding.to_dict() for finding in self.findings],
        }

    def to_markdown(self) -> str:
        lines = ["# Code Review", "", self.summary]
        if self.diff_truncated:
            lines.extend(
                [
                    "",
                    "> Note: the diff was truncated before review, so findings may be incomplete.",
                ]
            )

        if not self.findings:
            lines.extend(["", "No findings."])
            return "\n".join(lines)

        lines.extend(["", "## Findings"])
        severity_rank = {"high": 0, "medium": 1, "low": 2}
        for finding in sorted(self.findings, key=lambda item: severity_rank[item.severity]):
            location = finding.file
            if finding.line is not None:
                location = f"{location}:{finding.line}"
            lines.extend(
                [
                    "",
                    f"### [{finding.severity.upper()}] {finding.title}",
                    "",
                    f"- Location: `{location}`",
                    f"- Details: {finding.details}",
                ]
            )
        return "\n".join(lines)


def review_repository(config: ReviewConfig, provider: ModelProvider) -> ReviewResult:
    diff = collect_diff(config.target, config.base_branch)
    if not diff:
        return ReviewResult(summary="No changes found for review.", findings=[])

    diff, was_truncated = truncate_diff(diff, config.max_diff_chars)
    prompt = build_review_prompt(diff)

    try:
        response = provider.complete(prompt)
    except ProviderError as exc:
        raise ReviewError(str(exc)) from exc

    result = parse_review_response(response)
    return ReviewResult(
        summary=result.summary,
        findings=result.findings,
        diff_truncated=was_truncated,
    )


def parse_review_response(response: str) -> ReviewResult:
    data = _load_json_object(response)
    findings_data = data.get("findings", [])
    if not isinstance(findings_data, list):
        raise ReviewError("model response field 'findings' must be a list")

    findings = []
    for item in findings_data:
        if isinstance(item, dict):
            findings.append(Finding.from_dict(item))

    summary = str(data.get("summary") or "Review completed.")
    return ReviewResult(summary=summary, findings=findings)


def _load_json_object(response: str) -> dict[str, Any]:
    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", response, flags=re.DOTALL)
        if not match:
            raise ReviewError("model did not return valid JSON") from None
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise ReviewError("model returned JSON-like text that could not be parsed") from exc

    if not isinstance(data, dict):
        raise ReviewError("model response must be a JSON object")
    return data
