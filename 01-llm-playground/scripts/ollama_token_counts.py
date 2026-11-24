"""Step 2 part B: how many tokens each local Ollama model sees for the same text.

Run with:  uv run python scripts/ollama_token_counts.py

Ollama has no "tokenize" command, but every reply reports prompt_eval_count: how many prompt
tokens the model read. Asking twice per text gives two numbers:
  text only   the text exactly as typed (raw=True skips the chat template)
  with chat   the text wrapped in the model's chat template, as `ollama run` sends it
The difference is what the template adds. The six tokenizers from part A are printed above
the models, so you can see which one each Ollama model matches.

Every request starts from a freshly loaded model. Part C of step 1 showed Ollama reusing
cached prompt tokens, and a reused token is not counted, which would shrink the numbers.
"""

import sys

from ollama import Client, ResponseError

from playground.ollama_client import STEP1_MODELS, Timing, get_client, unload
from playground.tokenizers import ALL, tokenize

TEXTS = [
    "Explain what a token is in two sentences.",  # the step 1 prompt
    "1234567 2345678 1000000 9876543",  # the numbers from part A
    "O gato dorme no sofá enquanto chove lá fora.",  # Portuguese: the cat sleeps while it rains
]
# A 1 token reply: we only want the prompt count. Temperature 0 keeps it repeatable.
ONE_TOKEN = {"temperature": 0, "seed": 0, "num_predict": 1}


def count(client: Client, model: str, text: str, raw: bool) -> int:
    unload(client, model)  # empty the prompt cache
    t = Timing.from_response(client.generate(model=model, prompt=text, raw=raw, options=ONE_TOKEN))
    if t.load_s < 0.1:
        # A real load takes seconds. Near zero means the model was still warm, so part of the
        # prompt may have come from the cache and the count may be too low.
        print(f"  warning: {model} was not reloaded, its count may be low")
    return t.prompt_tokens


def main(models: list[str]) -> None:
    client = get_client()
    try:
        client.ps()
    except ConnectionError:
        sys.exit("Can't reach Ollama. Is `ollama serve` running?")

    # counts[model][text] = (text only, with chat)
    counts: dict[str, dict[str, tuple[int, int]]] = {}
    for model in models:
        print(f"Counting with {model} (one reload per request, about a minute) ...", flush=True)
        try:
            counts[model] = {
                text: (count(client, model, text, raw=True), count(client, model, text, raw=False))
                for text in TEXTS
            }
        except ResponseError as e:
            print(f"  skipped {model}: {e.error}")

    for text in TEXTS:
        print(f'\n"{text}" ({len(text)} characters)\n')
        print("| Tokenizer or model | Text only | With chat template | Template adds |")
        print("|---|---|---|---|")
        for name in ALL:
            print(f"| {name} (part A) | {tokenize(name, text).count} | | |")
        for model, by_text in counts.items():
            bare, chat = by_text[text]
            print(f"| {model} | {bare} | {chat} | {chat - bare} |")


if __name__ == "__main__":
    main(sys.argv[1:] or STEP1_MODELS)
