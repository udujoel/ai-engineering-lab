"""Fast checks for the cost maths. A fake counter stands in for real tokenizers."""

import pytest

from playground.sample_texts import SAMPLES
from playground.token_costs import Cost, language_penalty, measure

TEXTS = {"english": "a b c d", "portuguese": "a b c d e f"}


def fake_count(name: str, text: str) -> int:
    # "words" counts one token per word; "chars" one per character, spaces included.
    return len(text.split()) if name == "words" else len(text)


def test_measure_covers_every_pair_in_order():
    costs = measure(["words", "chars"], TEXTS, fake_count)
    assert [(c.tokenizer, c.sample) for c in costs] == [
        ("words", "english"),
        ("words", "portuguese"),
        ("chars", "english"),
        ("chars", "portuguese"),
    ]
    assert costs[0] == Cost("words", "english", characters=7, tokens=4)


def test_tokens_per_char():
    assert Cost("x", "y", characters=8, tokens=2).tokens_per_char == 0.25
    assert Cost("x", "y", characters=0, tokens=0).tokens_per_char == 0.0


def test_language_penalty_is_portuguese_over_english():
    penalty = language_penalty(measure(["words", "chars"], TEXTS, fake_count))
    assert penalty == {"words": 1.5, "chars": pytest.approx(11 / 7, abs=1e-3)}


def test_samples_are_the_agreed_set():
    assert list(SAMPLES) == ["english", "portuguese", "python", "json", "numbers", "emoji"]
    assert all(SAMPLES.values())
