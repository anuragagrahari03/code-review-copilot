from __future__ import annotations

SYSTEM_PROMPT = """You are a senior software engineer reviewing a git diff.
Focus on concrete correctness, security, reliability, performance, and test gaps.
Avoid style-only comments unless they hide a real maintainability risk.
Return only valid JSON with this shape:
{
  "summary": "one short paragraph",
  "findings": [
    {
      "severity": "low|medium|high",
      "file": "path/to/file.py",
      "line": 123,
      "title": "short issue title",
      "details": "why this matters and how to fix it"
    }
  ]
}
If there are no findings, return an empty findings array."""


def build_review_prompt(diff: str) -> str:
    return f"""Review this git diff.

```diff
{diff}
```"""
