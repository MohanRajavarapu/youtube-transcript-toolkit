"""
cleaner.py
Reformats raw YouTube transcript text into clean, readable paragraphs.
Author: algorembrant
"""

from __future__ import annotations

from config import DEFAULT_MODEL, MAX_TOKENS
from ai_client import complete_long

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

_CLEAN_SYSTEM = """You are a professional transcript editor.
Your task is to reformat raw, fragmented YouTube transcript text into clean,
readable paragraphs that preserve the speaker's words and intent exactly.

Rules:
- Do NOT paraphrase, summarize, or omit any content.
- Fix only punctuation, capitalization, and paragraph breaks.
- Group related sentences into coherent paragraphs of 3-6 sentences each.
- Remove filler words only when they impede readability (e.g. repeated "um", "uh", "like").
- Remove duplicate lines caused by auto-captioning overlap.
- Preserve proper nouns, technical terms, and speaker style.
- Output clean, flowing prose — no bullet points, no headers, no markdown.
- Do not add any commentary, preamble, or notes of your own.
"""

_CLEAN_USER_PREFIX = (
    "Reformat the following raw YouTube transcript into clean, readable paragraphs. "
    "Preserve all content. Fix punctuation and capitalization only.\n\n"
    "RAW TRANSCRIPT:"
)

_CLEAN_MERGE_SYSTEM = """You are a professional transcript editor.
You will receive several already-cleaned transcript sections.
Merge them into a single, seamless, well-paragraphed document.
Do not summarize or omit any content. Output clean flowing prose only.
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def clean(
    raw_text: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = MAX_TOKENS,
    stream: bool = True,
) -> str:
    """
    Reformat a raw transcript into clean paragraphs.

    Args:
        raw_text:   Plain-text transcript (output of fetcher.TranscriptResult.plain_text).
        model:      Anthropic model to use.
        max_tokens: Max output tokens per API call.
        stream:     Whether to stream progress tokens to stderr.

    Returns:
        Cleaned, paragraph-formatted transcript as a string.
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("Cannot clean an empty transcript.")

    return complete_long(
        system=_CLEAN_SYSTEM,
        user_prefix=_CLEAN_USER_PREFIX,
        text=raw_text.strip(),
        model=model,
        max_tokens=max_tokens,
        merge_system=_CLEAN_MERGE_SYSTEM,
        stream=stream,
    )