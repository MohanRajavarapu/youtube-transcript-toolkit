"""
pipeline.py
Orchestrates fetch -> clean -> summarize in a single pipeline call.
Author: algorembrant
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Optional

from fetcher import TranscriptResult, fetch, extract_video_id
from cleaner import clean
from summarizer import summarize
from config import DEFAULT_MODEL, QUALITY_MODEL


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class PipelineResult:
    video_id:   str
    raw:        str          = ""
    cleaned:    str          = ""
    summary:    str          = ""
    errors:     list[str]    = field(default_factory=list)

    @property
    def success(self) -> bool:
        return not self.errors


# ---------------------------------------------------------------------------
# Single-video pipeline
# ---------------------------------------------------------------------------

def run(
    url_or_id: str,
    languages: list[str] | None     = None,
    do_clean: bool                  = False,
    do_summarize: bool              = False,
    summary_mode: str               = "brief",
    model: str                      = DEFAULT_MODEL,
    quality: bool                   = False,
    stream: bool                    = True,
    output_dir: str | None          = None,
    transcript_format: str          = "text",
    timestamps: bool                = False,
) -> PipelineResult:
    """
    Full pipeline for one video.

    Args:
        url_or_id:         YouTube URL or video ID.
        languages:         Language preference list.
        do_clean:          Run paragraph cleaner.
        do_summarize:      Run summarizer.
        summary_mode:      One of 'brief', 'detailed', 'bullets', 'outline'.
        model:             Anthropic model identifier.
        quality:           Use the higher-quality model instead of the default fast one.
        stream:            Stream AI tokens to stderr.
        output_dir:        Directory to write output files (optional).
        transcript_format: Raw transcript format: 'text', 'json', 'srt', 'vtt'.
        timestamps:        Include timestamps in plain-text transcript.

    Returns:
        PipelineResult with all produced artifacts.
    """
    chosen_model = QUALITY_MODEL if quality else model
    result       = PipelineResult(video_id="")

    # 1. Extract ID
    try:
        video_id      = extract_video_id(url_or_id)
        result.video_id = video_id
    except ValueError as exc:
        result.errors.append(str(exc))
        return result

    # 2. Fetch
    print(f"\n[fetch] {video_id}", file=sys.stderr)
    transcript: TranscriptResult = fetch(video_id, languages=languages)
    result.raw = transcript.formatted(transcript_format, timestamps=timestamps)
    plain_text  = transcript.plain_text   # always used as AI input

    # 3. Clean
    if do_clean:
        print(f"\n[clean] Running paragraph cleaner...", file=sys.stderr)
        try:
            result.cleaned = clean(plain_text, model=chosen_model, stream=stream)
        except Exception as exc:
            result.errors.append(f"Cleaner error: {exc}")

    # 4. Summarize
    if do_summarize:
        print(f"\n[summarize] Mode: {summary_mode}", file=sys.stderr)
        # Prefer cleaned text if available
        source_text = result.cleaned if result.cleaned else plain_text
        try:
            result.summary = summarize(
                source_text, mode=summary_mode, model=chosen_model, stream=stream
            )
        except Exception as exc:
            result.errors.append(f"Summarizer error: {exc}")

    # 5. Save to disk
    if output_dir:
        _save(result, output_dir, transcript_format)

    return result


def _save(result: PipelineResult, output_dir: str, fmt: str) -> None:
    """Write all non-empty artifacts to output_dir."""
    os.makedirs(output_dir, exist_ok=True)
    vid = result.video_id

    ext_map = {"text": "txt", "json": "json", "srt": "srt", "vtt": "vtt"}
    ext = ext_map.get(fmt, "txt")

    files_written = []

    if result.raw:
        p = os.path.join(output_dir, f"{vid}_transcript.{ext}")
        _write(p, result.raw)
        files_written.append(p)

    if result.cleaned:
        p = os.path.join(output_dir, f"{vid}_cleaned.txt")
        _write(p, result.cleaned)
        files_written.append(p)

    if result.summary:
        p = os.path.join(output_dir, f"{vid}_summary.txt")
        _write(p, result.summary)
        files_written.append(p)

    for path in files_written:
        print(f"[saved] {path}", file=sys.stderr)


def _write(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# Batch pipeline
# ---------------------------------------------------------------------------

def run_batch(
    urls_or_ids: list[str],
    **kwargs,
) -> list[PipelineResult]:
    """
    Run the pipeline for multiple videos sequentially.
    All keyword arguments are forwarded to `run()`.

    Returns a list of PipelineResult, one per video.
    """
    results = []
    total   = len(urls_or_ids)
    for i, url_or_id in enumerate(urls_or_ids, 1):
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"[{i}/{total}] Processing: {url_or_id}", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        r = run(url_or_id, **kwargs)
        results.append(r)
    return results
