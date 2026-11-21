---
title: "The same meaning has different prices"
series: "Inside the LLM Playground"
part: 4
date: 2026-11-21
description: "Six tokenizers, one paragraph in English and Portuguese: a 24% to 86% language tax, three ways to split a number, and the hidden tokens in every chat template."
tags: [llm, ai-infrastructure, tokenizers, multilingual, cost, learning-in-public]
demo: https://claude.ai/artifact/C3tmEfxasHsveeyUkNhiue
---

# The same meaning has different prices

*Part 4 of Inside the LLM Playground, a series on what I learned building a small LLM lab on my laptop as I move towards AI infrastructure engineering.*

> **Try it as you read.** The "Tokenizers" station of the [LLM Engineering Flight Deck](https://claude.ai/artifact/C3tmEfxasHsveeyUkNhiue) shows all six texts from this post, the Portuguese penalty, the three ways of splitting digits and the hidden chat template costs, all from my measured results.

## Why tokens matter for infrastructure

Every number in the last two posts was counted in tokens. Context windows are measured in tokens, API bills are charged per token, and decode speed is tokens per second. That makes the tokenizer, the piece that turns text into tokens, a quiet factor in cost, latency and how much fits into memory. I wanted to know how much it actually varies, so I compared six tokenizers on the same texts:

| Tokenizer | Vocabulary size | Source |
|---|---|---|
| GPT-2 | 50,257 | Hugging Face |
| Qwen2.5 | 151,665 | Hugging Face (the model from part 1) |
| SmolLM2 | 49,152 | Hugging Face |
| Phi-4 mini | 200,029 | Hugging Face |
| GPT-4 (`cl100k_base`) | 100,277 | tiktoken |
| GPT-4o (`o200k_base`) | 200,019 | tiktoken |

## English is the baseline, not the test

I wrote one fixed set of six texts: an English paragraph, the same paragraph translated into Portuguese, a Python function, a JSON blob, a line of numbers and dates, and a line of emoji. Then I counted tokens with every tokenizer and divided by the number of characters, so that long and short texts compare fairly.

| Tokenizer | English (270 chars) | Portuguese (275) | Python (240) | JSON (157) | Numbers (77) | Emoji (33) |
|---|---|---|---|---|---|---|
| gpt2 | 56 | 104 | 86 | 67 | 31 | 20 |
| qwen2.5 | 56 | 85 | 72 | 73 | 49 | 15 |
| smollm2 | 58 | 104 | 79 | 77 | 49 | 22 |
| phi-4-mini | 55 | 68 | 66 | 65 | 35 | 14 |
| gpt-4 | 56 | 88 | 66 | 65 | 35 | 19 |
| gpt-4o | 55 | 68 | 66 | 65 | 35 | 14 |

English costs almost the same everywhere, between 55 and 58 tokens for the paragraph, or about five characters per token. Every one of these tokenizers was trained mostly on English, so English tells you very little about the differences between them.

## The Portuguese tax

Because the two paragraphs say the same thing, dividing Portuguese tokens by English tokens gives a clean measure of what the language alone costs:

| Tokenizer | Portuguese penalty |
|---|---|
| phi-4-mini | 1.24x |
| gpt-4o | 1.24x |
| qwen2.5 | 1.52x |
| gpt-4 | 1.57x |
| smollm2 | 1.79x |
| gpt2 | 1.86x |

The same meaning costs 24% more with GPT-4o and Phi-4 mini, and 86% more with GPT-2. If you serve Portuguese speakers, that difference shows up directly in your bill, in your latency, since there are more tokens to decode, and in how much conversation fits into the context window.

A single sentence showed me where the waste comes from. "O gato dorme no sofá enquanto chove lá fora." took 12 tokens with the two 200k vocabularies, 14 with Qwen2.5 and GPT-4, 18 with GPT-2 and 19 with SmolLM2. There are two ways a tokenizer wastes tokens on Portuguese. The first is that words get cut into fragments that are common in English, so GPT-2 splits `enquanto` into `enqu` and `anto`. The second is that accented letters break words apart, so in GPT-2 and SmolLM2 the `á` is a token of its own, which makes `sofá` cost three tokens. Only the 200k vocabularies kept `gato` and `sofá` whole. A word only earns its own token if it was common enough in the text the vocabulary was learned from, and the bigger, more multilingual vocabularies had room for Portuguese.

## Three ways to split a number

Numbers turned the ranking upside down. GPT-2 was the cheapest on the numbers line at 31 tokens, while Qwen2.5 and SmolLM2 were the most expensive at 49, because those two give every digit its own token. When I looked closer at how each tokenizer splits `1234567`, I found three completely different strategies:

| Strategy | Tokenizers | How `1234567` splits |
|---|---|---|
| Whatever was common in training | GPT-2 | `123` `45` `67` |
| One token per digit | Qwen2.5, SmolLM2 | `1` `2` `3` `4` `5` `6` `7` |
| Groups of three from the left | GPT-4, GPT-4o, Phi-4 mini | `123` `456` `7` |

I predicted that GPT-2 would not be consistent, and it was not. It split four different seven digit numbers in four different ways. Worse, the same token can mean different things, since `45` stands for different place values in 1234567 and 2345678. To add two numbers a model has to line up the place values, and GPT-2's tokens hide them. Grouping by three has a subtler problem, because `123` means millions in 1234567 but thousands in 123456, so the model needs the length of the number to read any group. One token per digit does not remove that need, because a `1` can still mean millions or hundred thousands depending on the length, but it means every digit sits in its own token, so the units digit is always the last token and two numbers can be lined up digit by digit from the right. My conclusion was that splitting every digit is worth the extra tokens for maths, even though it spent 28 tokens on 28 digits where groups of three spent 15. Fewer tokens is not the same as more useful tokens.

## The hidden tokens in every chat

The last experiment explained a mystery from part 2. The question "Explain what a token is in two sentences." is only 9 or 10 tokens in the six tokenizers above, and 10 or 11 in the four Ollama models when sent raw, yet Ollama counted between 13 and 35 prompt tokens for it in normal use. I asked each Ollama model to count the same texts twice, once raw and once wrapped in its chat template, and the difference is the template:

| Model | Tokens added by the chat template |
|---|---|
| llama3.2:3b | 24 |
| qwen3:4b | 10 |
| gemma3:4b | 8 to 9 |
| deepseek-r1:7b | 2 |

For a short question Llama's wrapping is more than twice the length of the question itself, because its template includes a system header with a knowledge cutoff date. The counts with the template matched my earlier benchmark numbers exactly, which was a reassuring check that the method works.

The raw counts were also a nice bit of detective work. Qwen3 matched Qwen2.5 exactly on all three test texts, while Llama always counted one more than GPT-4 and DeepSeek one more than Qwen2.5, whatever the text. A difference that never changes with the text cannot come from the text, so it has to be something added in front of every input, which here is a start of text marker. The Qwen technical report later confirmed that Qwen's vocabulary started from GPT-4's `cl100k_base`. Phi-4 mini and GPT-4o gave identical counts on all six texts and identical IDs on the emoji, which points to Phi-4 mini using GPT-4o's vocabulary.

## What I took away

- Tokenizers agree on English and disagree everywhere else, so test on the languages and formats you will actually serve.
- A language tax of 24% to 86% is a real cost in money, latency and context, and choosing the tokenizer is choosing who pays it.
- How a tokenizer splits numbers affects what a model can learn about arithmetic, not just how many tokens it uses.
- Chat templates add tokens to every request, almost the same number each time for most models, and that overhead matters most for short prompts at high volume.

## Next in the series

In part 5 I step back from the models and look at the AI assistant I used to study all of this. It made fourteen logged mistakes along the way, and how they were caught turned out to be one of the most useful lessons of the project.

*The scripts are `tokenize_text.py`, `ollama_token_counts.py` and `token_costs.py` in [ai-engineering-lab](https://github.com/udujoel/ai-engineering-lab), and the raw results are in `01-llm-playground/results/step2_token_costs.json`.*
