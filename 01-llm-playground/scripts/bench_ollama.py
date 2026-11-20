"""Step 1 benchmark: measure every local Ollama model the same way.

Run with:  uv run python scripts/bench_ollama.py [model ...]
           (no models given = the four from step 1)

For each model it measures:
  1. cold load  unload the model, then ask for a 1 token reply and read load_duration
  2. warm load  ask again straight away, while the model is still in memory
  3. prefill    a long prompt (about 1,500 tokens) with a 1 token reply: prompt eval rate
  4. decode     a fixed 200 token reply at temperature 0: eval rate
  5. memory     the model's size in `ollama ps`, weights plus KV cache
Prefill and decode run three times and report the median. Prints a markdown table.
"""

import statistics
import sys
import uuid
from dataclasses import dataclass

from ollama import Client, ResponseError

from playground.ollama_client import STEP1_MODELS, Timing, get_client, same_model, unload

RUNS = 3
DECODE_TOKENS = 200

# Temperature 0 and a fixed seed make runs repeatable. num_predict caps the reply length so
# every model writes the same number of tokens. Never set num_ctx here: a context size that
# differs from the loaded one makes Ollama reload the model, and the reload lands in the timing.
ONE_TOKEN = {"temperature": 0, "seed": 0, "num_predict": 1}
DECODE = {"temperature": 0, "seed": 0, "num_predict": DECODE_TOKENS}

DECODE_PROMPT = (
    "Write a long, detailed story about a lighthouse keeper who finds a message in a bottle."
)
PARAGRAPH = (
    "The harbour town woke slowly. Fishing boats left before dawn, gulls followed them out past "
    "the breakwater, and the bakery on the corner opened its shutters as the first light reached "
    "the hills. By mid morning the market was full of voices, crates of fish, baskets of bread "
    "and the smell of coffee drifting from the cafe by the water. "
)
LONG_PROMPT = PARAGRAPH * 20 + "\nSummarise the text above in one word."


def fresh(prompt: str) -> str:
    """Put a random tag at the start so Ollama's prompt cache can't reuse an earlier run.

    You saw the cache in part C: "prompt eval cached: 30 token(s)". A cached prompt is barely
    computed at all, so its prefill rate would be meaningless.
    """
    return f"[run {uuid.uuid4().hex[:8]}] {prompt}"


def ask(client: Client, model: str, prompt: str, options: dict) -> Timing:
    return Timing.from_response(client.generate(model=model, prompt=prompt, options=options))


@dataclass(frozen=True)
class Result:
    model: str
    cold_load_s: float
    warm_load_s: float
    prefill_tokens: int
    prefill_tps: float
    decode_tokens: int
    decode_tps: float
    memory_gib: float
    context: int


def bench(client: Client, model: str) -> Result:
    unload(client, model)
    cold = ask(client, model, fresh("Say hi."), ONE_TOKEN)
    warm = ask(client, model, fresh("Say hi."), ONE_TOKEN)
    prefill = [ask(client, model, fresh(LONG_PROMPT), ONE_TOKEN) for _ in range(RUNS)]
    decode = [ask(client, model, DECODE_PROMPT, DECODE) for _ in range(RUNS)]

    loaded = next(m for m in client.ps().models if same_model(m.model, model))
    return Result(
        model=model,
        cold_load_s=cold.load_s,
        warm_load_s=warm.load_s,
        prefill_tokens=prefill[0].prompt_tokens,
        prefill_tps=statistics.median(t.prefill_tps for t in prefill),
        decode_tokens=min(t.output_tokens for t in decode),
        decode_tps=statistics.median(t.decode_tps for t in decode),
        memory_gib=(loaded.size or 0) / 2**30,
        context=loaded.context_length or 0,
    )


def print_table(results: list[Result]) -> None:
    print("\n| Model | Cold load | Warm load | Prefill | Decode | Memory |")
    print("|---|---|---|---|---|---|")
    for r in results:
        print(
            f"| {r.model} | {r.cold_load_s:.2f} s | {r.warm_load_s * 1000:.0f} ms "
            f"| {r.prefill_tps:,.0f} tok/s ({r.prefill_tokens:,} tok) "
            f"| {r.decode_tps:.1f} tok/s ({r.decode_tokens} tok) "
            f"| {r.memory_gib:.1f} GiB at {r.context // 1024}k context |"
        )


def main(models: list[str]) -> None:
    client = get_client()
    try:
        client.ps()
    except ConnectionError:
        sys.exit("Can't reach Ollama. Is `ollama serve` running?")

    results = []
    for model in models:
        print(f"Benchmarking {model} ...", flush=True)
        try:
            results.append(bench(client, model))
        except ResponseError as e:
            print(f"  skipped {model}: {e.error}")
    print_table(results)


if __name__ == "__main__":
    main(sys.argv[1:] or STEP1_MODELS)
