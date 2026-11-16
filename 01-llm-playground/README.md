# Project 1: LLM Playground

See what happens between a prompt and a reply. Inspect tokenization, step through decoding, tune sampling and compare models on the same prompt.

## Stack

Ollama, Hugging Face transformers (Qwen2.5 0.5B), tiktoken, Streamlit, SQLite.

## Build steps

- [ ] 1. Run three or four local models from different families through Ollama.
- [ ] 2. Tokenizer explorer: tokens, IDs and token counts across tokenizers.
- [ ] 3. Hand written decoding loop: greedy, temperature, top k, top p and beam search, with per step probability charts.
- [ ] 4. Chat UI with model picker, decoding sliders, system prompt and streaming.
- [ ] 5. Side by side model comparison with latency and tokens per second.
- [ ] 6. Eval harness: 20 to 30 prompts, exact match and LLM judge, results in SQLite.
- [ ] 7. Base versus instruct model on the same prompts.
- [ ] 8. Stretch: small supervised fine tune with TRL.

## Done when

The UI and eval results show how sampling settings change the output.

## Findings

Results and trade offs are added here as steps are completed.
