# AI Engineering Lab

Four AI engineering projects built from first principles, from token sampling to a multi agent research system. Core loops are written by hand first, then compared with frameworks and hosted models.

| # | Project | Status |
|---|---|---|
| 1 | [LLM Playground](01-llm-playground/) | In progress |
| 2 | Customer Support Chatbot (multimodal RAG) | Planned |
| 3 | Ask the Web Agent (tools and MCP) | Planned |
| 4 | Deep Research (multi agent) | Planned |

Plans and architecture diagrams for each project are in the [build guide](docs/ai-engineering-build-guide.md). Project ideas follow ByteByteGo's AI Engineering course. All code and diagrams here are original.

## Layout

```
01-llm-playground/
02-support-rag/
03-web-agent/
04-deep-research/
shared/   # common clients, tracing, eval harness
evals/    # datasets and results
infra/    # docker compose, terraform
docs/
```

Folders are added as each project starts.

## Stack

Python 3.12 with uv, Ollama, Hugging Face transformers, Streamlit, FastAPI.

## Getting started

1. Install [uv](https://docs.astral.sh/uv/) and [Ollama](https://ollama.com/).
2. Pull a model, for example `ollama pull qwen2.5:7b`.
3. Follow the README in a project folder.

## Author

Joel Udu · [joeludu.com](https://joeludu.com)
