# Step-by-Step Setup and Usage Guide

Author: algorembrant

---

## Prerequisites

| Requirement          | Minimum Version | Notes                                      |
|----------------------|-----------------|--------------------------------------------|
| Python               | 3.8             | 3.10+ recommended                          |
| pip                  | 21.0            |                                            |
| Anthropic API Key    | --              | Required for clean and summarize commands  |

You need an Anthropic API key to use the `clean`, `summarize`, and `pipeline` commands.
Obtain one at: https://console.anthropic.com

---

## Step 1 — Get the Code

**Option A: Git clone**
```bash
git clone https://github.com/algorembrant/youtube-transcript-toolkit.git
cd youtube-transcript-toolkit
```

**Option B: Download ZIP**
Download and unzip, then open a terminal inside the project folder.

---

## Step 2 — Create a Virtual Environment

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (Command Prompt)**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

You should see `(.venv)` at the start of your terminal prompt.

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

Verify:
```bash
pip show anthropic
pip show youtube-transcript-api
```

---

## Step 4 — Set Your Anthropic API Key

**macOS / Linux (current session)**
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**macOS / Linux (permanent — add to shell profile)**
```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**Windows (Command Prompt)**
```cmd
set ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Windows (PowerShell)**
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

**Windows (permanent via System Settings)**
1. Search "Environment Variables" in Start Menu
2. Click "Edit the system environment variables"
3. Add a new variable: `ANTHROPIC_API_KEY` = your key

The `fetch` and `list` commands do NOT require an API key.
Only `clean`, `summarize`, and `pipeline` need it.

---

## Step 5 — Run Your First Commands

### Fetch a raw transcript (no API key needed)

```bash
python main.py fetch "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### See what languages are available

```bash
python main.py list dQw4w9WgXcQ
```

### Clean the transcript into paragraphs

```bash
python main.py clean dQw4w9WgXcQ
```

### Summarize the transcript

```bash
python main.py summarize dQw4w9WgXcQ -m brief
python main.py summarize dQw4w9WgXcQ -m detailed
python main.py summarize dQw4w9WgXcQ -m bullets
python main.py summarize dQw4w9WgXcQ -m outline
```

### Run the full pipeline (fetch + clean + summarize)

```bash
python main.py pipeline dQw4w9WgXcQ -m bullets
```

---

## Step 6 — Save Output to Files

### Single video — specify a file path

```bash
python main.py clean dQw4w9WgXcQ -o cleaned.txt
python main.py summarize dQw4w9WgXcQ -m detailed -o summary.txt
```

### Pipeline — specify a directory (creates 3 files per video)

```bash
python main.py pipeline dQw4w9WgXcQ -o ./output/
```

Files created:
```
./output/
  dQw4w9WgXcQ_transcript.txt
  dQw4w9WgXcQ_cleaned.txt
  dQw4w9WgXcQ_summary.txt
```

### Batch — multiple videos at once

```bash
python main.py pipeline VIDEO_ID_1 VIDEO_ID_2 VIDEO_ID_3 -o ./batch_output/
```

---

## Step 7 — Advanced Options

### Use the higher-quality model

```bash
python main.py clean dQw4w9WgXcQ --quality
python main.py summarize dQw4w9WgXcQ -m detailed --quality
```

Default model: `claude-haiku-4-5` (fast, cost-efficient)
Quality model: `claude-sonnet-4-6` (better for complex or long transcripts)

### Disable streaming (show output only after completion)

```bash
python main.py clean dQw4w9WgXcQ --no-stream
```

### Request a non-English transcript

```bash
python main.py clean dQw4w9WgXcQ -l ja       # Japanese only
python main.py clean dQw4w9WgXcQ -l es en    # Spanish, fall back to English
```

### Fetch raw transcript as SRT or JSON

```bash
python main.py fetch dQw4w9WgXcQ -f srt -o captions.srt
python main.py fetch dQw4w9WgXcQ -f json -o transcript.json
python main.py fetch dQw4w9WgXcQ -f vtt -o captions.vtt
```

### Fetch with timestamps

```bash
python main.py fetch dQw4w9WgXcQ -t
python main.py pipeline dQw4w9WgXcQ -t -o ./output/
```

### Pipeline — skip individual steps

```bash
# Fetch and summarize without cleaning
python main.py pipeline dQw4w9WgXcQ --skip-clean -m bullets

# Fetch and clean without summarizing
python main.py pipeline dQw4w9WgXcQ --skip-summary
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `TranscriptsDisabled` error | Video owner disabled captions | Use a different video |
| `VideoUnavailable` error | Private, deleted, or region-locked | Check URL; try VPN if region-locked |
| `NoTranscriptFound` | Requested language missing | Run `list` to see available languages |
| `AuthenticationError` | API key missing or wrong | Check `ANTHROPIC_API_KEY` env variable |
| `ModuleNotFoundError` | Dependencies not installed | Run `pip install -r requirements.txt` |
| Chunking messages in stderr | Transcript very long | Normal — multi-pass processing is automatic |
| Output cuts off mid-sentence | max_tokens limit hit | This is rare; open an issue if it occurs |

---

## Project File Reference

```
main.py          CLI entry point — all five commands
fetcher.py       YouTube direct caption API (no scraping)
cleaner.py       AI paragraph reformatter
summarizer.py    AI summarizer (4 modes)
pipeline.py      Orchestrates the full fetch -> clean -> summarize chain
ai_client.py     Anthropic API wrapper with chunking and streaming
config.py        Constants: model names, chunk size, summary modes
requirements.txt Two dependencies
README.md        Full project documentation
GUIDE.md         This file
LICENSE          MIT License
```
