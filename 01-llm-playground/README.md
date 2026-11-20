# Project 1: LLM Playground

See what happens between a prompt and a reply. Inspect tokenization, step through decoding, tune sampling and compare models on the same prompt.

## Stack

Ollama, Hugging Face transformers (Qwen2.5 0.5B), tiktoken, Streamlit, SQLite.

## Setup

Needs uv and Ollama (`brew install uv ollama`). From this folder:

```bash
uv sync                                  # create .venv with Python 3.12 and all libraries
uv run python scripts/smoke_test.py      # load Qwen2.5 0.5B on mps, print top 5 next tokens
uv run pytest -m "not slow"              # fast tests; drop the -m flag to include model tests
ollama serve                             # start the Ollama server when a step needs it
```

See [PLAN.md](PLAN.md) for how each step is built.

## Build steps

- [x] 1. Run three or four local models from different families through Ollama.
- [ ] 2. Tokenizer explorer: tokens, IDs and token counts across tokenizers.
- [ ] 3. Hand written decoding loop: greedy, temperature, top k, top p and beam search, with per step probability charts.
- [ ] 4. Chat UI with model picker, decoding sliders, system prompt and streaming.
- [ ] 5. Side by side model comparison with latency and tokens per second.
- [ ] 6. Eval harness: 20 to 30 prompts, exact match and LLM judge, results in SQLite.
- [ ] 7. Base versus instruct model on the same prompts.
- [ ] 8. Stretch: small supervised fine tune with TRL.

## Done when

The UI and eval results show how sampling settings change the output.

## Findings

Results and trade offs are added here as steps are completed. Full numbers and notes are in [LAB_NOTES.md](LAB_NOTES.md).

### Step 1: four local models on an M2 Pro (32 GB)

From `uv run python scripts/bench_ollama.py`: prefill on about 1,430 tokens, decode over 200 tokens at temperature 0, medians of 3.

| Model | Cold load | Warm load | Prefill | Decode | Memory at 32k context |
|---|---|---|---|---|---|
| llama3.2:3b | 2.85 s | 1 ms | 751 tok/s | 66.3 tok/s | 5.6 GiB |
| qwen3:4b | 2.42 s | 2 ms | 563 tok/s | 53.8 tok/s | 7.0 GiB |
| gemma3:4b | 2.47 s | 1 ms | 637 tok/s | 53.9 tok/s | 2.8 GiB |
| deepseek-r1:7b | 3.51 s | 1 ms | 343 tok/s | 33.4 tok/s | 5.7 GiB |

A rerun of Llama alone gave 71.1 tok/s decode, so expect up to about 7% noise between sessions.

- Decode speed follows model size: every token reads all the weights, and all four move 130 to 160 GB/s of the chip's 200 GB/s.
- Prefill is only 10 to 12 times faster than decode on this GPU, because prefill is limited by arithmetic, not memory.
- At a 32k context the KV cache can outweigh the weights: Llama and Qwen3 hold more cache than model. DeepSeek and Gemma don't, and Gemma's sliding window attention cuts its cache to a fifth of Qwen3's.
- Reasoning models spend most of their time thinking: Qwen3 wrote 1,145 tokens where Gemma wrote 56 for the same question, at the same speed per token.
- Only one model fits in memory at a time with other apps open, so each model switch costs about 3 s of loading.
