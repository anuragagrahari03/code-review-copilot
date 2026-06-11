from __future__ import annotations

import subprocess


class GitDiffError(RuntimeError):
    """Raised when a git diff cannot be collected."""


def collect_diff(target: str, base_branch: str) -> str:
    if target == "working":
        args = ["git", "diff", "--no-ext-diff", "--unified=80"]
    elif target == "staged":
        args = ["git", "diff", "--cached", "--no-ext-diff", "--unified=80"]
    elif target == "branch":
        args = ["git", "diff", "--no-ext-diff", "--unified=80", f"{base_branch}...HEAD"]
    else:
        raise GitDiffError(f"unsupported review target: {target}")

    completed = subprocess.run(args, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        details = completed.stderr.strip() or "git diff failed"
        raise GitDiffError(details)

    return completed.stdout.strip()


def truncate_diff(diff: str, max_chars: int) -> tuple[str, bool]:
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    if len(diff) <= max_chars:
        return diff, False
    notice = (
        "\n\n[Diff truncated by Code Review Copilot. "
        "Review may miss issues outside this excerpt.]\n"
    )
    if max_chars <= len(notice):
        return notice[:max_chars], True
    return diff[: max_chars - len(notice)] + notice, True
