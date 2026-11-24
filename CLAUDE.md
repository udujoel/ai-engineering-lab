# CLAUDE.md

## Repo

A learning lab of four AI engineering projects: an LLM playground, a multimodal RAG chatbot, a web agent and a deep research system. Plans are in `docs/ai-engineering-build-guide.md`. Each project has its own folder and a README checklist.

Current focus: `01-llm-playground/`.

## Working style

This is a learning project. Understanding matters more than speed.

- Explain the concept briefly before writing code for a step.
- The author is not a programmer but learns hands on. For each step, give the commands for the author to run in their own terminal, explain what each command does and what output to expect, then check the results together. Do not run the learning steps silently on the author's behalf.
- Claude writes code files when a step needs them, explains each piece (what it does, why this way, one rejected alternative, how it connects), and the author runs them.
- Core logic gets the most explanation: decoding and sampling, chunking and retrieval, the agent loop and orchestration. Ask the author to predict or interpret results, and to make the judgement calls.
- One build step at a time. When a step is done, tick it in the project README and suggest a commit message.
- Log every part's numbers, observations, the author's predictions and decisions in the project's `LAB_NOTES.md` as results come in. The author writes blog posts from it.
- Log every mistake, slip, forgotten item or self correction by Claude in `docs/mistakes-log.md` as soon as it is noticed, whoever caught it. Each entry covers context, what happened, why it was a mistake, implications, how it was caught, recovery and the lesson.
- No frameworks such as LangChain or LlamaIndex unless asked.
- Back trade offs with a small experiment or measurement.

## Conventions

- Python 3.12 with uv. Each project is its own uv project. Use `uv run` and `uv add`.
- Ollama at `http://localhost:11434`. Hugging Face caches live outside the repo.
- Use the `mps` torch device when available, otherwise CPU.
- pytest for tests, ruff for lint and format.
- Secrets in `.env` only. Keep `.env.example` current.
- Eval databases are gitignored. Summaries go in the project README.
- Docs are plain and concise. No em dashes.

## Never commit

Model weights, datasets, `.env` files or anything in `docs/reference-images/`.
