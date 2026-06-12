# Model Training Roadmap

You do not need fine-tuning on day one. Most AI products should earn their way
there.

## Stage 1: Prompt-Based Product

Goal: make the tool useful with existing models.

Work to do:

- improve prompts
- support local and hosted models
- collect diffs safely
- produce structured findings
- add tests for deterministic code

This is where the current project starts.

## Stage 2: Evaluation Set

Goal: measure whether the tool is getting better.

Create a small set of examples:

```json
{
  "diff": "git diff text",
  "expected_findings": [
    {
      "severity": "high",
      "file": "auth.py",
      "title": "Missing authorization check"
    }
  ]
}
```

Evaluation teaches you which prompts and models actually work. Without
evaluation, you are mostly trusting vibes.

## Stage 3: Feedback Data

Goal: collect better examples from real use.

Useful signals:

- which findings humans accepted
- which findings humans dismissed
- corrected wording from reviewers
- missed issues that humans later found

This becomes your training dataset.

## Stage 4: Fine-Tuning

Goal: teach a model your preferred review style and issue taxonomy.

Fine-tuning can help with:

- consistent output format
- domain-specific review habits
- fewer noisy comments
- better severity calibration

Fine-tuning is less likely to help if the model does not have enough code
context or if your examples are inconsistent.

## Stage 5: Bigger Systems

Once the basics work, the same ideas scale into:

- GitHub pull request bot
- IDE extension
- review dashboard
- organization-specific policy checks
- retrieval over internal docs
- model evaluation pipeline

The important pattern stays the same:

```text
context -> instruction -> model -> validation -> human feedback -> evaluation
```
