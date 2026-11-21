---
title: "Decode is a memory problem"
series: "Inside the LLM Playground"
part: 2
date: 2026-11-21
description: "Benchmarking four local models through Ollama on an M2 Pro: why decode speed follows model size, why prefill is only 10 to 12 times faster, and what thinking tokens really cost."
tags: [llm, ai-infrastructure, inference, ollama, benchmarking, learning-in-public]
demo: https://claude.ai/artifact/C3tmEfxasHsveeyUkNhiue
---

# Decode is a memory problem

*Part 2 of Inside the LLM Playground, a series on what I learned building a small LLM lab on my laptop as I move towards AI infrastructure engineering.*

> **Try it as you read.** The "Local models" station of the [LLM Engineering Flight Deck](https://claude.ai/artifact/C3tmEfxasHsveeyUkNhiue) races the four models from this post at the speeds I measured, and it has a bandwidth chart that predicts how fast they would run on other chips.

## The setup

After looking inside one tiny model in part 1, I wanted to see how real models behave when they are served the way most people run them locally. I used Ollama, which runs a small server on port 11434 and treats the command line as just another client. I pulled four models from four different makers, about 12.6 GB in total:

| Model | Maker | Download |
|---|---|---|
| llama3.2:3b | Meta | 2.0 GB |
| qwen3:4b | Alibaba | 2.5 GB |
| gemma3:4b | Google | 3.4 GB (including an 851 MB vision encoder) |
| deepseek-r1:7b | DeepSeek | 4.7 GB |

Then I wrote a benchmark script that measures every model in the same way. It records a cold load and a warm load, prefill on a prompt of roughly 1,430 tokens, and decode over a fixed 200 tokens at temperature 0, taking the median of three runs.

| Model | Cold load | Warm load | Prefill | Decode |
|---|---|---|---|---|
| llama3.2:3b | 2.85 s | 1 ms | 751 tok/s | 66.3 tok/s |
| qwen3:4b | 2.42 s | 2 ms | 563 tok/s | 53.8 tok/s |
| gemma3:4b | 2.47 s | 1 ms | 637 tok/s | 53.9 tok/s |
| deepseek-r1:7b | 3.51 s | 1 ms | 343 tok/s | 33.4 tok/s |

## Decode speed is set by memory bandwidth

Decode is the part where the model writes its reply one token at a time. To produce each token it has to read every weight in the model, and a 2 GB model therefore moves about 2 GB of memory for every single token. If that is the bottleneck, then multiplying the size of the weights by the tokens per second should give a figure close to the chip's memory bandwidth. I checked it with the speeds from my first runs:

| Model | GB read per token | Tokens per second | GB/s moved |
|---|---|---|---|
| llama3.2:3b | 2.0 | 72.9 | 146 |
| gemma3:4b | about 2.5 (text weights only) | 54.7 | 137 |
| qwen3:4b | 2.5 | 52.7 | 132 |
| deepseek-r1:7b | 4.7 | 34.1 | 160 |

All four land between 130 and 160 GB/s, which is 65 to 80% of the M2 Pro's roughly 200 GB/s. Gemma is a nice confirmation, because it downloads at 3.4 GB but decodes like a 2.5 GB model, and that is exactly what you would expect when the vision weights are never touched while writing text.

This was the moment the project stopped feeling like a toy for me. Once you know decode is bound by memory bandwidth, you can predict the speed of a model on hardware you have never touched, simply by dividing the bandwidth by the size of the weights. It also explains why quantisation matters so much in practice, since smaller weights mean fewer bytes to read for every token.

## Prefill is limited by arithmetic

Before the benchmark I predicted that prefill, the step where the model reads the whole prompt, would be "50+ times" faster than decode. I was wrong by a wide margin:

| Model | Prefill divided by decode |
|---|---|
| llama3.2:3b | 11.3x |
| qwen3:4b | 10.5x |
| gemma3:4b | 11.8x |
| deepseek-r1:7b | 10.3x |

Prefill reads the weights once for the whole prompt, so memory is not its limit. Its limit is the arithmetic, at roughly two operations per parameter per token. When I multiplied parameters by two and by the prefill rate, every model came out between 4.5 and 5.2 trillion operations per second, which looks like a steady ceiling for this GPU. A laptop GPU has much less compute relative to its memory speed than a data centre GPU, where the gap between prefill and decode is far larger. So "prefill is very fast" turns out to be a statement about the hardware rather than a law of nature, and that is the kind of nuance I want to be able to explain in an interview.

## Thinking tokens decide the total time

For a simpler test I sent the same question to all four models: "Explain what a token is in two sentences."

| Model | Reply tokens | Decode speed | Total time |
|---|---|---|---|
| llama3.2:3b | 76 | 72.9 tok/s | 4.1 s |
| gemma3:4b | 56 | 54.7 tok/s | 3.6 s |
| qwen3:4b | 1,145 | 52.7 tok/s | 24.8 s |
| deepseek-r1:7b | 601 | 34.1 tok/s | 21.5 s |

Qwen3 and Gemma decode at almost the same speed, yet Qwen3 took seven times as long, because it wrote 1,145 tokens of reasoning where Gemma wrote 56. DeepSeek is slower per token but wrote about half as many tokens as Qwen3, so it still finished first of the two. With short prompts like this one, the time to answer is mostly reply tokens divided by decode speed, which makes the length of the thinking the number that matters most.

I also tried to switch Qwen3's thinking off with `--think=false`. It still wrote 928 tokens of reasoning, and the reasoning leaked into the visible answer with a stray `</think>` near the end. The server log explained why, since the tag actually resolves to "Qwen3 4B Thinking 2507", a version trained to always reason. A flag can ask for a behaviour, but the weights decide whether you get it.

One more detail amused me. None of the four models explained an LLM token. Llama and Gemma talked about crypto tokens, Qwen3 about compiler tokens and DeepSeek about operating system tokens. Without context, each model went with the meaning that was most common in its training data, and the LLM sense of the word is still recent and rare.

## Cold, warm and noisy

Loading a model from disk took between 2.4 and 3.5 seconds, while a warm load took 1 to 2 ms, which is more than a thousand times faster. Ollama keeps a model in memory for five minutes after its last use, and that is why a local chat app feels slow on the first message and quick afterwards. On a warm run Ollama also reused its cache for 30 of the 31 prompt tokens. The last token is always recomputed, because its output is the prediction for the next one.

The benchmark also taught me about noise. Llama decoded at 72.9 tok/s in my first runs but 66.3 in the full benchmark, so I reran it on its own and got 71.1. Prefill barely moved, by about 1%, while decode moved by 7%. That fits the story, because decode depends on memory bandwidth, and on a Mac under memory pressure other apps compete for it. A median of three smooths out noise inside one session, but not between sessions, so I now treat any difference under about 10% between two sessions as noise rather than a finding.

## What I took away

- Decode is bound by memory bandwidth, so model size predicts speed, and bandwidth divided by weight size is a useful first estimate on any chip.
- Prefill is bound by compute, and the gap between prefill and decode depends heavily on the hardware.
- For reasoning models the number of tokens they choose to write matters more than how fast they write them.
- Warm starts and cached prompts make a huge difference to latency, and noise between sessions is larger than it looks.

## Next in the series

Speed was only half the story. In part 3 I look at where the memory actually goes, and why a 2 GB model ended up using 6 GB.

*The benchmark script is `scripts/bench_ollama.py` in [ai-engineering-lab](https://github.com/udujoel/ai-engineering-lab), and the full numbers are in `01-llm-playground/LAB_NOTES.md`.*
