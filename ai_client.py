"""
ai_client.py
Thin wrapper around the Anthropic API with chunked processing and streaming.
Author: algorembrant
"""

from __future__ import annotations

import sys
from typing import Iterator, Optional

import anthropic

from config import DEFAULT_MODEL, MAX_TOKENS, CHUNK_SIZE


# ---------------------------------------------------------------------------
# Module-level client (lazy init, reused across calls)
# ---------------------------------------------------------------------------
_client: Optional[anthropic.Anthropic] = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def complete(
    system: str,
    user: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = MAX_TOKENS,
    stream: bool = True,
) -> str:
    """
    Run a single completion and return the full response text.
    Streams tokens to stderr if `stream=True` so the user sees progress.
    """
    client = _get_client()

    if stream:
        result_parts: list[str] = []
        with client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        ) as stream_ctx:
            for text in stream_ctx.text_stream:
                print(text, end="", flush=True, file=sys.stderr)
                result_parts.append(text)
        print(file=sys.stderr)  # newline after stream
        return "".join(result_parts)
    else:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return response.content[0].text


def _split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """
    Split text into chunks of at most `chunk_size` characters,
    breaking on paragraph or sentence boundaries where possible.
    """
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunks.append(text[start:])
            break

        # Try to break at a paragraph boundary (\n\n)
        split_at = text.rfind("\n\n", start, end)
        if split_at == -1:
            # Fall back to sentence boundary
            split_at = text.rfind(". ", start, end)
        if split_at == -1:
            # Fall back to whitespace
            split_at = text.rfind(" ", start, end)
        if split_at == -1:
            split_at = end  # hard split

        chunks.append(text[start : split_at + 1])
        start = split_at + 1

    return chunks


def complete_long(
    system: str,
    user_prefix: str,
    text: str,
    user_suffix: str = "",
    model: str = DEFAULT_MODEL,
    max_tokens: int = MAX_TOKENS,
    merge_system: Optional[str] = None,
    stream: bool = True,
) -> str:
    """
    Process a potentially long text by splitting it into chunks,
    running a completion on each, then optionally merging the results.

    Args:
        system:       System prompt.
        user_prefix:  Text prepended before each chunk in the user message.
        text:         The main content to process (may be chunked).
        user_suffix:  Text appended after each chunk in the user message.
        model:        Anthropic model identifier.
        max_tokens:   Max output tokens per call.
        merge_system: If provided and there are multiple chunks, a final
                      merge pass is run with this system prompt.
        stream:       Whether to stream tokens to stderr.

    Returns:
        Final processed text (merged if multi-chunk).
    """
    chunks = _split_into_chunks(text)
    n = len(chunks)

    if n == 1:
        user_msg = f"{user_prefix}\n\n{chunks[0]}"
        if user_suffix:
            user_msg += f"\n\n{user_suffix}"
        return complete(system, user_msg, model=model, max_tokens=max_tokens, stream=stream)

    # Multi-chunk processing
    print(
        f"[info] Text is large ({len(text):,} chars). Processing in {n} chunks.",
        file=sys.stderr,
    )
    partial_results: list[str] = []
    for i, chunk in enumerate(chunks, 1):
        print(f"\n[chunk {i}/{n}]", file=sys.stderr)
        user_msg = (
            f"{user_prefix}\n\n"
            f"[Part {i} of {n}]\n\n{chunk}"
        )
        if user_suffix:
            user_msg += f"\n\n{user_suffix}"
        result = complete(system, user_msg, model=model, max_tokens=max_tokens, stream=stream)
        partial_results.append(result)

    combined = "\n\n".join(partial_results)

    # Optional merge/synthesis pass
    if merge_system and n > 1:
        print(f"\n[merging {n} chunks into final output]", file=sys.stderr)
        combined = complete(
            merge_system,
            f"Merge and unify the following {n} sections into a single cohesive output:\n\n{combined}",
            model=model,
            max_tokens=max_tokens,
            stream=stream,
        )

    return combined
