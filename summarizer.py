"""
summarizer.py
Summarizes YouTube transcript text in multiple modes via the Anthropic API.
Author: algorembrant
"""

from __future__ import annotations

from config import DEFAULT_MODEL, MAX_TOKENS, QUALITY_MODEL
from ai_client import complete_long

# ---------------------------------------------------------------------------
# Per-mode prompts
# ---------------------------------------------------------------------------

_SYSTEM_BASE = """You are an expert content analyst specializing in video transcripts.
Your summaries are accurate, concise, and written in clear professional prose.
Never hallucinate or add information not present in the transcript.
Do not add a preamble or closing statement — output only the requested summary.
"""

_MODE_PROMPTS: dict[str, dict[str, str]] = {

    "brief": {
        "system": _SYSTEM_BASE + (
            "Write a brief 3-5 sentence executive summary that captures the core message, "
            "key argument, and main conclusion of the transcript."
        ),
        "user_prefix": (
            "Write a brief 3-5 sentence executive summary of the following transcript.\n\n"
            "TRANSCRIPT:"
        ),
    },

    "detailed": {
        "system": _SYSTEM_BASE + (
            "Write a detailed, multi-section summary with clearly labeled sections. "
            "Sections should include: Overview, Key Points, Supporting Details, and Conclusion. "
            "Each section should be written as flowing prose paragraphs — no bullet points."
        ),
        "user_prefix": (
            "Write a detailed multi-section summary (Overview, Key Points, Supporting Details, Conclusion) "
            "of the following transcript. Use flowing prose — no bullet points.\n\n"
            "TRANSCRIPT:"
        ),
    },

    "bullets": {
        "system": _SYSTEM_BASE + (
            "Extract the most important takeaways as a structured bullet list. "
            "Group bullets under 3-5 thematic headings. Each bullet should be one clear sentence. "
            "Use markdown bold for headings."
        ),
        "user_prefix": (
            "Extract the key takeaways from the following transcript as a structured bullet list "
            "grouped under bold thematic headings.\n\n"
            "TRANSCRIPT:"
        ),
    },

    "outline": {
        "system": _SYSTEM_BASE + (
            "Create a hierarchical topic outline of the transcript. "
            "Use Roman numerals for top-level topics, capital letters for sub-topics, "
            "and Arabic numerals for specific points. Keep entries concise (one line each)."
        ),
        "user_prefix": (
            "Create a hierarchical outline (Roman numerals, sub-letters, sub-numbers) "
            "of the following transcript.\n\n"
            "TRANSCRIPT:"
        ),
    },
}

_MERGE_SYSTEM = """You are an expert content analyst.
You will receive several summary sections from different parts of a long transcript.
Merge them into a single cohesive, unified summary in the same format.
Remove duplicate points. Maintain a logical flow. Output only the final merged summary.
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def summarize(
    text: str,
    mode: str = "brief",
    model: str = DEFAULT_MODEL,
    max_tokens: int = MAX_TOKENS,
    stream: bool = True,
) -> str:
    """
    Summarize a transcript in the specified mode.

    Args:
        text:       Transcript text (raw or already cleaned).
        mode:       One of 'brief', 'detailed', 'bullets', 'outline'.
        model:      Anthropic model to use.
        max_tokens: Max output tokens per API call.
        stream:     Stream progress tokens to stderr.

    Returns:
        Formatted summary string.
    """
    if not text or not text.strip():
        raise ValueError("Cannot summarize an empty transcript.")

    if mode not in _MODE_PROMPTS:
        valid = ", ".join(_MODE_PROMPTS.keys())
        raise ValueError(f"Unknown summary mode: {mode!r}. Valid modes: {valid}")

    prompts = _MODE_PROMPTS[mode]

    # Detailed and outline summaries benefit from higher-quality model
    # but we keep the user's choice; they can override via --quality flag
    return complete_long(
        system=prompts["system"],
        user_prefix=prompts["user_prefix"],
        text=text.strip(),
        model=model,
        max_tokens=max_tokens,
        merge_system=_MERGE_SYSTEM,
        stream=stream,
    )
