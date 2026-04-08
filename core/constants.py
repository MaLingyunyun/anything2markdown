from __future__ import annotations

from pathlib import Path

DOC_EXTENSIONS = {
    ".pdf",
    ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp",
    ".docx", ".pptx", ".xlsx",
    ".html", ".htm",
    ".md", ".markdown",
    ".csv",
    ".adoc", ".asciidoc",
    ".tex", ".latex",
}

AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac",
}

VIDEO_EXTENSIONS = {
    ".mp4", ".avi", ".mov",
}

MEDIA_EXTENSIONS = AUDIO_EXTENSIONS | VIDEO_EXTENSIONS
SUPPORTED_EXTENSIONS = DOC_EXTENSIONS | MEDIA_EXTENSIONS

DEFAULT_OUTPUT_DIR = Path("./md_output")
