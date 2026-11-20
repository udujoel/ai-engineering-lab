"""Checks that the real model loads and predicts something sensible. Marked slow: it loads 1 GB."""

import pytest
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from playground.device import pick_device

MODEL_NAME = "Qwen/Qwen2.5-0.5B"


@pytest.mark.slow
def test_paris_is_a_top_guess():
    device = pick_device()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, dtype=torch.float32).to(device)

    input_ids = tokenizer("The capital of France is", return_tensors="pt").input_ids.to(device)
    with torch.inference_mode():
        logits = model(input_ids).logits

    probs = torch.softmax(logits[0, -1].float(), dim=-1)
    assert torch.isclose(probs.sum(), torch.tensor(1.0, device=device), atol=1e-4)

    top5 = [tokenizer.decode([i]).strip() for i in torch.topk(probs, k=5).indices.tolist()]
    assert "Paris" in top5
