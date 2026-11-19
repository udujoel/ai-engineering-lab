# Lab notes: Project 1, LLM Playground

A running record of what I ran, the numbers I got and what surprised me. Raw material for blog posts.

Machine: MacBook Pro, Apple M2 Pro, 32 GB unified memory (about 200 GB/s memory bandwidth). Ollama 0.40.16. Python 3.12 with uv.

---

## Step 0: first look inside a model (2026-11-16)

**What I did:** loaded Qwen2.5 0.5B (the base model, not the chat one) on the Mac GPU (`mps`) with Hugging Face transformers and ran one forward pass on "The capital of France is".

| Measure | Value |
|---|---|
| Device | mps (Apple GPU) |
| Load time, first run (includes download) | 31.3 s |
| Prompt tokens | `['The', ' capital', ' of', ' France', ' is']` |
| Token IDs | `[785, 6722, 315, 9625, 374]` |
| One forward pass | 774 ms |
| Output shape (logits) | (1, 5, 151936): one score per vocabulary entry, at every position |

Top 5 guesses for the next token:

| Token | Probability |
|---|---|
| ` Paris` | 31.6% |
| ` ______` | 11.5% |
| ` ____` | 6.4% |
| ` __` | 5.5% |
| `:\n` | 5.1% |

**Observations**
- A model never outputs a word. It outputs a probability for every one of 151,936 tokens, and something else picks one.
- Paris wins with only 31.6%. Most of the rest is fill in the blank underscores: a base model has read a lot of quizzes and worksheets, so "The capital of France is ____" is a very common pattern in its training text.
- Words start with a space inside the token (`' Paris'`), so " Paris" and "Paris" are different tokens.

---

## Step 1: four local models through Ollama (2026-11-17)

### Part A: downloads

| Model | Maker | Download | Notes |
|---|---|---|---|
| llama3.2:3b | Meta | 2.0 GB | |
| qwen3:4b | Alibaba | 2.5 GB | Turned out to be "Qwen3 4B Thinking 2507" |
| gemma3:4b | Google | 3.4 GB | Includes an 851 MB vision encoder |
| deepseek-r1:7b | DeepSeek | 4.7 GB | Reasoning model, distilled onto Qwen 7B |

Total 12.6 GB. Download speed about 63 MB/s. Ollama stores each file under its SHA-256 hash, and the CLI is just a client talking to a local server on port 11434.

### Part B: same prompt, four models

Prompt: "Explain what a token is in two sentences." Run with `ollama run <model> --verbose`.

| Model | Load (cold) | Prompt tokens | Reply tokens | Decode speed | Total time |
|---|---|---|---|---|---|
| llama3.2:3b | 2.84 s | 35 | 76 | 72.9 tok/s | 4.1 s |
| gemma3:4b | 2.27 s | 19 | 56 | 54.7 tok/s | 3.6 s |
| qwen3:4b | 2.95 s | 20 | 1,145 | 52.7 tok/s | 24.8 s |
| qwen3:4b, `--think=false` | 2.63 s | 20 | 928 | 52.1 tok/s | 20.5 s |
| deepseek-r1:7b | 3.67 s | 13 | 601 | 34.1 tok/s | 21.5 s |

**Finding 1: decode speed is set by model size, because every token reads all the weights.**

| Model | GB read per token | x tok/s | = GB/s moved |
|---|---|---|---|
| llama3.2:3b | 2.0 | 72.9 | 146 |
| gemma3:4b | about 2.5 (text weights only) | 54.7 | 137 |
| qwen3:4b | 2.5 | 52.7 | 132 |
| deepseek-r1:7b | 4.7 | 34.1 | 160 |

All four land at 65 to 80% of the chip's 200 GB/s. Gemma downloads at 3.4 GB but decodes like a 2.5 GB model, because the vision part is not touched when writing text.

**Finding 2: thinking tokens decide the total time.** Qwen3 and Gemma decode at the same speed, but Qwen3 wrote 1,145 tokens against Gemma's 56 and took 7 times as long. Deepseek is slower per token but wrote half as many tokens as Qwen3, so it finished first of the two. Time to answer = load + reply tokens / decode speed.

**Finding 3: `--think=false` did not stop Qwen3 from thinking.** The server log names the model "Qwen3 4B Thinking 2507", a model trained to always reason. Ollama switched thinking off in the template, the model reasoned anyway, and the reasoning leaked into the visible answer (a lone `</think>` near the end). It saved only 217 tokens. A flag can ask for a behaviour; the weights decide.

**Finding 4: most of the memory is the KV cache, not the model.** `ollama ps` showed 6.0 GB for a 2.0 GB model. Ollama reserves a KV cache for the full 32,768 token context up front. Figures from the server log:

| Model | Download | KV cache | In memory |
|---|---|---|---|
| llama3.2:3b | 2.0 GB | 3.5 GiB | 6.0 GB |
| qwen3:4b | 2.5 GB | 4.5 GiB | about 7.0 GB |
| deepseek-r1:7b | 4.7 GB | 1.75 GiB | 6.0 GB |

KV cache = 2 (keys and values) x layers x KV heads x 128 x 2 bytes x 32,768 positions. Qwen3 has 36 layers x 8 KV heads, deepseek 28 x 4, so the smaller model carries 2.6 times the cache.

**Finding 5: only one model fits at a time on this Mac right now.** After all four runs, `ollama ps` listed only deepseek. The server log said: `model predicted to exceed available memory, evicting ... system_free="4.4 GiB"`. The limit was free system RAM, not the GPU budget, because the Mac shares one pool of memory between apps and GPU.

**Finding 6: same question, four different meanings of "token".** Llama and Gemma explained crypto tokens, Qwen3 compiler tokens, and DeepSeek operating system tokens (inventing a "printer token" along the way). None explained LLM tokens. My reading: the prompt gave no context, so each model went with the meaning most common in its training data. The LLM sense of the word is recent and rare in that data.

**Other notes**
- The same 8 word question became 13 to 35 prompt tokens. Each model wraps it in its own hidden chat template; Llama's adds a system header with a knowledge cutoff date.
- Prompt eval rates from short prompts are noise (55 to 512 tok/s for similar prompts). Prefill needs a long prompt to measure.
- Each model ships its own default sampling settings (seen in the log): deepseek temperature 0.8, top_k 40; qwen3 temperature 0.6, top_k 20, top_p 0.95.

### Part C: cold vs warm, prompt cache, RAM

Same command twice: `ollama run llama3.2:3b --verbose "Say hello in five words."`

| | Run 1 (cold) | Run 2 (warm) |
|---|---|---|
| Load duration | 2,590 ms | 0.9 ms |
| Prompt tokens computed | 31 | 1 (30 cached) |
| Decode speed | 74.6 tok/s | 70.2 tok/s |
| Total | 2,776 ms | 138 ms |
| Reply | "Hello, I'm here to help." | "Hello from the digital realm." |

- Warm is 20 times faster overall. The 5 minute keep alive is why a chat app is slow on the first message and fast after.
- Ollama reused the KV cache from run 1 for 30 of 31 prompt tokens. The last token is always recomputed, because its output is the prediction for the next token.
- The prompt eval rate of 28.67 tok/s is 1 token / 34.9 ms: correct maths, meaningless number.
- Same prompt, different reply: sampling is random at temperature above 0 (Step 3).

RAM check (`top -l 1 -s 0 | grep PhysMem`): 31 GB used, 9.8 GB wired, 7.3 GB compressed, 70 MB unused. The compressor figure shows the Mac is under memory pressure.

### Decisions

- **Keep qwen3:4b as the always thinking model.** It decodes at the same speed as Gemma, so the time difference between them is the cost of reasoning.
- **Keep the 32k context (one model loaded at a time).** Close other apps when I need more room, rather than shrinking the context.

### Part D: benchmark script

`scripts/bench_ollama.py` measures every model the same way: cold and warm load, prefill on a 1,500 token prompt, decode over a fixed 200 tokens at temperature 0 (median of 3), and memory from `ollama ps`.

Tests first: `uv run pytest -m "not slow"` gave 7 passed, 1 deselected.

My predictions before running:
1. Prefill would be "50+ times" faster than decode.
2. Qwen3 would use the most memory: model plus KV cache, about 7 GB, 36 layers.

Results (`uv run python scripts/bench_ollama.py`):

| Model | Cold load | Warm load | Prefill | Decode | Memory |
|---|---|---|---|---|---|
| llama3.2:3b | 2.85 s | 1 ms | 751 tok/s (1,443 tok) | 66.3 tok/s (200 tok) | 5.6 GiB at 32k context |
| qwen3:4b | 2.42 s | 2 ms | 563 tok/s (1,433 tok) | 53.8 tok/s (200 tok) | 7.0 GiB at 32k context |
| gemma3:4b | 2.47 s | 1 ms | 637 tok/s (1,411 tok) | 53.9 tok/s (200 tok) | 2.8 GiB at 32k context |
| deepseek-r1:7b | 3.51 s | 1 ms | 343 tok/s (1,425 tok) | 33.4 tok/s (200 tok) | 5.7 GiB at 32k context |

**Prediction 1 was too high: prefill is only 10 to 12 times faster than decode.**

| Model | Prefill / decode |
|---|---|
| llama3.2:3b | 11.3x |
| qwen3:4b | 10.5x |
| gemma3:4b | 11.8x |
| deepseek-r1:7b | 10.3x |

Prefill and decode hit different limits. Decode reads all the weights for every token, so memory bandwidth limits it. Prefill reads the weights once for the whole prompt, so the limit is arithmetic: about 2 x parameters operations per token. Parameters x 2 x prefill rate gives about 4.5 to 5.2 trillion operations per second for every model, a steady ceiling for this GPU. A laptop GPU has much less arithmetic power relative to its memory speed than a data centre GPU, where the gap between prefill and decode is far larger. So "prefill is very fast" depends on the hardware.

**Prediction 2 was right: Qwen3 uses the most memory (7.0 GiB).** Its 36 layers x 8 KV heads give the biggest KV cache (4.5 GiB).

**Surprise: Gemma uses only 2.8 GiB, the least of all four, despite the biggest download.** The server log shows why. Gemma 3 uses sliding window attention: 29 of its 34 layers only look at the most recent 1,024 tokens, so their cache holds 1,536 positions instead of 32,768. Only 5 layers keep the full context.

| Gemma KV cache | Layers | Positions | Size |
|---|---|---|---|
| Full attention | 5 | 32,768 | 640 MiB |
| Sliding window | 29 | 1,536 | 174 MiB |
| Total | | | 814 MiB, about a fifth of Qwen3's |

The trade off showed up in the log too: `forcing full prompt re-processing due to lack of cache data (likely due to SWA ...)`. Gemma could not reuse its prompt cache between requests, so it rereads the whole conversation every turn.

**Other notes**
- Warm load is 1 to 2 ms against 2.4 to 3.5 s cold, more than 1,000 times faster.
- Decode matches Part B within 2% for Qwen3, Gemma and deepseek. Llama dropped from 72.9 to 66.3 tok/s (9%), so I reran Llama alone (`uv run python scripts/bench_ollama.py llama3.2:3b`):

| Llama run | Cold load | Warm load | Prefill | Decode |
|---|---|---|---|---|
| Part B (`ollama run`) | 2.84 s | | | 72.9 tok/s |
| Full benchmark | 2.85 s | 1 ms | 751 tok/s | 66.3 tok/s |
| Rerun alone | 2.39 s | 7 ms | 758 tok/s | 71.1 tok/s |

  Back within 2.5% of Part B, so the 66.3 was a slow session, not a property of the model. Prefill barely moved (1%), decode moved 7%. Decode depends on memory bandwidth, which other apps compete for on a Mac under memory pressure. Lesson: a median of 3 runs smooths noise inside one session, not between sessions. Differences under about 10% between two sessions are not a finding.
- Units: my script reports GiB (1,024^3 bytes), `ollama ps` reports GB (1,000^3). Llama's 5.6 GiB is the same as the 6.0 GB `ollama ps` showed in Part B.
- Same caveat for "cold": the model files were probably still in the macOS file cache. A load right after a reboot would be slower.

---

## Step 2: tokenizer explorer (2026-11-18)

### Part A: six tokenizers, one sentence

`scripts/tokenize_text.py` shows how each tokenizer splits a text into pieces and IDs. Qwen2.5 is the Step 0 model's tokenizer. The other five are new: GPT-2, SmolLM2 and Phi-4 mini from Hugging Face (tokenizer files only, a few MB each), and OpenAI's GPT-4 (`cl100k_base`) and GPT-4o (`o200k_base`) through tiktoken. Tests first: `uv run pytest tests/test_tokenizers.py` gave 7 passed.

My predictions before running:
1. "A token is a piece of text that a model works with. It converts this to a number before using it." Qwen would make the 8 word sentence 8 tokens.
2. `1234567` would likely stay as one token, and the six tokenizers might not all do the same.

Results for "Explain what a token is in two sentences." (41 characters, 8 words). `·` is a space:

| Tokenizer | Vocabulary | Tokens | How "Explain" splits |
|---|---|---|---|
| gpt2 | 50,257 | 10 | `Expl` `ain` |
| qwen2.5 | 151,665 | 10 | `Ex` `plain` |
| smollm2 | 49,152 | 9 | `Explain` |
| phi-4-mini | 200,029 | 9 | `Explain` |
| gpt-4 | 100,277 | 10 | `Ex` `plain` |
| gpt-4o | 200,019 | 9 | `Explain` |

The rest is the same for all six: `·what | ·a | ·token | ·is | ·in | ·two | ·sentences | .`

**Prediction 1 was close: 9 to 10 tokens, not 8.** The full stop is a token of its own, and "Explain" splits in two for half the tokenizers. Common English words are one token each in every vocabulary.

**The space belongs to the next word.** Every word after the first is stored as `·what`, `·token`: a space plus the word. So "token" at the start of a sentence and " token" in the middle are different tokens with different IDs (the same thing as `' Paris'` in Step 0).

**Phi-4 mini and GPT-4o produced identical IDs** (`[176289, 1412, 261, ...]`). Microsoft built Phi-4 mini on OpenAI's o200k vocabulary. The 10 extra entries (200,029 vs 200,019) are presumably Phi's own special tokens.

**Qwen2.5 and GPT-4 split the sentence the same way, and many IDs match exactly** (` a` 264, ` is` 374, ` in` 304, `.` 13). Qwen's vocabulary looks like it was built on top of GPT-4's cl100k. Not yet confirmed from a source.

**A bigger vocabulary did not mean fewer tokens here.** SmolLM2 (49k) used 9, the same as the 200k vocabularies. For plain English all of them are near one token per word. Where they should differ is other languages, code and numbers (Part B).

**Back to Step 1:** the bare sentence is 9 to 10 tokens, but Ollama counted 13 to 35. The difference is each model's hidden chat template. Llama's 35 means about 25 tokens of wrapping (its system header with a knowledge cutoff date). Part B will measure this per model.

#### Numbers and emoji

`uv run python scripts/tokenize_text.py "The price is 1234567 dollars 🙂"` (30 characters, 6 words):

| Tokenizer | Tokens | How `1234567` splits | Rule |
|---|---|---|---|
| gpt2 | 8 | `·123` `45` `67` | No rule: whatever chunks happened to be common in its training text, space included |
| qwen2.5 | 13 | `1` `2` `3` `4` `5` `6` `7` | One token per digit |
| smollm2 | 13 | `1` `2` `3` `4` `5` `6` `7` | One token per digit |
| phi-4-mini | 9 | `123` `456` `7` | Groups of up to 3 digits, counted from the left |
| gpt-4 | 9 | `123` `456` `7` | Groups of up to 3 digits, counted from the left |
| gpt-4o | 9 | `123` `456` `7` | Groups of up to 3 digits, counted from the left |

**Prediction 2 was half right.** The number did not stay one token in any tokenizer, but the tokenizers did not all agree: there are three different strategies. "GPT-4, GPT-4o and Phi did the same on the number."

- The digit-by-digit tokenizers spend 7 tokens on the number. Price or context cost aside, that is the most expensive.
- In five of the six, the space before the number is a token of its own (`·`). Only GPT-2 glues it to the digits (`·123`).
- The emoji was not split: ` 🙂` is one token in all six, so no `▯` appeared. Common emoji have their own token.

**Which split makes arithmetic easiest?** My first guess: "gpt2 might make arithmetic easier but not sure on this one".

#### Testing the arithmetic question

My predictions before running:
1. Will GPT-2 split different 7 digit numbers the same way? "I'd lean towards no for gpt2. Don't think it'll be consistent."
2. For which strategy is the last token always just the units digit? "the gpt-4x and phi"

`uv run python scripts/tokenize_text.py "1234567 2345678 1000000 9876543 👍🏽"`:

| Tokenizer | 1234567 | 2345678 | 1000000 | 9876543 | Total tokens |
|---|---|---|---|---|---|
| gpt2 | `123` `45` `67` | `·23` `45` `678` | `·100` `0000` | `·9` `87` `65` `43` | 17 |
| qwen2.5, smollm2 | 7 single digits | 7 single digits | 7 single digits | 7 single digits | 34, 37 |
| phi-4-mini, gpt-4, gpt-4o | `123` `456` `7` | `234` `567` `8` | `100` `000` `0` | `987` `654` `3` | 18, 20, 18 |

**Prediction 1 was right.** GPT-2 split four 7 digit numbers four different ways (3-2-2, 2-2-3, 3-4, 1-2-2-2). Worse, the same token means different things: `45` is the thousands and hundreds digits in 1234567, but the ten thousands and thousands digits in 2345678. To add two numbers the model must line up place values, and GPT-2's tokens hide them.

**Prediction 2 was right for these numbers, but only by coincidence.** A 7 digit number groups as 3 + 3 + 1, so the last group happens to be the units digit alone. A 6 digit number like 123456 groups as `123` `456`, and the units digit is buried in a 3 digit token. Left grouping has a second problem: `123` means millions in 1234567 but thousands in 123456, so the model has to know the length of the number to read any group. Only one token per digit (Qwen2.5, SmolLM2) always keeps the units digit on its own.

The trade off is cost: one token per digit spent 28 tokens on 28 digits, against 15 for 3 digit groups.

**The emoji did split.** 👍🏽 is two characters (thumbs up plus a skin tone modifier), 8 bytes in all, and took 3 to 6 tokens with the space: 3 for Qwen2.5, Phi-4 mini and GPT-4o, 5 for GPT-2 and GPT-4, 6 for SmolLM2. Emoji with modifiers are expensive.

**Bug found in my explorer:** Phi-4 mini and GPT-4o gave identical IDs for the emoji but displayed the pieces differently. Fixed, see mistake 11 in `docs/mistakes-log.md`. The counts and IDs above were correct; only the placement of `▯` differed.
