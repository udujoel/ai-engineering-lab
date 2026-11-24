# Project 1 build plan

How to build the LLM Playground so that each step teaches one idea and ends with a number you measured. The step list in [README.md](README.md) stays the checklist. This file explains how to do each step.

By the end you should be able to explain, using your own UI and eval data, what happens between a prompt and a reply. That covers how text becomes tokens, how logits become one chosen token, why sampling settings change the output, and how post training changes behaviour.

## Your machine

| Item | Value | What it means |
|---|---|---|
| Chip and memory | M2 Pro, 32 GB unified | Quantised models up to about 14B run well. Use the `mps` device for transformers. |
| Free disk | 37 GB (disk is 96% full) | Keep Ollama models to about 12 GB and Hugging Face downloads to about 3 GB. Free some space first. |
| uv, Ollama | Not installed | Step 0 installs both. |
| Hugging Face cache | MLX builds of Qwen3 1.7B and Gemma 4 E2B | Not used here. They could be a later MLX vs PyTorch speed check. |

## What the research changed

1. **Ollama now returns log probabilities.** `/api/chat` accepts `logprobs: true` and `top_logprobs` (0 to 20) on models that support it. So the "top ten next tokens" chart can show the large Ollama models too, not only the 0.5B model. Use it as a cross check against your hand written loop. It needs a recent Ollama release.
2. **Timing comes free from Ollama.** The final response carries `eval_count`, `eval_duration`, `prompt_eval_count`, `prompt_eval_duration` and `load_duration`, all durations in nanoseconds. Tokens per second is `eval_count / eval_duration * 1e9`. Measure time to first token yourself on the client.
3. **transformers is on major version 5.** In a hand written loop with a KV cache, feed only the newest token plus `past_key_values` after the first step. Feeding the whole sequence again corrupts output. Pin the version in `pyproject.toml`.
4. **Keep Qwen2.5 0.5B for the low level work.** It has a clean base and instruct pair. Qwen3 0.6B also has both, but the instruct model has a thinking mode, and its model card warns that greedy decoding leads to repetition. That would muddy the first greedy vs sampling lesson. Add it later as an experiment that tests the model card's claim.
5. **Ollama model names move fast.** The tags in the original guide (`qwen2.5:7b`, `gemma2:9b`) still work but are a generation old. Check current tags and sizes on ollama.com/library before you pull.

## Models

**Ollama, four families, about 12 GB in total.** The tags below are examples, so confirm them first.

| Family | Example tag | What it teaches |
|---|---|---|
| Qwen | `qwen3:4b` | Qwen3 4B Thinking 2507: always reasons, `--think=false` does not stop it. Kept on purpose to show the cost of reasoning. |
| Gemma | `gemma3:4b` or the smallest `gemma4` | Very large vocabulary (about 256k), so it spends fewer tokens on non English text |
| Llama | `llama3.2:3b` | Meta baseline with a 128k vocabulary |
| Reasoning | `deepseek-r1:7b` | Thinking tokens and what they cost in latency |

**Hugging Face.**

- Full models: `Qwen/Qwen2.5-0.5B` and `Qwen/Qwen2.5-0.5B-Instruct`, about 1 GB each.
- Tokenizers only, a few MB each: `gpt2`, `Qwen/Qwen2.5-0.5B`, `HuggingFaceTB/SmolLM2-135M`, `microsoft/Phi-4-mini-instruct`.
- tiktoken: `cl100k_base` and `o200k_base`.

The Llama and Gemma tokenizers on Hugging Face are gated: you have to accept the licence and use an HF token. To skip that, count tokens for the Ollama models through Ollama itself. Send text to `/api/generate` with `raw: true` and read `prompt_eval_count`.

## Layout

```
01-llm-playground/
  pyproject.toml
  .env.example
  src/playground/
    device.py           # mps or cpu
    hf_model.py         # load model and tokenizer, next token logits
    decoding.py         # greedy, temperature, top k, top p, beam
    tokenizers.py       # wrappers over tiktoken, AutoTokenizer and Ollama counts
    ollama_client.py    # chat, stream, stats, logprobs
    compare.py          # run one prompt on N models, collect metrics
    evals/
      prompts.jsonl     # 20 to 30 prompts with expected answers
      scorers.py        # exact match normalisation, judge rubric
      store.py          # SQLite schema and writes
      run.py            # grid runner
  app/
    Home.py
    pages/
      1_Tokenizers.py
      2_Decoding.py
      3_Chat.py
      4_Compare.py
      5_Evals.py
      6_Base_vs_Instruct.py
  tests/
    test_decoding.py
    test_scorers.py
  data/                 # gitignored: playground.db
```

## Who does what

Claude writes all the code and explains each piece as it goes. Your job is to follow along, run the app, look at the results and make the calls that need judgement:

- which prompts belong in the eval set and what counts as a correct answer
- whether the LLM judge agrees with your own reading of 10 outputs
- what the numbers mean, written up in the README Findings section

You also run every step yourself. Each step comes as small parts: the commands to type, what each one does, and what output to expect. You run them, and then we read the results together. When a step needs code, Claude writes the file and explains it, and you run it.

`decoding.py` (step 3) gets the most explanation, because it is the heart of the project.

## Steps

Each step has four parts: the concept, what to build, the experiment that backs it up, and how you know it's done.

### Step 0. Setup (about 1 hour)

- Free disk space, then install uv and the Ollama app.
- `uv init` in `01-llm-playground`, then add `torch`, `transformers`, `tiktoken`, `ollama`, `streamlit`, `pandas`, `altair`, `pytest` and `ruff`.
- Add a `device.py` helper that returns `mps` when available.
- Check with a smoke test that loads Qwen2.5 0.5B on MPS and prints one next token.

### Step 1. Local models through Ollama

- **Concept.** A model is a weights file plus a runtime. Quantisation (Q4, Q8) trades accuracy for memory and speed.
- **Build.** Pull four models. Write `ollama_client.chat()` that returns the text plus a stats dict.
- **Experiment.** For each model, record cold load time, warm tokens per second and memory used. The model with the best tokens per second is often not the smallest one, so check.
- **Done when** a table in the README lists the four models with those three numbers.

### Step 2. Tokenizer explorer

- **Concept.** Models see integer IDs, not words. The vocabulary decides how many tokens a text costs, which drives price, context length and speed.
- **Build.** A page where you type text and see coloured token pieces, IDs and counts for six or more tokenizers side by side.
- **Experiment.** Use one fixed test set: an English paragraph, the same paragraph in Portuguese, a Python function, a JSON blob, emoji and numbers like `1234567`. Chart tokens per character for each tokenizer. Look at how each one splits numbers and leading spaces.
- **Done when** you can say which tokenizer is cheapest for Portuguese and why.

### Step 3. Hand written decoding loop (the core of the project)

- **Concept.** One forward pass gives logits over the vocabulary for the next position. Softmax turns them into probabilities, and a decoding strategy picks one token. Append it and repeat.
- **Build, in this order:**
  1. `next_token_logits(model, input_ids)`, without a cache.
  2. `greedy`, then `apply_temperature`, `top_k_filter` and `top_p_filter` as pure functions on a logits tensor. Then `sample` with a seeded `torch.Generator`.
  3. `generate(strategy, max_new_tokens)` that records the top ten tokens and their probabilities at every step.
  4. Add the KV cache.
  5. Beam search with length normalisation.
- **Tests (written before the code).** On fake logits: top k keeps exactly k, top p keeps the smallest set whose cumulative probability reaches p, temperature near 0 matches greedy, and the same seed gives the same sample. On the real model, your greedy output must match `model.generate(do_sample=False)` token for token.
- **Experiments.**
  - Time 100 tokens with and without the KV cache.
  - Chart entropy per step for greedy, top p 0.9 and temperature 1.2.
  - Find a prompt where greedy loops on the base model.
  - Compare your top ten probabilities with Ollama's `top_logprobs` for the same prompt.
- **Done when** the Decoding page steps through generation one token at a time with a probability bar chart, and all the tests pass.

### Step 4. Chat UI

- **Concept.** Chat models are next token predictors wrapped in a chat template. The system prompt is just more tokens at the front.
- **Build.** Use `st.chat_message`, `st.chat_input` and `st.write_stream` over `ollama.chat(stream=True)`. Add a model picker, sliders for temperature, top p, top k and max tokens, a seed field and a system prompt box. Put thinking output in a collapsible block for reasoning models.
- **Experiment.** Send one prompt under three system prompts and watch `prompt_eval_count` change. That is the cost of the system prompt on every turn.
- **Done when** streaming works and the sliders visibly change answers.

### Step 5. Side by side comparison

- **Concept.** Latency has two parts: prompt processing (prefill) and generation (decode). Each scales differently.
- **Build.** Run one prompt on two to four models. Show the answers in columns with time to first token, tokens per second, prompt tokens and output tokens.
- **Experiment.** Run the models one after another and then concurrently. On one Mac they compete for memory bandwidth, so measure how much concurrent runs distort tokens per second. Also count thinking tokens separately for the reasoning model.
- **Done when** the page shows the metrics and the README explains the sequential vs concurrent result.

### Step 6. Eval harness

- **Concept.** One sample tells you nothing about a sampling setting. You need many prompts, several seeds and a fixed scorer.
- **Build.**
  - About 25 prompts across three kinds: exact answers (arithmetic, facts), format following (JSON, word limits, checked by rules) and open ended (judged).
  - SQLite tables `runs` (model, settings, seed, timestamp) and `results` (prompt, output, score, latency, tokens).
  - A grid runner and an Evals page with charts.
- **Judge.** Start with the largest local model. A hosted model can come later through `.env`. Before you trust it, label 10 outputs yourself and measure how often the judge agrees with you. Watch for verbosity and position bias.
- **Experiment.** Run temperature {0, 0.7, 1.2} × top p {0.9, 1.0} × 3 seeds. Plot mean score and spread per setting. That is about 25 × 4 × 6 × 3 = 1,800 calls, so run it overnight or trim the grid.
- **Done when** a chart shows accuracy and variance against temperature. This is the project's "done when" in the README.

### Step 7. Base vs instruct

- **Concept.** Pretraining teaches the model to continue text. SFT and RLHF teach it to follow instructions and stop.
- **Build.** Same prompts on Qwen2.5 0.5B base and instruct, with and without the chat template. That gives four combinations.
- **Experiment.** Score all four with the step 6 harness. Also try few shot prompts on the base model to see how much of the gap they close.
- **Done when** the README has the four combination table and one sample output for each.

### Step 8. Stretch: small supervised fine tune

- **Concept.** SFT is next token training on (prompt, answer) pairs, with the loss counted only on the answer.
- **Build.** Run TRL `SFTTrainer` on Qwen2.5 0.5B base with a few hundred examples on MPS. A full fine tune fits in 32 GB, and LoRA through `peft` is lighter. Add the result to the Decoding and Base vs Instruct pickers.
- **Experiment.** Score the result with the eval harness against base and the official instruct model.
- **Done when** your fine tune has a row in the comparison table.

## Pitfalls to expect

- Compute softmax in float32. On MPS, float16 can produce NaN probabilities.
- Streamlit reruns the whole script on every interaction, so cache models with `st.cache_resource`.
- Ollama keeps models loaded (`keep_alive`). Warm a model up before you time it, and unload it between timing runs if memory gets tight.
- Instruct models need `tokenizer.apply_chat_template`. Base models get raw text.
- For reproducibility, use `options.seed` in Ollama and `torch.Generator` in your loop.
- When you think a sampling setting made things better, check the variance across seeds before you believe it.

## Rough schedule (evenings)

| Session | Work |
|---|---|
| 1 | Steps 0 and 1 |
| 2 | Step 2 |
| 3 and 4 | Step 3 (the longest step, don't rush it) |
| 5 | Steps 4 and 5 |
| 6 | Step 6 |
| 7 | Step 7, README findings, blog post notes |
| Later | Step 8 |

## Questions the Findings section should answer

1. Which tokenizer is cheapest for English, for Portuguese and for code, and by how much?
2. How much faster is decoding with a KV cache?
3. How do accuracy and variance change from temperature 0 to 1.2?
4. Why does top p 0.9 with temperature 1.2 differ from greedy? Answer with entropy charts and eval scores.
5. How far apart are base and instruct, and how much does few shot prompting close the gap?
6. How much latency do thinking tokens add on the reasoning model?

## Sources

- [Ollama chat API](https://docs.ollama.com/api/chat): logprobs, options and timing fields
- [Ollama Python logprobs example](https://sources.debian.org/src/ollama-python/0.6.1-1/examples/chat-logprobs.py)
- [transformers v5 release notes](https://releases.sh/hugging-face/transformers-releases) and a [v5 cache discussion](https://huggingface.co/transformers-community/group-beam-search/discussions/4)
- [Qwen3 0.6B Base model card](https://huggingface.co/Qwen/Qwen3-0.6B-Base)
- [Ollama model library](https://registry.ollama.ai/library)
