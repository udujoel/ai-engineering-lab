# Inside the LLM Playground

A blog series written from Project 1 of this lab (`01-llm-playground/`). Each post is drawn from `LAB_NOTES.md`, `docs/mistakes-log.md` and the measured results, and every number in it comes from a real run on a MacBook Pro with an M2 Pro and 32 GB of memory.

**Interactive demo:** [LLM Engineering Flight Deck](https://www.joeludu.com/demos/llm-flight-deck.html). A self hosted copy is in [`demo/flight-deck.html`](demo/flight-deck.html), a single HTML file that can be dropped onto a personal site as it is.

| Part | Post | Demo station |
|---|---|---|
| 1 | [A model outputs odds, not words](01-a-model-outputs-odds-not-words.md) | Inside a model |
| 2 | [Decode is a memory problem](02-decode-is-a-memory-problem.md) | Local models |
| 3 | [Where the memory goes: the KV cache](03-where-the-memory-goes.md) | Local models (KV cache slider) |
| 4 | [The same meaning has different prices](04-the-same-meaning-has-different-prices.md) | Tokenizers |
| 5 | [What my AI study assistant got wrong](05-what-my-ai-study-assistant-got-wrong.md) | All |

Each post has front matter (`title`, `series`, `part`, `date`, `description`, `tags`, `demo`) so it can be copied into most Markdown blog setups without changes. Later posts will follow as Step 3 (decoding) and the remaining steps are built.
