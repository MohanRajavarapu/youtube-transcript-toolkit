"""
fetcher.py
Fetches YouTube transcripts directly via the caption API — no HTML parsing.
Author: algorembrant
"""

from __future__ import annotations

import re
import sys
from typing import Optional

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import (
    JSONFormatter,
    SRTFormatter,
    TextFormatter,
    WebVTTFormatter,
)
from youtube_transcript_api._errors import (
    NoTranscriptAvailable,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

from config import DEFAULT_LANGUAGES


# ---------------------------------------------------------------------------
# URL / ID helpers
# ---------------------------------------------------------------------------

_ID_PATTERNS = [
    r"(?:youtube\.com/watch\?.*v=)([a-zA-Z0-9_-]{11})",
    r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",
    r"(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})",
    r"(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
]


def extract_video_id(url_or_id: str) -> str:
    """Return the 11-character YouTube video ID from a URL or raw ID."""
    for pattern in _ID_PATTERNS:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    if re.fullmatch(r"[a-zA-Z0-9_-]{11}", url_or_id):
        return url_or_id

    raise ValueError(
        f"Cannot extract a valid YouTube video ID from: {url_or_id!r}\n"
        "Accepted: full YouTube URL, youtu.be link, Shorts URL, embed URL, or raw 11-char ID."
    )


# ---------------------------------------------------------------------------
# Language listing
# ---------------------------------------------------------------------------

def list_available_transcripts(video_id: str) -> None:
    """Print all available transcript languages for a video."""
    tlist = YouTubeTranscriptApi.list_transcripts(video_id)

    manual = list(tlist._manually_created_transcripts.values())
    auto   = list(tlist._generated_transcripts.values())

    print(f"\nAvailable transcripts  --  video: {video_id}\n")
    if manual:
        print("Manually created:")
        for t in manual:
            print(f"  [{t.language_code:8s}] {t.language}")
    if auto:
        print("Auto-generated:")
        for t in auto:
            print(f"  [{t.language_code:8s}] {t.language}")
    if not manual and not auto:
        print("  (none found)")


# ---------------------------------------------------------------------------
# Core fetch
# ---------------------------------------------------------------------------

class TranscriptResult:
    """Container for a fetched transcript."""

    def __init__(
        self,
        video_id: str,
        raw_data: list[dict],
        language_code: str,
        language: str,
        is_generated: bool,
    ) -> None:
        self.video_id      = video_id
        self.raw_data      = raw_data          # list of {text, start, duration}
        self.language_code = language_code
        self.language      = language
        self.is_generated  = is_generated

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def plain_text(self) -> str:
        """Plain transcript text without timestamps."""
        return TextFormatter().format_transcript(self.raw_data)

    def timestamped_text(self) -> str:
        """Plain text with [MM:SS.ss] prefixes."""
        lines = []
        for entry in self.raw_data:
            m = int(entry["start"] // 60)
            s = entry["start"] % 60
            lines.append(f"[{m:02d}:{s:05.2f}] {entry['text']}")
        return "\n".join(lines)

    def as_json(self) -> str:
        return JSONFormatter().format_transcript(self.raw_data, indent=2)

    def as_srt(self) -> str:
        return SRTFormatter().format_transcript(self.raw_data)

    def as_vtt(self) -> str:
        return WebVTTFormatter().format_transcript(self.raw_data)

    def formatted(self, fmt: str, timestamps: bool = False) -> str:
        """Return transcript in the requested format string."""
        if fmt == "json":
            return self.as_json()
        if fmt == "srt":
            return self.as_srt()
        if fmt == "vtt":
            return self.as_vtt()
        # default: text
        return self.timestamped_text() if timestamps else self.plain_text

    def __len__(self) -> int:
        return len(self.plain_text)


def fetch(
    video_id: str,
    languages: Optional[list[str]] = None,
) -> TranscriptResult:
    """
    Fetch a YouTube transcript directly via the caption API.

    Args:
        video_id:  11-character YouTube video ID.
        languages: Ordered list of preferred language codes.

    Returns:
        TranscriptResult instance.

    Raises:
        SystemExit on unrecoverable errors (TranscriptsDisabled, VideoUnavailable, etc.)
    """
    if languages is None:
        languages = DEFAULT_LANGUAGES

    try:
        tlist = YouTubeTranscriptApi.list_transcripts(video_id)

        try:
            transcript_obj = tlist.find_transcript(languages)
        except NoTranscriptFound:
            all_t = (
                list(tlist._manually_created_transcripts.values())
                + list(tlist._generated_transcripts.values())
            )
            if not all_t:
                raise NoTranscriptAvailable(video_id)
            transcript_obj = all_t[0]
            print(
                f"[warn] Requested language(s) not found. "
                f"Using [{transcript_obj.language_code}] {transcript_obj.language}.",
                file=sys.stderr,
            )

        raw = transcript_obj.fetch()
        return TranscriptResult(
            video_id=video_id,
            raw_data=raw,
            language_code=transcript_obj.language_code,
            language=transcript_obj.language,
            is_generated=transcript_obj.is_generated,
        )

    except TranscriptsDisabled:
        sys.exit(f"[error] Transcripts are disabled for video '{video_id}'.")
    except VideoUnavailable:
        sys.exit(f"[error] Video '{video_id}' is unavailable (private, deleted, or region-locked).")
    except NoTranscriptAvailable:
        sys.exit(f"[error] No transcript found for video '{video_id}'.")
    except Exception as exc:
        sys.exit(f"[error] Unexpected error while fetching transcript: {exc}")