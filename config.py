"""
config.py
Central configuration for the YouTube Transcript Toolkit.
Author: algorembrant
"""

# ---------------------------------------------------------------------------
# Model settings
# ---------------------------------------------------------------------------
# claude-haiku-4-5 is used by default for speed.
# Switch to claude-sonnet-4-6 for higher quality at the cost of latency.
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
QUALITY_MODEL = "claude-sonnet-4-6"

MAX_TOKENS = 8192          # Maximum tokens to request from the model
CHUNK_SIZE = 60_000        # Characters per chunk for very long transcripts

# ---------------------------------------------------------------------------
# Transcript defaults
# ---------------------------------------------------------------------------
DEFAULT_LANGUAGES = ["en"]

# ---------------------------------------------------------------------------
# Summary modes
# ---------------------------------------------------------------------------
SUMMARY_MODES = {
    "brief": {
        "label": "Brief",
        "description": "3-5 sentence executive summary",
    },
    "detailed": {
        "label": "Detailed",
        "description": "Comprehensive multi-section breakdown",
    },
    "bullets": {
        "label": "Bullet Points",
        "description": "Key takeaways as a structured bullet list",
    },
    "outline": {
        "label": "Outline",
        "description": "Hierarchical topic outline",
    },
}

# ---------------------------------------------------------------------------
# Output formats
# ---------------------------------------------------------------------------
OUTPUT_FORMATS = ["text", "json", "srt", "vtt"]
