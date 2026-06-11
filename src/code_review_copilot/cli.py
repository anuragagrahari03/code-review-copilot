from __future__ import annotations

import argparse
import json
import sys

from .config import ReviewConfig
from .git_utils import GitDiffError
from .providers import ProviderError, create_provider
from .reviewer import ReviewError, review_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="code-review-copilot",
        description="AI-assisted code review from a git diff.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    review = subparsers.add_parser("review", help="Review code changes")
    review.add_argument(
        "--target",
        choices=["working", "staged", "branch"],
        default="working",
        help="Which git changes to review.",
    )
    review.add_argument(
        "--base",
        default="main",
        help="Base branch for --target branch. Default: main.",
    )
    review.add_argument(
        "--provider",
        choices=["mock", "ollama", "openai-compatible"],
        default="mock",
        help="Model provider to use.",
    )
    review.add_argument(
        "--model",
        default=None,
        help="Model name. Example: stable-code or gpt-4.1-mini.",
    )
    review.add_argument(
        "--api-base",
        default=None,
        help="Base URL for model APIs. Optional for Ollama and OpenAI-compatible providers.",
    )
    review.add_argument(
        "--api-key-env",
        default="AI_API_KEY",
        help="Environment variable that stores the API key.",
    )
    review.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format.",
    )
    review.add_argument(
        "--max-diff-chars",
        type=int,
        default=40_000,
        help="Maximum diff characters to send to the model.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "review":
        config = ReviewConfig(
            target=args.target,
            base_branch=args.base,
            provider=args.provider,
            model=args.model,
            api_base=args.api_base,
            api_key_env=args.api_key_env,
            output_format=args.format,
            max_diff_chars=args.max_diff_chars,
        )
        try:
            provider = create_provider(config)
            result = review_repository(config, provider)
        except (GitDiffError, ProviderError, ReviewError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        if args.format == "json":
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(result.to_markdown())
        return 0

    parser.error("unknown command")
    return 2
