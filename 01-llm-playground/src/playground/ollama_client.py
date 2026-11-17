"""Small helpers for talking to the local Ollama server.

Ollama reports every duration in nanoseconds. These helpers turn one response into seconds
and tokens per second, so the benchmark (step 1), the chat UI (step 4) and the side by side
comparison (step 5) all measure speed the same way.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from ollama import Client, GenerateResponse

NS_PER_SECOND = 1_000_000_000
DEFAULT_HOST = "http://localhost:11434"


def get_client() -> Client:
    """A client for the server in OLLAMA_HOST (read from .env), or the default local one."""
    load_dotenv()
    return Client(host=os.getenv("OLLAMA_HOST") or DEFAULT_HOST)


def tokens_per_second(count: int, duration_ns: int) -> float:
    """Tokens divided by seconds. Returns 0.0 when nothing was timed."""
    if not count or not duration_ns:
        return 0.0
    return count / (duration_ns / NS_PER_SECOND)


@dataclass(frozen=True)
class Timing:
    """The numbers `ollama run --verbose` prints, taken from one API response."""

    load_s: float  # copying weights into GPU memory; near zero when the model is warm
    prompt_tokens: int  # your prompt plus the hidden chat template
    prefill_tps: float  # prompt eval rate: reading the prompt, all tokens at once
    output_tokens: int  # reply tokens, thinking included
    decode_tps: float  # eval rate: writing the reply, one token per pass
    total_s: float

    @classmethod
    def from_response(cls, r: GenerateResponse) -> "Timing":
        prompt_tokens = r.prompt_eval_count or 0
        output_tokens = r.eval_count or 0
        return cls(
            load_s=(r.load_duration or 0) / NS_PER_SECOND,
            prompt_tokens=prompt_tokens,
            prefill_tps=tokens_per_second(prompt_tokens, r.prompt_eval_duration or 0),
            output_tokens=output_tokens,
            decode_tps=tokens_per_second(output_tokens, r.eval_duration or 0),
            total_s=(r.total_duration or 0) / NS_PER_SECOND,
        )
