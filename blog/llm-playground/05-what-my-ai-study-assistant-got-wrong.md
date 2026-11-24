---
title: "What my AI study assistant got wrong"
series: "Inside the LLM Playground"
part: 5
date: 2026-11-21
description: "Fourteen logged mistakes from the AI assistant I studied with: what happened, why, how each was caught and corrected, and what it means for engineers who rely on AI."
tags: [llm, ai-assisted-engineering, code-review, learning-in-public, ai-infrastructure]
demo: https://www.joeludu.com/demos/llm-flight-deck.html
---

# What my AI study assistant got wrong

*Part 5 of Inside the LLM Playground, a series on what I learned building a small LLM lab on my laptop as I move towards AI infrastructure engineering.*

> **The demo.** The results these mistakes touched are all in the [LLM Engineering Flight Deck](https://www.joeludu.com/demos/llm-flight-deck.html). The forward pass timing in its first station is the corrected one from mistake 12 below.

## Why I kept a mistakes log

I studied this whole project with an AI assistant, Claude, which wrote most of the code, explained each piece and handed me the commands to run. Early on I asked it to keep a log of every slip, wrong statement, forgotten item or self correction it made, whoever caught it, with the context, the cause, the fix and the lesson. I did it partly for honesty and partly because I suspected the mistakes would teach me as much as the results.

By the end of the first project the log had fourteen entries across four days. None of them changed a measured result in a way that survived into my notes, but several would have if nobody had caught them. Below I go through each one, grouped by the kind of mistake, and finish with what I think it means for anyone who builds with an AI assistant.

| # | Mistake | Caught by |
|---|---|---|
| 1 | Ran the learning step itself instead of teaching it | Me |
| 2 | Said qwen3:4b has a thinking toggle | The assistant |
| 3 | Treated GB as GiB | The assistant |
| 4 | Called an 8 word prompt "9 words" | The assistant |
| 5 | Forgot to build `ollama_client.chat()` | The assistant |
| 6 | Misquoted a token ID from memory | Me |
| 7 | Presented new tokenizers as familiar and stated a guess as fact | Me |
| 8 | Was wrong about which folder the terminal was in | The assistant |
| 9 | Tool slips I never saw | The assistant |
| 10 | Told me to expect a split emoji that did not split | The assistant |
| 11 | Showed the same tokens differently depending on the library | The assistant |
| 12 | Timed the GPU without waiting for the GPU | Review bots |
| 13 | Three edge case bugs | Review bots |
| 14 | Stated two findings more broadly than the data showed | Review bots |

## Mistakes of process

**1. It did the learning for me.** In the very first step the assistant ran every install, file and test itself while I watched. At the end I told it that I did not think I had learnt much from just watching it do 99.9% of the work. It happened because it read "I am not a programmer, so you write the code" as "you do everything", when what I meant was that it should write code and I would still run it. The fix was a rule in the project instructions that it writes the code and explains it, and I run every command and we read the output together. The way to avoid this is to say plainly which part of the work is yours, because an assistant will optimise for finishing the task unless you tell it the goal is learning. The wider implication is that an AI that is good at doing can quietly take away the practice you came for.

**5. It ticked a step that was not finished.** The plan for Step 1 included building a `chat()` function that returns the text plus a stats dictionary. The assistant built the timing helpers and the benchmark but not `chat()`, then marked the step as done. It had checked the step's "done when" line, the results table, without checking the build list above it. It caught this itself while reviewing past work, and the function is now scheduled for Step 4, where it is first needed. That entry is still open. The lesson is to check every item in a step before ticking it, and for engineers it is a reminder that "done" from an assistant means done against whatever it chose to check.

## Mistakes of memory and confidence

**2. It described a model from general knowledge.** The plan described `qwen3:4b` as a Qwen3 model with a thinking toggle. When I ran it with `--think=false`, it still wrote 928 tokens of reasoning. The assistant had described the model family from what it knew in general, without checking what this particular tag resolves to. It caught the problem when the output did not match and it read the server log, which names the model "Qwen3 4B Thinking 2507". The plan was corrected, and the mismatch became one of my favourite findings: a flag can ask for a behaviour, but the weights decide. To avoid it, check what a tag actually is with `ollama show` or the log before describing what it can do. The implication is that an assistant's knowledge is about families and versions in general, while your system runs one specific artefact.

**6. It quoted a number from memory.** While introducing Step 2 it told me that " Paris" was token 9625. In fact 9625 is " France", which was part of the prompt, and " Paris" is 12095, a number Step 0 never printed. I caught it because I had no memory of that number and asked what it was talking about. It corrected the claim and checked it with the tokenizer. The rule since then has been to quote numbers only from the notes or a fresh run. For anyone relying on AI, this is the clearest case of all, because a confident wrong number undermines trust in every other number it gives you.

**7. It stated a guess as a fact.** In the same introduction it listed six tokenizers without saying that five of them were new to me, and it wrote, in chat and in a code comment, that Qwen2.5 is "the same family as your qwen3 and deepseek models". I said I could not remember working with those models, which is how this was caught. The family claim was plausible but unchecked, so it was removed from the comment and turned into an experiment instead. That experiment later supported it, since Qwen3 matched Qwen2.5's token counts exactly and the Qwen technical report confirmed the shared starting vocabulary. The lesson is to link new material to what was actually done and to mark a guess as a guess. The implication I take from it is that the line between "likely" and "checked" is exactly where an assistant tends to blur, and turning a claim into a test is a good habit for humans too.

**10. It predicted output without testing it.** Before one run it told me to watch for the `▯` symbol on the emoji, which implied that 🙂 would be split into partial pieces. All six tokenizers kept it as one token. It had set an expectation without testing the exact text, and it noticed when it read my output. The fix was to explain the result and suggest an emoji with a skin tone modifier, which does split. The way to avoid it is to run the example first or frame the prediction as a question. In a learning setting a wrong expectation can make you think your tools are broken, and in production work it can make you chase a bug that does not exist.

## Mistakes of carelessness

**3. It mixed up units.** It read the sizes from `ollama ps` as GiB when they are GB, which differ by about 7% at this size. So Llama's 6.0 GB and 5.6 GiB looked like two different amounts of memory when they were the same. It caught this when the numbers would not line up, and a units note went into my lab notes. The lesson is simple: put a unit on every memory figure and check which unit each tool uses. Small unit errors are exactly how an invented finding ends up in a blog post.

**4. It estimated instead of counting.** It wrote that "the same 9 word question" became 13 to 35 tokens, but the question has 8 words. It noticed when the Step 2 script printed "8 words" and corrected the notes. A trivial slip, but it sat in notes meant for publication, and the fix is to count rather than estimate whenever a number goes into writing.

**8. It explained an error without reading the terminal.** When my first `uv run pytest` failed, it explained that a particular terminal tab "was already in 01-llm-playground". The terminal showed that the tab was in the top folder, where the same command had already failed twice. It realised this on its next turn, and I fixed it with `cd 01-llm-playground`. The lesson is to read the actual state before explaining a failure. For engineers, this is the familiar risk of an assistant reasoning from what should be true instead of what the screen says.

**9. Tool slips I never saw.** Several of its own tool calls failed along the way. `uv` was blocked in its sandbox, a shell append to a notes file was blocked, a 1,000 line terminal read was too large to return, and `ls | grep` hid matches behind colour codes and made pytest look missing. It caught each one from the error and worked around it. None reached my results, but the last one could easily have led to a wrong diagnosis. It is a reminder that an assistant works through its own layer of tools, and that layer can fail in ways you never see.

## Mistakes in the code

**11. Two code paths that disagreed.** My tokenizer explorer has two adapters, one for Hugging Face tokenizers and one for tiktoken. Phi-4 mini and GPT-4o produced identical token IDs for 👍🏽 but displayed the pieces differently, because the two adapters followed different rules for where to show a character split across tokens. While fixing it, a new test found a second difference: Phi-4 mini turned the typed text `<|endoftext|>` into its real control token, while GPT-4o kept it as plain text. That second one is a known security issue, because if typed text can become a control token, a user can inject markers into a prompt. The assistant caught it by comparing the two identical ID lists in my output. Both adapters now follow the same rule, and a test checks that the two tokenizers agree. The lesson is to test two code paths that should behave the same against each other, not only each on its own. Pairs that share a vocabulary make a free check.

**12. It timed the GPU without waiting for the GPU.** This is the one I mentioned in part 1. The smoke test stopped its timer as soon as the model call returned, but PyTorch on Apple's GPU queues work and returns before the work is done. Two automated reviewers on my pull request, Devin and CodeRabbit, caught it. The fix was to call `torch.mps.synchronize()` before starting and stopping the clock, and the rerun gave 212 ms against the original 774 ms. Because waiting can only add time, the sync cannot explain the drop, and my best guess is first run warm up. These are single runs, so that stays a hypothesis until I repeat the measurement with a warm up run and several synced timings. The lesson is that every GPU timing needs a synchronize on both sides and a warm up run. For infrastructure work this is not a small thing, because benchmarks drive decisions about hardware and capacity.

**13. Edge case bugs.** The same reviewers found a group of smaller bugs. A device setting the docs said could go in `.env` was never loaded, an untagged model name like `llama3.2` would have crashed the benchmark because Ollama lists it as `llama3.2:latest`, and the tiktoken adapter crashed on empty text. The empty text bug would have crashed the Streamlit page I am building next, since it starts with an empty text box. None of my recorded results were affected, because I always passed full tags and never tokenized empty text. Each bug was a promise in a docstring or an obvious input that nobody had tested, and each now has a fix and a test. The lesson is to test the edges a user will hit first: empty input, the short form of a name and every setting the docs advertise.

**14. Findings stated too broadly.** My README said "most memory is KV cache, not weights", and my notes said the chat template cost "is fixed per model". The reviewers pointed out that the cache is larger than the weights only for Llama and Qwen3, not DeepSeek or Gemma, and that Gemma's template cost varied, measured on only three texts. A third reviewer, cubic, found four smaller imprecisions, such as calling logits probabilities and counting vocabulary slots as tokens. All of them were reworded to say what the data supports. The lesson I keep coming back to is that a finding is only as general as the models and texts behind it, so say which ones.

## How the mistakes were caught

Counting the entries, the assistant caught eight of its own mistakes, I caught three, and automated review bots caught the remaining three groups. The bots found the subtle technical ones, such as asynchronous GPU timing and untested edge cases, that neither of us noticed while working. I caught the ones that clashed with my own memory of what we had done. The assistant caught the ones where reality pushed back, such as a log, a script's output or a test.

That pattern is the main thing I learned. Most mistakes were caught because something concrete contradicted a claim. A log disagreed with the plan, a script printed a different number or a test failed. The mistakes that got furthest were the ones where nothing pushed back, like a confident number quoted from memory.

## What this means for engineers who rely on AI

- **Make the assistant cite its source.** Numbers should come from a run, a log or the notes, never from memory. If it cannot point to where a number came from, treat it as a guess.
- **Turn claims into tests.** "Same family" became an experiment with a clear result. That habit is cheap and it works for people as well as models.
- **Layer your checks.** The assistant, a human and automated reviewers each caught a different kind of mistake. No single layer would have found them all.
- **Watch the boundaries of "done".** An assistant checks the criteria it chooses. Write down what done means and check every item.
- **Keep a mistakes log.** Writing each mistake down with its cause and lesson turned a stream of small errors into a set of rules that changed how we worked, and it made the whole project more trustworthy rather than less.

Working with an AI assistant made this project possible for me, and I would do it again. It just works best when you treat it like a fast, capable colleague whose claims you still verify, which, now that I write it down, is how good engineering teams treat everyone.

*The full mistakes log, with all fourteen entries, is `docs/mistakes-log.md` in [ai-engineering-lab](https://github.com/udujoel/ai-engineering-lab).*
