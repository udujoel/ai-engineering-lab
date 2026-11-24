---
title: "A model outputs odds, not words"
series: "Inside the LLM Playground"
part: 1
date: 2026-11-21
description: "The first look inside a language model: one forward pass, 151,936 scores, and why Paris only wins with 31.6%."
tags: [llm, ai-infrastructure, pytorch, apple-silicon, learning-in-public]
demo: https://www.joeludu.com/demos/llm-flight-deck.html#inside
---

# A model outputs odds, not words

*Part 1 of Inside the LLM Playground, a series on what I learned building a small LLM lab on my laptop as I move towards AI infrastructure engineering.*

> **Try it as you read.** Everything in this series is also in an interactive demo, the [LLM Engineering Flight Deck](https://www.joeludu.com/demos/llm-flight-deck.html#inside). This post goes with its first station, "Inside a model", where you can watch the forward pass climb the layers and see the real top five guesses from my run.

## Why I started here

Most of us meet language models through a chat box, where a question goes in and a paragraph comes out. I wanted to see the machinery in between, because the jobs I am aiming for are about running that machinery well: making it fast, fitting it into memory and knowing where the time goes. So the first project in my lab is an LLM playground, and its very first step was simply to load a small model and look at what it actually produces.

The setup was deliberately modest. I used a MacBook Pro with an M2 Pro chip and 32 GB of unified memory, Python 3.12 managed by uv, and Hugging Face transformers. The model was Qwen2.5 0.5B, the base version rather than the chat one, running on the Mac's GPU through PyTorch's `mps` device.

## One prompt, one forward pass

I gave the model five words, "The capital of France is", and asked it for a single forward pass. The tokenizer first turned the text into five tokens and their IDs:

| Token | ID |
|---|---|
| `The` | 785 |
| `·capital` | 6722 |
| `·of` | 315 |
| `·France` | 9625 |
| `·is` | 374 |

The `·` marks a space, and it is the first small surprise. The space belongs to the word that follows it, so " Paris" and "Paris" are two different tokens with two different IDs. That detail comes back again and again later in the project.

What came out of the model was not a word. It was a tensor with the shape `(1, 5, 151936)`, which means one score for every slot in the vocabulary, at every one of the five positions. Those scores are called logits, and a softmax turns them into probabilities. Only the last position matters for the next word, so I took its scores, ran the softmax and sorted them.

| Next token | Probability |
|---|---|
| `·Paris` | 31.6% |
| `·______` | 11.5% |
| `·____` | 6.4% |
| `·__` | 5.5% |
| `:\n` | 5.1% |

## What surprised me

**The model never chooses a word.** It hands back odds for all 151,936 slots (the tokenizer uses 151,665 of them, and the rest is padding that never wins), and something outside the model has to pick one. That picking step is called decoding, and it is a design decision rather than a property of the model. Greedy decoding takes the top entry, while sampling with a temperature rolls a weighted die. I will build that part by hand later in the series, but it changed how I think about every chat reply I have ever read. Each word was a choice made from a list of odds.

**The right answer only got 31.6%.** I expected Paris to be close to certain. Instead, most of the remaining probability went to runs of underscores. A base model has been trained on a huge amount of ordinary web text, and that includes a lot of quizzes and worksheets where "The capital of France is ____" is exactly what comes next. The model was not wrong about the world. It was right about its training data, which is a different thing, and it is the reason chat models go through a second round of training before anyone talks to them.

## The timing lesson I nearly missed

My first run timed the forward pass at 774 ms. Later, two automated code reviewers on my pull request pointed out that the timer in my script stopped as soon as the model call returned. On Apple's GPU, PyTorch queues the work and returns before the GPU has actually finished, so a timer like that can measure how fast the work was queued instead of how fast it ran. The fix is to call `torch.mps.synchronize()` before starting and before stopping the clock.

When I reran the script with the synced timer, the forward pass took **212 ms**, with the same tokens, the same IDs and the same top five. That drop puzzled me at first, because waiting for the GPU can only add time and never remove it. So the sync was not what made it faster. The likely explanation is first run overhead, since the first time a model runs on `mps` the GPU kernels get compiled and memory gets set up. I suspect my 774 ms was mostly warm up, though I have not proved it yet, and loading also fell from 31.3 s to 4.9 s once the weights were already on disk.

I only have one run of each, so I treat both numbers as rough. The lesson is not rough at all, though. Asynchronous GPU timing catches people out all the time, and in AI infrastructure work a benchmark that measures the wrong thing is worse than no benchmark, because people make decisions from it. Every GPU timing now gets a synchronize on both sides and a warm up run before the one that counts.

## What I took away

- A language model outputs a score for every token in its vocabulary, and decoding is a separate choice made on top of those scores.
- A base model reflects its training text, which is why the most likely continuation is not always the most useful one.
- Spaces live inside tokens, which makes token counts and IDs less intuitive than they first look.
- On a GPU, a timing only means something if you wait for the device and throw away the first run.

## Next in the series

In part 2 I move from one tiny model in Python to four real models served locally through Ollama, and the numbers turn into an infrastructure story about memory bandwidth, compute and why a laptop GPU behaves the way it does.

*The code and full lab notes are in [ai-engineering-lab](https://github.com/udujoel/ai-engineering-lab), under `01-llm-playground/`.*
