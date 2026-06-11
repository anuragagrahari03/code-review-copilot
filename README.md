# Code Review Copilot

An educational AI-assisted code review tool.

This project is built to teach the moving parts behind AI developer tools:

- how to collect useful code context from git
- how to turn that context into a model prompt
- how to support multiple model providers behind one interface
- how to parse model output into useful review findings
- how this can grow toward datasets, evaluation, and fine-tuning

The first version is a command-line tool. That is deliberate: a CLI keeps the
system small enough to understand while still solving a real problem.

## Quick Start

Run the deterministic mock reviewer:

```bash
PYTHONPATH=src python -m code_review_copilot review --provider mock
```

Review staged changes:

```bash
PYTHONPATH=src python -m code_review_copilot review --target staged
```

Return machine-readable output:

```bash
PYTHONPATH=src python -m code_review_copilot review --format json
```

Run tests:

```bash
python -m unittest discover -s tests
```

## Using a Local Model with Ollama

Install and run Ollama separately, then pull a code-capable model:

```bash
ollama pull stable-code
```

Run the reviewer:

```bash
PYTHONPATH=src python -m code_review_copilot review \
  --provider ollama \
  --model stable-code
```

For a MacBook Air M1 with 8 GB RAM, start with `stable-code`. See
[Local Model Setup](docs/local-model-setup.md) for installation, customization,
and the future fine-tuning path.

## Using an OpenAI-Compatible API

Many hosted model providers expose an OpenAI-compatible `/v1/chat/completions`
endpoint. Configure the API key in your shell:

```bash
export AI_API_KEY="your-key"
```

Then run:

```bash
PYTHONPATH=src python -m code_review_copilot review \
  --provider openai-compatible \
  --model gpt-4.1-mini \
  --api-base https://api.openai.com/v1
```

The provider name is intentionally generic. The goal is not to lock the project
to one vendor, but to teach the pattern: one review pipeline, many model
backends.

## Architecture

```text
git diff -> prompt builder -> model provider -> response parser -> report
```

- `git_utils.py` collects the code change to review.
- `prompts.py` creates the instruction sent to the model.
- `providers.py` hides provider-specific API details.
- `reviewer.py` orchestrates the review workflow.
- `cli.py` exposes the workflow as a command-line app.

## Why This Shape?

AI tools usually have two parts:

1. **Deterministic software**: collecting diffs, formatting prompts, parsing
   responses, enforcing output schemas, running tests.
2. **Probabilistic model behavior**: understanding intent, spotting risky code,
   explaining tradeoffs, and suggesting fixes.

Good AI engineering is mostly about building a reliable deterministic shell
around an unreliable-but-useful model. This project keeps that boundary visible.

## Learning Path

1. **Prompting**: edit `src/code_review_copilot/prompts.py` and observe how
   model behavior changes.
2. **Provider APIs**: read `src/code_review_copilot/providers.py` to see how
   different models can share one interface.
3. **Evaluation**: create small sample diffs and compare review quality across
   prompts/models.
4. **Data collection**: save diffs, model reviews, and human corrections.
5. **Fine-tuning**: train or fine-tune a model on high-quality examples once
   you have enough curated data.

Fine-tuning is intentionally later in the journey. Most useful AI products start
with prompting, retrieval/context, evaluation, and feedback loops before model
training becomes worthwhile.

More notes:

- [Learning Notes](docs/learning-notes.md)
- [Local Model Setup](docs/local-model-setup.md)
- [Model Training Roadmap](docs/model-training-roadmap.md)
