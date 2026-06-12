# Learning Notes

This project is a small version of the architecture used by many AI coding
tools.

## 1. The Model Is Not the Whole Product

The model is only one part. The surrounding software decides:

- what code context the model sees
- which instructions guide the model
- how strict the output format is
- how errors are handled
- how results are shown to the user

That surrounding software is often where the product quality comes from.

## 2. Why We Start With a CLI

A command-line tool is easier to reason about than a full web app:

- input is a git diff
- output is Markdown or JSON
- there is no database yet
- tests can cover most deterministic behavior

Once the core workflow is useful, it can be wrapped in a web UI, GitHub app, or
IDE extension.

## 3. Prompting

`prompts.py` contains two important ideas:

- a system prompt, which defines the reviewer role and output contract
- a user prompt, which contains the actual diff

Models are sensitive to instructions. Small wording changes can affect whether
the review is precise, noisy, strict, or vague.

## 4. Provider Abstraction

`providers.py` defines one common method:

```python
complete(prompt: str) -> str
```

The rest of the app does not care whether the response came from a mock model,
Ollama, OpenAI, Anthropic, Gemini, or a fine-tuned model. This is called an
abstraction boundary.

## 5. Why JSON Output Matters

Natural language is flexible, but software needs structure. The prompt asks the
model to return JSON so the app can reliably extract:

- severity
- file
- line
- title
- details

Real systems usually make this stricter with schemas, retries, and validation.

## 6. Fine-Tuning Comes Later

Fine-tuning teaches a model to behave differently by training on examples. For a
code review tool, examples might look like:

- input: a git diff
- output: a high-quality review written by an experienced engineer

Before fine-tuning, you need enough good examples. Bad training data teaches bad
habits. A practical path is:

1. build the prompt-based version
2. collect model reviews
3. correct those reviews by hand
4. measure quality
5. fine-tune only when prompting is no longer enough

## 7. Evaluation

Evaluation means checking whether the tool is improving. You can start with a
small folder of sample diffs and expected findings.

Good review findings are:

- specific
- actionable
- tied to changed code
- more focused on real risk than personal preference

This matters because AI models can sound confident even when they are wrong.
