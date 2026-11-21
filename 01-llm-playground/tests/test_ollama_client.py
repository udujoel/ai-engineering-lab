"""Checks the speed maths against the numbers `ollama run --verbose` printed in step 1.

No server needed: the response below is the llama3.2:3b run from step 1, part B.
"""

import pytest
from ollama import GenerateResponse

from playground.ollama_client import Timing, same_model, tokens_per_second


def test_tokens_per_second_matches_ollama_cli():
    # eval count 76, eval duration 1.04222 s, and the CLI printed "eval rate: 72.92 tokens/s"
    assert tokens_per_second(76, 1_042_220_000) == pytest.approx(72.92, abs=0.01)


def test_tokens_per_second_is_zero_when_nothing_was_timed():
    assert tokens_per_second(0, 0) == 0.0
    assert tokens_per_second(5, 0) == 0.0


def test_timing_from_response():
    response = GenerateResponse(
        model="llama3.2:3b",
        total_duration=4_134_296_083,
        load_duration=2_842_467_625,
        prompt_eval_count=35,
        prompt_eval_duration=245_955_000,
        eval_count=76,
        eval_duration=1_042_220_000,
    )
    t = Timing.from_response(response)
    assert t.load_s == pytest.approx(2.842, abs=0.001)
    assert t.prefill_tps == pytest.approx(142.30, abs=0.01)
    assert t.decode_tps == pytest.approx(72.92, abs=0.01)
    assert t.total_s == pytest.approx(4.134, abs=0.001)


def test_same_model_treats_missing_tag_as_latest():
    assert same_model("llama3.2", "llama3.2:latest")
    assert same_model("qwen3:4b", "qwen3:4b")
    assert not same_model("llama3.2", "llama3.2:3b")
    assert same_model("library/llama3.2", "library/llama3.2:latest")
