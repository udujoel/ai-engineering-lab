"""Step 2, part A: show how six tokenizers split the same text.

Run with:  uv run python scripts/tokenize_text.py ["any text you like"]
           (no text given = the Step 1 prompt)

Pieces are separated by |. A dot (·) is a space, ↵ is a new line, and ▯ is a token that holds
only part of a character (its bytes are finished by a neighbouring token).
"""

import sys

from playground.tokenizers import ALL, tokenize

DEFAULT_TEXT = "Explain what a token is in two sentences."


def show(piece: str) -> str:
    return piece.replace(" ", "·").replace("\n", "↵") if piece else "▯"


def main(text: str) -> None:
    print(f"Text: {text!r}  ({len(text)} characters, {len(text.split())} words)\n")
    for name in ALL:
        t = tokenize(name, text)
        print(f"{name}  (vocabulary {t.vocab_size:,})  {t.count} tokens")
        print("  pieces: " + " | ".join(show(p) for p in t.pieces))
        print(f"  ids:    {t.ids}\n")


if __name__ == "__main__":
    main(" ".join(sys.argv[1:]) or DEFAULT_TEXT)
