---
license: mit
sdk: static
colorFrom: blue
colorTo: red
tags:
  - youtube
  - transcript
  - api
  - fetch
  - clean
  - summarize
  - python
  - tools

---

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white)
![Anthropic](https://img.shields.io/badge/Powered%20by-Anthropic%20Claude-blueviolet?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![No Scraping](https://img.shields.io/badge/No%20Scraping-Direct%20API-brightgreen?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)
![Author](https://img.shields.io/badge/Author-algorembrant-orange?style=flat-square)

---

# YouTube Transcript Toolkit

A fast, zero-scraping command-line toolkit that fetches YouTube transcripts
directly via the caption API, then uses the Anthropic Claude API to reformat
them into clean paragraphs and produce multi-mode summaries.

No Selenium. No BeautifulSoup. No headless browsers. Two AI-powered
post-processing features built on top of direct caption API access.

---

## Architecture

```
main.py          CLI entry point — five commands (fetch, list, clean, summarize, pipeline)
fetcher.py       Direct YouTube caption API — no HTML parsing
cleaner.py       AI paragraph reformatter (Anthropic Claude)
summarizer.py    AI summarizer with 4 output modes (Anthropic Claude)
pipeline.py      Orchestrates fetch -> clean -> summarize in one pass
ai_client.py     Shared Anthropic API wrapper with chunking and streaming
config.py        Model names, limits, summary modes, defaults
```

---

## Features

- Direct caption API — transcript fetch is near-instant regardless of video length
- Paragraph Cleaner — reformats fragmented auto-captions into readable prose (no content removed)
- Summarizer — four modes: brief, detailed, bullet points, hierarchical outline
- Full pipeline — fetch + clean + summarize in a single command
- Token streaming — see AI output in real time as it generates
- Automatic chunking — handles transcripts of any length by splitting and merging
- Fast model by default (claude-haiku), quality model available via --quality flag
- Batch processing — multiple video IDs/URLs in one command
- Output formats — plain text, JSON, SRT, WebVTT for the raw transcript

---

## Installation

```bash
git clone https://github.com/algorembrant/youtube-transcript-toolkit.git
cd youtube-transcript-toolkit
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."   # Windows: set ANTHROPIC_API_KEY=sk-ant-...
```

---

## Commands

### fetch — raw transcript only (no AI)

```bash
python main.py fetch "https://www.youtube.com/watch?v=VIDEO_ID"
python main.py fetch VIDEO_ID -f srt -o transcript.srt
python main.py fetch VIDEO_ID -f json -o transcript.json
python main.py fetch VIDEO_ID -t                          # with timestamps
python main.py fetch VIDEO_ID -l es en                   # Spanish, fall back to English
```

### list — available languages

```bash
python main.py list VIDEO_ID
```

### clean — reformat into paragraphs

```bash
python main.py clean VIDEO_ID
python main.py clean VIDEO_ID -o cleaned.txt
python main.py clean VIDEO_ID --quality                  # use higher-quality model
python main.py clean VIDEO_ID --no-stream                # disable live token output
```

### summarize — AI-generated summary

```bash
python main.py summarize VIDEO_ID                        # brief (default)
python main.py summarize VIDEO_ID -m detailed
python main.py summarize VIDEO_ID -m bullets
python main.py summarize VIDEO_ID -m outline
python main.py summarize VIDEO_ID -m detailed --quality -o summary.txt
```

### pipeline — fetch + clean + summarize

```bash
python main.py pipeline VIDEO_ID
python main.py pipeline VIDEO_ID -m bullets -o ./output/
python main.py pipeline VIDEO_ID --skip-clean            # fetch + summarize only
python main.py pipeline VIDEO_ID --skip-summary          # fetch + clean only
python main.py pipeline ID1 ID2 ID3 -o ./batch/          # batch
```

---

## Summary Modes

| Mode       | Description                                      |
|------------|--------------------------------------------------|
| `brief`    | 3-5 sentence executive summary                   |
| `detailed` | Multi-section prose: Overview, Key Points, etc.  |
| `bullets`  | Key takeaways grouped under bold thematic headers|
| `outline`  | Hierarchical Roman-numeral topic outline         |

---

## Model Selection

| Flag        | Model Used                  | Best For                          |
|-------------|-----------------------------|------------------------------------|
| (default)   | claude-haiku-4-5            | Speed, short-to-medium transcripts |
| `--quality` | claude-sonnet-4-6           | Long transcripts, deep summaries   |

---

## CLI Reference

```
usage: main.py {fetch,list,clean,summarize,pipeline} [options] video [video ...]

commands:
  fetch       Fetch raw transcript (no AI)
  list        List available transcript languages
  clean       Fetch + AI paragraph formatting
  summarize   Fetch + AI summarization
  pipeline    Fetch + clean + summarize in one pass

shared options:
  -l, --languages LANG [LANG ...]    Language codes, in order of preference
  -o, --output PATH                  Output file (single) or directory (batch)
  --quality                          Use higher-quality Claude model
  --no-stream                        Disable live token streaming

fetch / pipeline options:
  -f, --format {text,json,srt,vtt}   Raw transcript format (default: text)
  -t, --timestamps                   Add timestamps to plain-text output

clean / summarize / pipeline options:
  -m, --mode {brief,detailed,bullets,outline}   Summary mode (default: brief)

pipeline options:
  --skip-clean     Skip paragraph cleaning step
  --skip-summary   Skip summarization step
```

---

## Output Files (pipeline with -o)

When using `pipeline -o ./output/`, three files are saved per video:

```
./output/
  VIDEO_ID_transcript.txt    Raw transcript
  VIDEO_ID_cleaned.txt       Paragraph-cleaned transcript
  VIDEO_ID_summary.txt       Summary
```

---

## Chunking Strategy

Transcripts larger than 60,000 characters are automatically split into chunks
at paragraph or sentence boundaries. Each chunk is processed independently,
then the partial results are merged in a final synthesis pass. This allows
the toolkit to handle full-length lecture recordings, long-form interviews,
and documentary transcripts without hitting token limits.

---

## Supported URL Formats

```
https://www.youtube.com/watch?v=VIDEO_ID
https://youtu.be/VIDEO_ID
https://www.youtube.com/shorts/VIDEO_ID
https://www.youtube.com/embed/VIDEO_ID
VIDEO_ID  (raw 11-character ID)
```

---

## Error Reference

| Error                   | Cause                                            |
|-------------------------|--------------------------------------------------|
| `TranscriptsDisabled`   | Video owner has disabled captions                |
| `VideoUnavailable`      | Video is private, deleted, or region-locked      |
| `NoTranscriptFound`     | Requested language does not exist                |
| `NoTranscriptAvailable` | No captions of any kind exist for this video     |
| `AuthenticationError`   | ANTHROPIC_API_KEY is missing or invalid          |

---

## Dependencies

| Package                | Version    | Purpose                              |
|------------------------|------------|--------------------------------------|
| anthropic              | >=0.40.0   | Claude API (clean + summarize)       |
| youtube-transcript-api | 0.6.2      | Direct YouTube caption API access    |

---

## License

MIT License. See `LICENSE` for details.

---

## Disclaimer

This tool uses YouTube's publicly accessible caption endpoint and the Anthropic
API for personal, educational, and research use. An Anthropic API key is required
for the clean and summarize features. Review YouTube's Terms of Service before
using this tool in a production or commercial context.
