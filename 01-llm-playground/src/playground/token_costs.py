"""Step 2: what each tokenizer charges for each kind of text.

Two measures per (tokenizer, text):
  tokens           what you pay for, and what fills the context window
  tokens per char  tokens divided by characters, so short and long texts compare fairly.
                   Lower is cheaper. English prose is usually around 0.2 to 0.25.

`language_penalty` answers the Step 2 question directly: how many times more tokens the
Portuguese paragraph costs than the English one, which says the same thing.
"""

from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass

# Any function that turns (tokenizer name, text) into a token count. The real one wraps
# playground.tokenizers.tokenize; tests pass a fake, so they need no downloads.
Counter = Callable[[str, str], int]


@dataclass(frozen=True)
class Cost:
    tokenizer: str
    sample: str
    characters: int
    tokens: int

    @property
    def tokens_per_char(self) -> float:
        return self.tokens / self.characters if self.characters else 0.0

    def as_dict(self) -> dict:
        return {**asdict(self), "tokens_per_char": round(self.tokens_per_char, 4)}


def measure(tokenizers: list[str], samples: Mapping[str, str], count: Counter) -> list[Cost]:
    """One Cost for every tokenizer and sample, tokenizers in the outer loop."""
    return [
        Cost(name, label, len(text), count(name, text))
        for name in tokenizers
        for label, text in samples.items()
    ]


def language_penalty(costs: list[Cost], base: str = "english", other: str = "portuguese") -> dict:
    """Tokenizer -> tokens(other) / tokens(base). 1.0 means no penalty; 1.5 means 50% more."""
    by = {(c.tokenizer, c.sample): c.tokens for c in costs}
    names = dict.fromkeys(c.tokenizer for c in costs)  # keeps first-seen order
    return {n: round(by[n, other] / by[n, base], 3) for n in names if by.get((n, base))}
