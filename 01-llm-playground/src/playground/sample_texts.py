"""Step 2: one fixed set of texts for comparing tokenizers.

The same texts are used every time, so numbers from different runs and different tokenizers
can be compared. The English and Portuguese paragraphs say the same thing, so any difference
in their token counts comes from the language, not the content.
"""

ENGLISH = (
    "The harbour town woke slowly. Fishing boats left before dawn, and the bakery on the corner "
    "opened its shutters as the first light reached the hills. By mid morning the market was "
    "full of voices, crates of fish and the smell of coffee drifting from the cafe by the water."
)

# The ENGLISH paragraph translated into European Portuguese, sentence by sentence.
PORTUGUESE = (
    "A vila do porto acordou devagar. Os barcos de pesca saíram antes do amanhecer, e a padaria "
    "da esquina abriu as portadas quando a primeira luz chegou às colinas. A meio da manhã o "
    "mercado estava cheio de vozes, caixas de peixe e o cheiro a café que vinha do café junto à "
    "água."
)

PYTHON = '''def tokens_per_second(count: int, duration_ns: int) -> float:
    """Tokens divided by seconds. Returns 0.0 when nothing was timed."""
    if not count or not duration_ns:
        return 0.0
    return count / (duration_ns / 1_000_000_000)
'''

JSON = (
    '{"model": "qwen3:4b", "created_at": "2026-11-19T22:37:05Z", "done": true, '
    '"prompt_eval_count": 24, "eval_count": 1, "options": {"temperature": 0, "seed": 0}}'
)

NUMBERS = "Order 1234567 shipped on 2026-11-20 at 14:05 for $1,299.99, a 12.5% discount."

EMOJI = "Great job 👍🏽 see you soon 🙂 🇵🇹 ❤️"

# Display name -> text. The order here is the order of rows in tables and charts.
SAMPLES = {
    "english": ENGLISH,
    "portuguese": PORTUGUESE,
    "python": PYTHON,
    "json": JSON,
    "numbers": NUMBERS,
    "emoji": EMOJI,
}
