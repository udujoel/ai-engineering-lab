---
title: "Where the memory goes: the KV cache"
series: "Inside the LLM Playground"
part: 3
date: 2026-11-21
description: "Why a 2 GB model used 6 GB of memory, how to calculate the KV cache, and how Gemma's sliding window attention shrank its cache to a fifth of Qwen3's."
tags: [llm, ai-infrastructure, kv-cache, memory, ollama, learning-in-public]
demo: https://claude.ai/artifact/C3tmEfxasHsveeyUkNhiue
---

# Where the memory goes: the KV cache

*Part 3 of Inside the LLM Playground, a series on what I learned building a small LLM lab on my laptop as I move towards AI infrastructure engineering.*

> **Try it as you read.** The "Local models" station of the [LLM Engineering Flight Deck](https://claude.ai/artifact/C3tmEfxasHsveeyUkNhiue) has a KV cache slider. Drag the context length and watch each model's cache grow, then see how Gemma's sliding window changes the curve. At 32k it matches the figures from my server log.

## A 2 GB model using 6 GB

After running Llama 3.2 3B, I checked `ollama ps` and saw it holding 6.0 GB of memory, even though the model file is only 2.0 GB. My first thought was that something had gone wrong. It had not. Ollama reserves a key value cache, the KV cache, for the full context window up front, and I was running with a 32,768 token context.

The cache exists because of how attention works. Every new token looks back at every earlier token, and to do that it needs a key and a value vector for each of them, in every layer. Recomputing those for the whole conversation on every step would be far too slow, so the model stores them instead. The cost is memory, and it grows with the context length.

## The formula

The size of the cache can be worked out from a few numbers in the model's configuration:

```
KV cache = 2 (keys and values) x layers x KV heads x head dimension x 2 bytes x positions
```

For Llama 3.2 3B that is 2 x 28 layers x 8 KV heads x 128 x 2 bytes x 32,768 positions, which comes to 3.5 GiB, exactly what the server log reported. Here is how the three models with a plain full attention cache compare:

| Model | Download | KV cache at 32k | In memory |
|---|---|---|---|
| llama3.2:3b | 2.0 GB | 3.5 GiB | 6.0 GB |
| qwen3:4b | 2.5 GB | 4.5 GiB | about 7.0 GB |
| deepseek-r1:7b | 4.7 GB | 1.75 GiB | 6.0 GB |

The result I find most interesting is DeepSeek. It is the biggest model of the three, yet it carries the smallest cache, because it has 28 layers with only 4 KV heads, while Qwen3 has 36 layers with 8. The smaller model ends up carrying 2.6 times the cache. At a 32k context the cache outweighs the weights for Llama and Qwen3, though not for DeepSeek, and I had to learn to say exactly that rather than claim the cache always dominates.

Before running the benchmark I predicted that Qwen3 would use the most memory, at about 7 GB, because of its 36 layers. That prediction held, and the benchmark measured it at 7.0 GiB.

## Gemma's trick: sliding window attention

The surprise came from Gemma. Its download is bigger than Llama's or Qwen3's, but it used the least memory of all four, only 2.8 GiB at the same 32k context as measured by the benchmark. The server log showed why. Gemma 3 uses sliding window attention, so 29 of its 34 layers only look at the most recent 1,024 tokens, and only 5 layers keep the full context.

| Gemma KV cache | Layers | Positions | Size |
|---|---|---|---|
| Full attention | 5 | 32,768 | 640 MiB |
| Sliding window | 29 | 1,536 | 174 MiB |
| Total | | | 814 MiB, about a fifth of Qwen3's |

That is a real architecture choice showing up as a real memory saving, measured on my own machine, and it is the kind of trade off that decides how many users a server can hold at once. It is not free, though. The same log also contained this line: `forcing full prompt re-processing due to lack of cache data (likely due to SWA ...)`. Because most of Gemma's layers throw old positions away, Ollama could not reuse the prompt cache between requests, so Gemma rereads the whole conversation every turn. You save memory and pay for it in prefill time.

## Only one model fits at a time

After running all four models, `ollama ps` listed only DeepSeek. The server log said `model predicted to exceed available memory, evicting ... system_free="4.4 GiB"`. On a Mac the CPU and GPU share one pool of memory, so the limit was free system RAM rather than a separate GPU budget. A quick check with `top` showed 31 GB used, 7.3 GB compressed and 70 MB unused, which means the Mac was already under pressure from everything else I had open.

That gave me two choices. I could shrink the context window to make the caches smaller, or keep the 32k context and run one model at a time. I chose to keep the context and close other apps when I need room, and I accepted that every model switch costs about three seconds of loading.

## A small lesson about units

While comparing my script with `ollama ps`, the numbers would not line up until I noticed that they use different units. My script reports GiB, which is 1,024³ bytes, while `ollama ps` reports GB, which is 1,000³ bytes. Llama's 5.6 GiB in the benchmark and its 6.0 GB in `ollama ps` are the same amount of memory. It is a tiny thing, but a difference of about 7% is easily big enough to invent a finding that is not real, so every memory figure in my notes now carries its unit.

## What I took away

- Memory for serving a model is weights plus KV cache, and at long contexts the cache can be the larger of the two.
- The cache size follows directly from layers, KV heads, head dimension and context length, so you can calculate it before you run anything.
- Architecture choices such as fewer KV heads or sliding window attention change memory use dramatically, and each one comes with its own cost.
- On unified memory machines the real limit is the free system RAM, which depends on everything else that is running.

## Next in the series

So far I have treated tokens as a given. In part 4 I open up the tokenizers themselves and find that the same meaning can cost very different amounts depending on the language, the tokenizer and even how it splits a number.

*The full Step 1 notes, including the server log figures, are in `01-llm-playground/LAB_NOTES.md` in [ai-engineering-lab](https://github.com/udujoel/ai-engineering-lab).*
