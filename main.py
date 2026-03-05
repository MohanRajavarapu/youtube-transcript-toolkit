#!/usr/bin/env python3
"""
main.py
YouTube Transcript Toolkit — CLI entry point.

Commands:
  fetch       Fetch and print/save raw transcript
  clean       Fetch transcript and reformat into paragraphs
  summarize   Fetch transcript and summarize
  pipeline    Fetch, clean, and summarize in one pass
  list        List available transcript languages for a video

Author: algorembrant
"""

from __future__ import annotations

import argparse
import sys

from config import DEFAULT_MODEL, QUALITY_MODEL, SUMMARY_MODES, OUTPUT_FORMATS
from fetcher import extract_video_id, list_available_transcripts, fetch
from cleaner import clean
from summarizer import summarize
from pipeline import run, run_batch


# ---------------------------------------------------------------------------
# Shared argument groups
# ---------------------------------------------------------------------------

def _add_video_args(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "video",
        nargs="+",
        help="YouTube video URL(s) or ID(s).",
    )

def _add_lang_args(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "-l", "--languages",
        nargs="+",
        default=["en"],
        metavar="LANG",
        help="Language codes in order of preference (default: en). Example: --languages en es",
    )

def _add_output_args(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "-o", "--output",
        metavar="PATH",
        help="Output file (single video) or directory (multiple videos).",
    )

def _add_ai_args(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--quality",
        action="store_true",
        help=f"Use the higher-quality model ({QUALITY_MODEL}) instead of the default fast model.",
    )
    p.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable token streaming (collect full response before printing).",
    )

def _add_format_args(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "-f", "--format",
        choices=OUTPUT_FORMATS,
        default="text",
        help="Raw transcript output format (default: text).",
    )
    p.add_argument(
        "-t", "--timestamps",
        action="store_true",
        help="Include timestamps in plain-text transcript output.",
    )


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="yttool",
        description=(
            "YouTube Transcript Toolkit\n"
            "Fetch, clean, and summarize YouTube transcripts. No HTML parsing.\n"
            "Author: algorembrant"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---- fetch ----
    p_fetch = subparsers.add_parser(
        "fetch",
        help="Fetch the raw transcript of a YouTube video.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    _add_video_args(p_fetch)
    _add_lang_args(p_fetch)
    _add_format_args(p_fetch)
    _add_output_args(p_fetch)

    # ---- list ----
    p_list = subparsers.add_parser(
        "list",
        help="List all available transcript languages for a video.",
    )
    _add_video_args(p_list)

    # ---- clean ----
    p_clean = subparsers.add_parser(
        "clean",
        help="Fetch a transcript and reformat it into clean paragraphs.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    _add_video_args(p_clean)
    _add_lang_args(p_clean)
    _add_ai_args(p_clean)
    _add_output_args(p_clean)

    # ---- summarize ----
    p_sum = subparsers.add_parser(
        "summarize",
        help="Fetch a transcript and summarize it.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    _add_video_args(p_sum)
    _add_lang_args(p_sum)
    p_sum.add_argument(
        "-m", "--mode",
        choices=list(SUMMARY_MODES.keys()),
        default="brief",
        help=(
            "Summary mode (default: brief):\n"
            + "\n".join(
                f"  {k:10s} {v['description']}"
                for k, v in SUMMARY_MODES.items()
            )
        ),
    )
    _add_ai_args(p_sum)
    _add_output_args(p_sum)

    # ---- pipeline ----
    p_pipe = subparsers.add_parser(
        "pipeline",
        help="Fetch, clean, and summarize in one pass.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    _add_video_args(p_pipe)
    _add_lang_args(p_pipe)
    _add_format_args(p_pipe)
    p_pipe.add_argument(
        "-m", "--mode",
        choices=list(SUMMARY_MODES.keys()),
        default="brief",
        help="Summary mode (default: brief).",
    )
    p_pipe.add_argument(
        "--skip-clean",
        action="store_true",
        help="Skip the cleaning step; summarize raw transcript directly.",
    )
    p_pipe.add_argument(
        "--skip-summary",
        action="store_true",
        help="Skip the summarization step; only fetch and clean.",
    )
    _add_ai_args(p_pipe)
    _add_output_args(p_pipe)

    return parser


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def cmd_list(args: argparse.Namespace) -> None:
    for v in args.video:
        vid = extract_video_id(v)
        list_available_transcripts(vid)


def cmd_fetch(args: argparse.Namespace) -> None:
    import os

    video_ids = [extract_video_id(v) for v in args.video]
    single    = len(video_ids) == 1

    for vid in video_ids:
        result = fetch(vid, languages=args.languages)
        text   = result.formatted(args.format, timestamps=args.timestamps)

        if args.output:
            if single:
                out_path = args.output
            else:
                ext_map = {"text": "txt", "json": "json", "srt": "srt", "vtt": "vtt"}
                os.makedirs(args.output, exist_ok=True)
                out_path = os.path.join(args.output, f"{vid}.{ext_map.get(args.format, 'txt')}")

            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"[saved] {out_path}", file=sys.stderr)
        else:
            if not single:
                print(f"\n{'='*60}\nVideo: {vid}\n{'='*60}")
            print(text)


def cmd_clean(args: argparse.Namespace) -> None:
    import os

    video_ids = [extract_video_id(v) for v in args.video]
    single    = len(video_ids) == 1
    model     = QUALITY_MODEL if args.quality else DEFAULT_MODEL
    stream    = not args.no_stream

    for vid in video_ids:
        result   = fetch(vid, languages=args.languages)
        cleaned  = clean(result.plain_text, model=model, stream=stream)

        if args.output:
            if single:
                out_path = args.output
            else:
                os.makedirs(args.output, exist_ok=True)
                out_path = os.path.join(args.output, f"{vid}_cleaned.txt")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(cleaned)
            print(f"\n[saved] {out_path}", file=sys.stderr)
        else:
            if not single:
                print(f"\n{'='*60}\nVideo: {vid}\n{'='*60}")
            print(cleaned)


def cmd_summarize(args: argparse.Namespace) -> None:
    import os

    video_ids = [extract_video_id(v) for v in args.video]
    single    = len(video_ids) == 1
    model     = QUALITY_MODEL if args.quality else DEFAULT_MODEL
    stream    = not args.no_stream

    for vid in video_ids:
        result  = fetch(vid, languages=args.languages)
        summary = summarize(result.plain_text, mode=args.mode, model=model, stream=stream)

        if args.output:
            if single:
                out_path = args.output
            else:
                os.makedirs(args.output, exist_ok=True)
                out_path = os.path.join(args.output, f"{vid}_summary.txt")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(summary)
            print(f"\n[saved] {out_path}", file=sys.stderr)
        else:
            if not single:
                print(f"\n{'='*60}\nVideo: {vid}\n{'='*60}")
            print(summary)


def cmd_pipeline(args: argparse.Namespace) -> None:
    video_ids = [extract_video_id(v) for v in args.video]
    model     = QUALITY_MODEL if args.quality else DEFAULT_MODEL
    stream    = not args.no_stream

    kwargs = dict(
        languages         = args.languages,
        do_clean          = not args.skip_clean,
        do_summarize      = not args.skip_summary,
        summary_mode      = args.mode,
        model             = model,
        quality           = args.quality,
        stream            = stream,
        output_dir        = args.output,
        transcript_format = args.format,
        timestamps        = args.timestamps,
    )

    if len(video_ids) == 1:
        r = run(video_ids[0], **kwargs)
        if not args.output:
            _print_pipeline_result(r)
    else:
        results = run_batch(video_ids, **kwargs)
        if not args.output:
            for r in results:
                print(f"\n{'='*60}\nVideo: {r.video_id}\n{'='*60}")
                _print_pipeline_result(r)

    # Report errors
    all_errors = []
    if isinstance(r if len(video_ids) == 1 else None, object):
        pass  # handled per-result below


def _print_pipeline_result(r) -> None:
    sections = []
    if r.raw:
        sections.append(("RAW TRANSCRIPT", r.raw))
    if r.cleaned:
        sections.append(("CLEANED TRANSCRIPT", r.cleaned))
    if r.summary:
        sections.append(("SUMMARY", r.summary))

    for title, content in sections:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
        print(content)

    if r.errors:
        print(f"\n[errors]", file=sys.stderr)
        for err in r.errors:
            print(f"  {err}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    dispatch = {
        "list":      cmd_list,
        "fetch":     cmd_fetch,
        "clean":     cmd_clean,
        "summarize": cmd_summarize,
        "pipeline":  cmd_pipeline,
    }

    handler = dispatch.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()