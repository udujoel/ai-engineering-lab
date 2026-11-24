"""Checks that every tokenizer's pieces line up with the text.

Marked slow: the first run downloads each tokenizer (a few MB) from Hugging Face or OpenAI.
"""

import pytest

from playground.tokenizers import ALL, tokenize

TRICKY = 'Hello  world\n  1234567 🙂👍🏽 olá, ação! {"key": [1, 2]} <|endoftext|>'


@pytest.mark.slow
@pytest.mark.parametrize("name", ALL)
def test_pieces_join_back_to_the_text(name):
    # The key property: no text lost, none repeated, even for emoji split over several tokens.
    t = tokenize(name, TRICKY)
    assert "".join(t.pieces) == TRICKY
    assert len(t.pieces) == len(t.ids) == t.count


@pytest.mark.slow
def test_same_ids_display_the_same_pieces():
    # Phi-4 mini uses GPT-4o's vocabulary, so its IDs match. The pieces must match too, even
    # though one goes through Hugging Face and the other through tiktoken. A 2026-11-18 bug
    # showed the split emoji 👍🏽 differently in the two.
    phi, gpt4o = tokenize("phi-4-mini", TRICKY), tokenize("gpt-4o", TRICKY)
    assert phi.ids == gpt4o.ids
    assert phi.pieces == gpt4o.pieces


@pytest.mark.slow
@pytest.mark.parametrize("name", ALL)
def test_empty_text_has_no_tokens(name):
    # The Streamlit page starts with an empty box, so this must not crash.
    assert tokenize(name, "").count == 0


def test_unknown_tokenizer_is_a_clear_error():
    with pytest.raises(KeyError, match="Choose from"):
        tokenize("not-a-tokenizer", "hi")
