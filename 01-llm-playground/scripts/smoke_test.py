"""Step 0 smoke test: load Qwen2.5 0.5B on the GPU and show its top 5 guesses for the next token.

Run with:  uv run python scripts/smoke_test.py ["your prompt"]

This is one turn of the loop that step 3 builds: text -> token IDs -> model -> logits ->
probabilities. Generation is just this step repeated, appending the chosen token each time.
"""

import sys
import time

import torch
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer

from playground.device import pick_device

MODEL_NAME = "Qwen/Qwen2.5-0.5B"  # the base model: it continues text, it does not chat
DEFAULT_PROMPT = "The capital of France is"


def sync(device: torch.device) -> None:
    """Wait until the GPU has finished all queued work. The CPU runs in order, so it needs none."""
    if device.type == "mps":
        torch.mps.synchronize()


def main(prompt: str) -> None:
    load_dotenv()  # so PLAYGROUND_DEVICE in .env works; values already exported in the shell win
    device = pick_device()
    print(f"Device: {device}")

    start = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    # float32 keeps the probabilities exact; at 0.5B parameters it needs only about 2 GB.
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, dtype=torch.float32).to(device)
    print(f"Loaded {MODEL_NAME} in {time.perf_counter() - start:.1f}s")

    # 1. Text to token IDs. Each ID is a row number in the model's vocabulary.
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
    pieces = [tokenizer.decode([i]) for i in input_ids[0].tolist()]
    print(f"\nPrompt: {prompt!r}")
    print(f"Tokens ({len(pieces)}): {pieces}")
    print(f"IDs:    {input_ids[0].tolist()}")

    # 2. One forward pass. logits has shape (batch, sequence length, vocabulary size):
    #    one score for every vocabulary entry, at every position in the prompt.
    #    The GPU runs work in the background: Python gets `logits` back before the GPU has
    #    finished. synchronize() waits for it, so the timer measures the real work.
    sync(device)
    start = time.perf_counter()
    with torch.inference_mode():
        logits = model(input_ids).logits
    sync(device)
    print(
        f"\nForward pass: {(time.perf_counter() - start) * 1000:.0f} ms, "
        f"logits shape {tuple(logits.shape)}"
    )

    # 3. Only the last position predicts the next token. Softmax turns scores into
    #    probabilities that add up to 1. Do it in float32 to avoid rounding problems on MPS.
    probs = torch.softmax(logits[0, -1].float(), dim=-1)
    top = torch.topk(probs, k=5)

    print("\nTop 5 next tokens:")
    for p, token_id in zip(top.values.tolist(), top.indices.tolist(), strict=True):
        print(f"  {tokenizer.decode([token_id])!r:<14} id={token_id:<7} {p:6.1%}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PROMPT)
