# CLAUDE.md

## Repo

A learning lab of four AI engineering projects: an LLM playground, a multimodal RAG chatbot, a web agent and a deep research system. Plans are in `docs/ai-engineering-build-guide.md`. Each project has its own folder and a README checklist.

Current focus: `01-llm-playground/`.

## Working style

This is a learning project. Understanding matters more than speed.

- Explain the concept briefly before writing code for a step.
- The author writes the core logic: decoding and sampling, chunking and retrieval, the agent loop and orchestration. For these, provide signatures, tests and hints, then review. Write full code only when asked.
- Setup, UI wiring, config, plotting and test scaffolding can be written directly.
- One build step at a time. When a step is done, tick it in the project README and suggest a commit message.
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
