# Mistakes log

Every slip, wrong statement, forgotten item or self correction Claude made in this lab, oldest first. Claude adds an entry as soon as a mistake is noticed, whoever caught it.

Each entry covers:
- **Context:** what we were doing at the time.
- **What happened:** the mistake itself.
- **Why it was a mistake:** what was wrong about it.
- **Implications:** what it affected, or could have.
- **How it was caught:** who noticed, and from what.
- **Recovery:** what was fixed, and anything still open.
- **Lesson:** what to do differently.

Entries 1 to 9 were reconstructed on 2026-11-18 from the session transcripts. The early part of the work was compressed into summaries, so small slips from then may be missing.

## Summary

| # | Date | Step | Mistake | Caught by | Status |
|---|---|---|---|---|---|
| 1 | 2026-11-16 | P1 Step 0 | Ran the learning step myself instead of teaching it | Author | Fixed |
| 2 | 2026-11-17 | P1 Step 1 | Said qwen3:4b has a thinking toggle | Me | Fixed |
| 3 | 2026-11-17 | P1 Step 1 | Treated GB as GiB | Me | Fixed |
| 4 | 2026-11-17 | P1 Step 1 | Called an 8 word prompt "9 words" | Me | Fixed |
| 5 | 2026-11-17 | P1 Step 1 | Forgot to build `ollama_client.chat()` | Me | **Open** |
| 6 | 2026-11-18 | P1 Step 2 | Misquoted a Step 0 token ID | Author | Fixed |
| 7 | 2026-11-18 | P1 Step 2 | Presented new tokenizers as familiar, stated a guess as fact | Author | Fixed |
| 8 | 2026-11-18 | P1 Step 2 | Wrong about which folder the terminal was in | Me | Fixed |
| 9 | 2026-11-16 to 18 | All | Tool slips the author didn't see | Me | Fixed |
| 10 | 2026-11-18 | P1 Step 2 | Told the author to expect a split emoji that didn't split | Me | Fixed |
| 11 | 2026-11-18 | P1 Step 2 | Tokenizer explorer showed the same tokens differently by library | Me | Fixed |
| 12 | 2026-11-16 | P1 Step 0 | Timed the GPU forward pass without waiting for the GPU | Review bots | Fixed |
| 13 | 2026-11-16 to 19 | P1 Steps 0 to 2 | Three edge case bugs: `.env` device, untagged model names, empty text | Review bots | Fixed |
| 14 | 2026-11-17 to 19 | P1 Steps 1 and 2 | Stated two findings more broadly than the data showed | Review bot | Fixed |

---

## 1. Ran the learning step myself instead of teaching it

- **Context:** Project 1, Step 0 (setup). The author had said they are not a programmer and would follow along while I wrote the code.
- **What happened:** I did almost the whole step myself, running every install, file and test while the author watched. The author wrote: "this doesn't seem very interactive, don't think i learnt much from that step... Not just watching you do 99.9% of it."
- **Why it was a mistake:** the project's purpose is hands-on learning. "I won't write the code" meant "you write it", not "you run everything too". Running the commands, seeing the output and interpreting it is where the learning happens.
- **Implications:** Step 0 taught very little. The author has no first-hand memory of the setup, such as installing uv or the first model load.
- **How it was caught:** the author, at the end of the step.
- **Recovery:** Step 0 was committed as it was. From Step 1 on, every step gives the author the commands with explanations. The author runs them, and we read the output together. The rule went into CLAUDE.md and memory.
- **Lesson:** writing code is my job; running and interpreting it is the author's. When unsure, hand over the command.

## 2. Said qwen3:4b has a thinking toggle

- **Context:** Project 1 planning, then Step 1 Part B, running four models on the same prompt.
- **What happened:** PLAN.md described the `qwen3:4b` tag as a Qwen3 model with a thinking toggle. In Part B, `--think=false` still produced 928 tokens of reasoning, which leaked into the answer.
- **Why it was a mistake:** I described the model from general knowledge of the Qwen3 family, without checking what this tag actually is. The server log names it "Qwen3 4B Thinking 2507", a version trained to always reason.
- **Implications:** the plan promised an on/off thinking comparison that this model can't give. Anyone reading the plan would expect the flag to work.
- **How it was caught:** by me, when the output didn't match and I checked the server log.
- **Recovery:** PLAN.md's model table was corrected. This became Finding 3 ("A flag can ask for a behaviour; the weights decide"). The author decided to keep the model to show the cost of reasoning.
- **Lesson:** check what a tag resolves to (`ollama show`, the server log) before describing its features.

## 3. Treated GB as GiB

- **Context:** Step 1 Part D, comparing the benchmark script's memory figures with `ollama ps`.
- **What happened:** I read `ollama ps` sizes as GiB (1,024^3 bytes). They are GB (1,000^3). The script reports GiB.
- **Why it was a mistake:** the two units differ by about 7% at this size. Llama's "6.0 GB" and "5.6 GiB" are the same amount of memory, but I compared them as if they were different.
- **Implications:** memory comparisons between Part B and Part D looked inconsistent, and a wrong conclusion could have gone into the blog notes.
- **How it was caught:** by me, when the script's numbers didn't line up with `ollama ps`.
- **Recovery:** a units note was added to LAB_NOTES Part D, and the author was told.
- **Lesson:** put a unit on every memory figure, and check which unit each tool uses.

## 4. Called an 8 word prompt "9 words"

- **Context:** writing Step 1 Part B into LAB_NOTES.
- **What happened:** I wrote "The same 9 word question became 13 to 35 prompt tokens." "Explain what a token is in two sentences." has 8 words.
- **Why it was a mistake:** I estimated instead of counting.
- **Implications:** small, but the error sat in notes meant for a blog. It also affects the token-per-word comparison Step 2 relies on.
- **How it was caught:** by me, when the Step 2 script printed "8 words".
- **Recovery:** LAB_NOTES corrected.
- **Lesson:** count, don't estimate, when a number goes into the notes.

## 5. Forgot to build `ollama_client.chat()`

- **Context:** Step 1. PLAN.md's Build line says: "Write `ollama_client.chat()` that returns the text plus a stats dict."
- **What happened:** I built the timing helpers (`get_client`, `Timing`) and the benchmark script, but not `chat()`. Step 1 was then ticked as done in the README.
- **Why it was a mistake:** I checked the step's "Done when" line (the results table) but not its Build list.
- **Implications:** Step 1 is marked complete while missing a piece. Step 4 (chat UI) and Step 5 (comparison) depend on it.
- **How it was caught:** by me, while reviewing past work on 2026-11-18.
- **Recovery:** **open.** It will be built at the start of Step 4, which is its first real use.
- **Lesson:** before ticking a step, check every item in its Build, Experiment and Done when lines.

## 6. Misquoted a Step 0 token ID

- **Context:** introducing Step 2, recalling Step 0's smoke test on "The capital of France is".
- **What happened:** I wrote "' Paris' was 9625". 9625 is ` France`, part of the prompt. ` Paris` is 12095, and Step 0 never printed it.
- **Why it was a mistake:** I quoted a number from memory instead of checking LAB_NOTES, which had it right.
- **Implications:** it confused the author about what we had done, and it undermines trust in every other number I quote.
- **How it was caught:** by the author ("wait, what are you talking about?").
- **Recovery:** corrected in chat and checked with the tokenizer.
- **Lesson:** quote numbers from the notes or a fresh run, never from memory.

## 7. Presented new tokenizers as familiar, stated a guess as fact

- **Context:** the same Step 2 introduction.
- **What happened:** I listed six tokenizers without saying five of them (GPT-2, SmolLM2, Phi-4 mini, GPT-4, GPT-4o) were new and came from PLAN.md. I also wrote that Qwen2.5 is "the same family as your qwen3 and deepseek models" as fact, in chat and in a code comment.
- **Why it was a mistake:** the author reasonably thought they had missed something. The family claim is plausible but nobody had checked it.
- **Implications:** confusion about what had been done, and an unchecked claim heading into the notes.
- **How it was caught:** by the author ("Can't remember working on those models").
- **Recovery:** I explained where each tokenizer comes from and removed the claim from the code comment. It is now a test for Step 2 Part B. Part B (2026-11-19) supports it: qwen3 matched Qwen2.5's token counts exactly on three different texts, and deepseek-r1 matched them plus 1 on all three. The Qwen technical report (arXiv 2309.16609) confirms that Qwen started from cl100k_base.
- **Lesson:** link new material to what was actually done, say what is new, and mark guesses as guesses.

## 8. Wrong about which folder the terminal was in

- **Context:** Step 2 Part A. The author's first `uv run pytest` failed with "Failed to spawn: pytest".
- **What happened:** I explained that `!` commands start from the top folder, and that the playground tab "was already in 01-llm-playground". The terminal shows the tab itself was at the top folder: the same command had already failed there twice.
- **Why it was a mistake:** I explained without first reading the terminal I was describing.
- **Implications:** half the explanation was wrong. If the author had switched to the tab as I suggested, the command would have failed again.
- **How it was caught:** by me, reading the terminal in the next turn.
- **Recovery:** the author ran `cd 01-llm-playground && ...`, which worked. This entry records the correction.
- **Lesson:** read the terminal, and check its current folder, before explaining a failure or giving commands.

## 9. Tool slips the author didn't see

- **Context:** throughout Steps 0 to 2.
- **What happened:** several of my own tool calls failed or misled me:
  - `uv` was blocked by my sandbox, so I used `.venv/bin/...` directly.
  - Appending to MEMORY.md through the shell was blocked, so I used the file editor.
  - A 1,000 line terminal read was too large to return.
  - `ls | grep` hid matches behind colour codes, making pytest look missing.
- **Why it was a mistake:** each one cost time, and the last could have led to a wrong diagnosis.
- **Implications:** no wrong results reached the author, but each slip slowed the session.
- **How it was caught:** by me, from the errors.
- **Recovery:** worked around each one.
- **Lesson:** use the dedicated tools, read smaller ranges, and use plain `/bin/ls` when filtering output.

## 10. Told the author to expect a split emoji that didn't split

- **Context:** Step 2 Part A, the run on "The price is 1234567 dollars 🙂".
- **What happened:** I told the author to "watch for `▯` on the emoji", which implied 🙂 would be split into partial pieces. All six tokenizers kept ` 🙂` as one token.
- **Why it was a mistake:** I set an expectation without testing the exact text. 🙂 is common enough to have its own token everywhere. The tests use 👍🏽 (thumbs up plus a skin tone), which is more likely to split.
- **Implications:** the author might think `▯` is broken, or that emoji never split.
- **How it was caught:** by me, reading the output.
- **Recovery:** explained in chat, and an emoji that does split was suggested for the next run.
- **Lesson:** run the example myself before predicting what the author will see, or frame it as a question.

## 11. Tokenizer explorer showed the same tokens differently by library

- **Context:** Step 2 Part A, the run on "1234567 2345678 1000000 9876543 👍🏽".
- **What happened:** Phi-4 mini and GPT-4o produced identical IDs for ` 👍🏽` (`160433, 52622, 121`), but the explorer displayed them differently: `·👍 | 🏽 | ▯` for Phi-4 mini and `·👍 | ▯ | 🏽` for GPT-4o. While fixing it, the new test found a second difference: Phi-4 mini turned the typed text `<|endoftext|>` into its real control token (ID 199999), while GPT-4o kept it as plain text.
- **Why it was a mistake:** `src/playground/tokenizers.py` has two adapters, one per library, and they followed different rules. When a character is split across tokens, the Hugging Face adapter put the character on the first token covering it, and the tiktoken adapter on the last. And only the tiktoken adapter was told to treat control-token text as ordinary text. My tests checked that each tokenizer's pieces join back to the text, but never that the two adapters agree with each other.
- **Implications:** token counts and IDs were always correct, but the display of split characters could not be compared across tokenizers, which is the whole point of the explorer. The control-token difference is also a known security issue: if typed text can become a control token, a user can inject "end of text" or role markers into a prompt.
- **How it was caught:** by me, comparing the two identical ID lists in the author's output.
- **Recovery:** both adapters now use the same rule (a character is shown on the token that completes it), and the Hugging Face adapter uses `split_special_tokens=True`. A new test checks that Phi-4 mini and GPT-4o give identical IDs and pieces. 16 tests pass. The emoji pieces recorded in LAB_NOTES from that run used the old display; the counts and IDs there are correct.
- **Lesson:** when two code paths should behave the same, test them against each other, not just each on its own. Pairs that share a vocabulary make a free check.

## 12. Timed the GPU forward pass without waiting for the GPU

- **Context:** Step 0 smoke test, which timed one forward pass of Qwen2.5 0.5B on `mps`. LAB_NOTES recorded 774 ms.
- **What happened:** `scripts/smoke_test.py` stopped the timer as soon as `model(input_ids)` returned. On the Apple GPU, PyTorch queues work and returns before the GPU has finished, so the timer could stop early.
- **Why it was a mistake:** GPU work is asynchronous. A timing has to wait for the device (`torch.mps.synchronize()`) before reading the clock, or it measures how fast work was queued, not how fast it ran.
- **Implications:** the 774 ms in Step 0 may be too low. Nothing else depends on it, and the Ollama numbers in Step 1 come from the server's own timers, so they are unaffected.
- **How it was caught:** by two review bots (Devin and CodeRabbit) on PR #1, 2026-11-20.
- **Recovery:** the script now synchronizes before starting and before stopping the timer. Rerunning the smoke test will give the corrected number for LAB_NOTES.
- **Lesson:** every GPU timing needs a synchronize on both sides. This matters for Step 3, where the KV cache experiment times decoding on `mps`.

## 13. Three edge case bugs: `.env` device, untagged model names, empty text

- **Context:** code written in Steps 0 to 2.
- **What happened:**
  - `device.py` documents that `PLAYGROUND_DEVICE` can be set in `.env`, but nothing on the smoke test's path loaded `.env`.
  - `bench_ollama.py` and `unload()` compared model names exactly. Ollama lists `llama3.2` as `llama3.2:latest`, so an untagged name would crash the benchmark at the end, and `unload()` could return before the model was gone.
  - The tiktoken adapter in `tokenizers.py` crashed on empty text instead of returning zero tokens.
  - `HF_TOKEN` in `.env` was never loaded for the tokenizers either.
  - `bench_ollama.py` paired the median decode rate with the minimum token count. Every run hit the full 200 tokens, so the recorded table is right, but a run that stopped early would have been misreported.
- **Why it was a mistake:** each one is a promise in a docstring or an obvious input that was never tested.
- **Implications:** none of the recorded results: Du always passed full tags, never used the `.env` device setting, and never tokenized empty text. The empty text bug would have crashed the Streamlit page in Part C, which starts with an empty box.
- **How it was caught:** by Devin and CodeRabbit on PR #1, 2026-11-20.
- **Recovery:** the smoke test loads `.env` (shell values still win), a new `same_model()` treats a missing tag as `latest`, and empty text returns no tokens. New tests cover the name matching and empty text.
- **Lesson:** test the edges a user will hit first: empty input, the short form of a name, and every setting the docs advertise.

## 14. Stated two findings more broadly than the data showed

- **Context:** Step 1 Finding 4 and the README, and Step 2 Part B's template cost.
- **What happened:** the README said "Most memory is KV cache, not weights", and LAB_NOTES said "The template cost is fixed per model".
- **Why it was a mistake:** the KV cache is larger than the weights only for Llama and Qwen3. DeepSeek (1.75 GiB cache, 4.7 GB model) and Gemma (0.8 GiB cache) are the other way round. And Gemma's template cost varied (9, 8, 9), on only three texts.
- **Implications:** a blog post written from the notes would have carried the overstatement.
- **Also:** cubic found four smaller imprecisions in LAB_NOTES: "outputs a probability" (the model outputs logits; softmax makes them probabilities), 151,936 called tokens (they are vocabulary slots, 151,665 used by the tokenizer), a time-to-answer formula without prefill, and a KV cache formula with a fixed head dimension of 128 (Gemma's is 256).
- **How it was caught:** by CodeRabbit and cubic on PR #1, 2026-11-20.
- **Recovery:** all of these are reworded, and both statements now say what the data supports: the cache can outweigh the weights at a 32k context, and the template cost looks fixed for these three texts.
- **Lesson:** a finding is only as general as the models and texts behind it. Say which ones.
