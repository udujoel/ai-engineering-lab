"""Step 2, part B (finish): token cost of six kinds of text across six tokenizers.

Run with:  uv run python scripts/token_costs.py

Prints two tables (token counts, then tokens per character) and the Portuguese penalty, then
writes two files to results/:
  step2_token_costs.json       every number, for the Streamlit page and the portfolio site
  step2_tokens_per_char.html   a grouped bar chart; open it in a browser
"""

import json
from pathlib import Path

import altair as alt
import pandas as pd

from playground.sample_texts import SAMPLES
from playground.token_costs import language_penalty, measure
from playground.tokenizers import ALL, tokenize

RESULTS = Path(__file__).resolve().parent.parent / "results"


def count(name: str, text: str) -> int:
    return tokenize(name, text).count


def main() -> None:
    costs = measure(ALL, SAMPLES, count)
    df = pd.DataFrame([c.as_dict() for c in costs])

    print("Characters per sample:", {k: len(v) for k, v in SAMPLES.items()}, "\n")
    print("Tokens")
    print(df.pivot(index="tokenizer", columns="sample", values="tokens").loc[ALL, list(SAMPLES)])
    print("\nTokens per character (lower is cheaper)")
    tpc = df.pivot(index="tokenizer", columns="sample", values="tokens_per_char")
    print(tpc.loc[ALL, list(SAMPLES)].round(3))

    penalty = language_penalty(costs)
    print("\nPortuguese tokens / English tokens (same paragraph, 1.0 = no penalty)")
    for name, ratio in sorted(penalty.items(), key=lambda kv: kv[1]):
        print(f"  {name:<11} {ratio:.2f}")

    RESULTS.mkdir(exist_ok=True)
    data = {
        "samples": {k: {"characters": len(v), "text": v} for k, v in SAMPLES.items()},
        "costs": [c.as_dict() for c in costs],
        "portuguese_penalty": penalty,
    }
    (RESULTS / "step2_token_costs.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))

    chart = (
        alt.Chart(df, title="Tokens per character by tokenizer (lower is cheaper)")
        .mark_bar()
        .encode(
            x=alt.X("tokenizer:N", sort=ALL, title=None),
            y=alt.Y("tokens_per_char:Q", title="tokens per character"),
            color=alt.Color("tokenizer:N", sort=ALL, legend=None),
            column=alt.Column("sample:N", sort=list(SAMPLES), title=None),
            tooltip=["tokenizer", "sample", "tokens", "characters", "tokens_per_char"],
        )
        .properties(width=110, height=220)
    )
    chart.save(RESULTS / "step2_tokens_per_char.html")
    print(f"\nWrote step2_token_costs.json and step2_tokens_per_char.html to {RESULTS}")


if __name__ == "__main__":
    main()
