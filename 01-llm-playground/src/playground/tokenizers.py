"""Step 2: one interface over two tokenizer libraries.

Every tokenizer here answers the same two questions about a text:
  1. Which integer IDs does it become? (what the model actually sees)
  2. Which slice of the text does each ID cover? (so we can show the pieces)

Hugging Face tokenizers and OpenAI's tiktoken answer question 2 in different ways, so each
gets a small adapter, and the rest of the project only ever calls `tokenize(name, text)`.
"""

from dataclasses import dataclass
from functools import cache

import tiktoken
from transformers import AutoTokenizer

# Hugging Face repos. Only the tokenizer files are downloaded (a few MB each), never the weights.
HF_TOKENIZERS = {
    "gpt2": "gpt2",  # OpenAI, 2019: the original byte level BPE
    "qwen2.5": "Qwen/Qwen2.5-0.5B",  # Alibaba: the Step 0 model's tokenizer, already downloaded
    "smollm2": "HuggingFaceTB/SmolLM2-135M",  # Hugging Face: small vocabulary, English focused
    "phi-4-mini": "microsoft/Phi-4-mini-instruct",  # Microsoft: large multilingual vocabulary
}
# OpenAI's encodings, served by tiktoken. cl100k_base is GPT-4, o200k_base is GPT-4o and later.
TIKTOKEN_ENCODINGS = {
    "gpt-4": "cl100k_base",
    "gpt-4o": "o200k_base",
}
ALL = [*HF_TOKENIZERS, *TIKTOKEN_ENCODINGS]


@dataclass(frozen=True)
class Tokens:
    tokenizer: str
    vocab_size: int
    ids: list[int]
    # pieces[i] is the slice of the original text that ids[i] covers. Joined, they give the text
    # back. A piece is "" when its token holds only some of the bytes of a character (an emoji
    # is 4 bytes and can be split over several tokens). The character is shown on the token that
    # completes it, the same rule for both libraries.
    pieces: list[str]

    @property
    def count(self) -> int:
        return len(self.ids)


def tokenize(name: str, text: str) -> Tokens:
    if name in HF_TOKENIZERS:
        return _tokenize_hf(name, text)
    if name in TIKTOKEN_ENCODINGS:
        return _tokenize_tiktoken(name, text)
    raise KeyError(f"Unknown tokenizer {name!r}. Choose from: {', '.join(ALL)}")


# @cache keeps each tokenizer in memory after the first load, so the Streamlit page in part C
# doesn't reload it on every keystroke.
@cache
def _hf(name: str):
    return AutoTokenizer.from_pretrained(HF_TOKENIZERS[name])


@cache
def _tiktoken(name: str) -> tiktoken.Encoding:
    return tiktoken.get_encoding(TIKTOKEN_ENCODINGS[name])


def _tokenize_hf(name: str, text: str) -> Tokens:
    tok = _hf(name)
    # add_special_tokens=False: count only the text itself, no hidden start of text marker.
    # return_offsets_mapping=True: a (start, end) character span for every token.
    # split_special_tokens=True: text like "<|endoftext|>" stays ordinary text, not a control
    # token, matching the tiktoken adapter below. Typed text should never act as a control token.
    enc = tok(
        text, add_special_tokens=False, return_offsets_mapping=True, split_special_tokens=True
    )
    spans = enc["offset_mapping"]
    pieces = []
    covered = 0  # end of the text already shown
    for i, (_, end) in enumerate(spans):
        # Tokens that split one character all report that character's full span. Stop each
        # piece where the next token starts, so a token whose character carries on into the next
        # token shows nothing, and the character appears on the token that completes it. That is
        # the rule tiktoken's offsets follow, so both libraries display a split the same way.
        next_start = spans[i + 1][0] if i + 1 < len(spans) else len(text)
        stop = max(covered, min(end, next_start))
        pieces.append(text[covered:stop])
        covered = stop
    return Tokens(name, len(tok), enc["input_ids"], pieces)


def _tokenize_tiktoken(name: str, text: str) -> Tokens:
    enc = _tiktoken(name)
    # disallowed_special=(): treat text like "<|endoftext|>" as ordinary text, not a control token.
    ids = enc.encode(text, disallowed_special=())
    # tiktoken gives only where each token starts. Each token ends where the next one starts.
    _, starts = enc.decode_with_offsets(ids)
    ends = [*starts[1:], len(text)]
    pieces = [text[start:end] for start, end in zip(starts, ends, strict=True)]
    return Tokens(name, enc.n_vocab, ids, pieces)
