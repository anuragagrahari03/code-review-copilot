# Local Model Setup for MacBook Air M1 8 GB

This guide is tuned for a MacBook Air M1 with 8 GB unified memory.

## Recommended Model

Start with:

```bash
qwen2.5-coder:3b
```

Why this model:

- it is code-specific
- it has a 32K context window in Ollama
- the model download is about 1.9 GB
- it is much more comfortable on 8 GB RAM than a 7B model

You can later try `qwen2.5-coder:7b`, but close memory-heavy apps first. Avoid
14B, 32B, and larger models on this laptop.

## Step 1: Install Ollama

Download Ollama for macOS:

```text
https://ollama.com/download
```

After installation, open the Ollama app once. Then confirm the CLI works:

```bash
ollama --version
```

Ollama runs a local API server at:

```text
http://localhost:11434
```

Our Python app talks to that local server.

## Step 2: Download the Model

```bash
ollama pull qwen2.5-coder:3b
```

Test it directly:

```bash
ollama run qwen2.5-coder:3b
```

Ask:

```text
Explain this code review tool in simple terms.
```

Exit with:

```text
/bye
```

## Step 3: Run This Project With Ollama

From the project root:

```bash
PYTHONPATH=src python -m code_review_copilot review \
  --provider ollama \
  --model qwen2.5-coder:3b
```

If you created staged changes and want to review only those:

```bash
PYTHONPATH=src python -m code_review_copilot review \
  --provider ollama \
  --model qwen2.5-coder:3b \
  --target staged
```

## Step 4: Create a Custom Local Reviewer

This is not fine-tuning. It is prompt-based customization using Ollama's
`Modelfile`. Think of it as giving the model a default personality and runtime
settings.

Create the custom model:

```bash
ollama create code-reviewer -f models/code-reviewer.Modelfile
```

Run it in the terminal:

```bash
ollama run code-reviewer
```

Use it from this project:

```bash
PYTHONPATH=src python -m code_review_copilot review \
  --provider ollama \
  --model code-reviewer
```

## Why Not Fine-Tune Immediately?

Fine-tuning means changing model weights using examples. Your MacBook can be
used for small experiments, but 8 GB RAM is tight. For now, the best learning
path is:

1. run a local model
2. improve prompts
3. collect review examples
4. build an evaluation set
5. try small LoRA fine-tuning later

This mirrors how real AI products are usually built. You first learn what good
outputs look like, then train on those examples.

## Future Fine-Tuning Path

When you are ready, use Apple MLX/MLX-LM for small LoRA experiments.

High-level shape:

```text
training data -> base model -> LoRA adapter -> evaluation -> optional export
```

Your training data should look like code review conversations:

```json
{"messages":[{"role":"user","content":"Review this diff: ..."},{"role":"assistant","content":"{\"summary\":\"...\",\"findings\":[...]}"}]}
```

Start tiny: 20 to 50 high-quality examples. Quality matters much more than
quantity at this stage.

## Sources

- Ollama macOS docs: https://docs.ollama.com/macos
- Ollama Qwen2.5-Coder model page: https://ollama.com/library/qwen2.5-coder
- Ollama Modelfile docs: https://docs.ollama.com/modelfile
- MLX-LM LoRA docs: https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md
