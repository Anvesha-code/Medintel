import os
import re
from typing import List, Tuple

from app.core.config import settings  # ✅ centralized config

# ----------------------------
# Configuration
# ----------------------------
CHUNKS_DIR = os.path.join("data", "chunks")
SAVE_CHUNKS = True   # ✅ toggle this later for prod


# ----------------------------
# Directory helpers
# ----------------------------
def ensure_chunks_dir():
    os.makedirs(CHUNKS_DIR, exist_ok=True)


# ----------------------------
# Normalization & Cleaning
# ----------------------------
def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace while preserving paragraph boundaries.
    """
    if text is None:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    text = re.sub(r" {2,}", " ", text)

    return text.strip()


def detect_repeated_lines(pages: List[str], min_pages_percent: float = 0.5) -> List[str]:
    """
    Detect repeated header/footer lines across pages.
    """
    if not pages:
        return []

    counts = {}
    num_pages = len(pages)

    for page_text in pages:
        lines = [l.strip() for l in page_text.splitlines() if l.strip()]
        candidates = lines[:6] + lines[-6:]
        seen = set()

        for l in candidates:
            if len(l) > 200:
                continue
            key = re.sub(r"\s+", " ", l.lower())
            if key in seen:
                continue
            seen.add(key)
            counts[key] = counts.get(key, 0) + 1

    threshold = max(1, int(num_pages * min_pages_percent))
    return [line for line, cnt in counts.items() if cnt >= threshold]


def remove_headers_footers_from_pages(pages: List[str]) -> List[str]:
    """
    Remove detected repeated header/footer lines.
    """
    repeated = detect_repeated_lines(pages)
    if not repeated:
        return pages

    cleaned_pages = []
    for page_text in pages:
        new_lines = []
        for l in page_text.splitlines():
            key = re.sub(r"\s+", " ", l.strip().lower())
            if key and key in repeated:
                continue
            new_lines.append(l)
        cleaned_pages.append("\n".join(new_lines))

    return cleaned_pages


def remove_long_empty_sections(text: str, max_empty_lines: int = 2) -> str:
    """
    Collapse long runs of empty lines.
    """
    if text is None:
        return ""

    pattern = r"(\n\s*){" + str(max_empty_lines + 1) + r",}"
    return re.sub(pattern, "\n" * max_empty_lines, text)


# ----------------------------
# Page Cleaning Pipeline
# ----------------------------
def clean_text_pages(
    pages: List[dict],
    source_type: str = None
) -> Tuple[str, List[str]]:
    """
    Cleans extracted pages and returns:
      (full_text, cleaned_pages_list)
    """
    raw_pages = [
        p.get("text", "") if isinstance(p, dict) else str(p or "")
        for p in pages
    ]

    skip_hf = source_type in ("spreadsheet", "table")

    pages_no_hf = raw_pages if skip_hf else remove_headers_footers_from_pages(raw_pages)

    cleaned_pages = []
    for p in pages_no_hf:
        p2 = normalize_whitespace(p)
        p2 = remove_long_empty_sections(p2, max_empty_lines=2)
        cleaned_pages.append(p2.strip())

    full_text = "\n\n".join([p for p in cleaned_pages if p])

    return full_text, cleaned_pages


# ----------------------------
# Chunking Functions
# ----------------------------
def chunk_text(
    text: str,
    chunk_size: int = settings.CHUNK_SIZE,
    overlap: int = settings.CHUNK_OVERLAP
) -> List[str]:
    """
    Character-based chunking for prose content.
    """
    if not text:
        return []

    if len(text) <= chunk_size:
        return [text.strip()]

    chunks = []
    start = 0
    n = len(text)

    while start < n:
        end = start + chunk_size
        chunk = text[start:end]

        if end < n:
            tail = text[end:end + 100]
            m = re.search(r"[.!?]\s", tail)
            if m:
                chunk += tail[:m.end()]
                end += m.end()

        chunks.append(chunk.strip())
        start = max(0, end - overlap)

    return chunks


def chunk_table_text(
    table_text: str,
    chunk_size: int = 300
) -> List[str]:
    """
    Row-aligned chunking for table-like text.
    """
    if not table_text:
        return []

    rows = [r.strip() for r in table_text.splitlines() if r.strip()]
    chunks, curr, curr_len = [], [], 0

    for r in rows:
        r_len = len(r) + 1
        if curr and curr_len + r_len > chunk_size:
            chunks.append("\n".join(curr))
            curr, curr_len = [r], r_len
        else:
            curr.append(r)
            curr_len += r_len

    if curr:
        chunks.append("\n".join(curr))

    return chunks


def chunk_audio_transcript(
    transcript_text: str,
    chunk_chars: int = settings.AUDIO_CHUNK_CHARS,
    overlap: int = settings.AUDIO_CHUNK_OVERLAP
) -> List[str]:
    """
    Chunk long audio transcripts.
    """
    if not transcript_text:
        return []

    if len(transcript_text) <= chunk_chars:
        return [transcript_text.strip()]

    chunks = []
    start = 0
    n = len(transcript_text)

    while start < n:
        end = start + chunk_chars
        chunk = transcript_text[start:end]

        if end < n:
            tail = transcript_text[end:end + 100]
            m = re.search(r"[.!?]\s", tail)
            if m:
                chunk += tail[:m.end()]
                end += m.end()

        chunks.append(chunk.strip())
        start = max(0, end - overlap)

    return chunks


# ----------------------------
# Chunk Persistence (Optional)
# ----------------------------
def save_chunks_locally(chunks: List[str], prefix: str = "chunk") -> List[str]:
    """
    Save chunks to disk (MVP / debug only).
    """
    if not SAVE_CHUNKS:
        return []

    ensure_chunks_dir()
    saved_paths = []

    for i, c in enumerate(chunks, start=1):
        filename = f"{prefix}_{i:04d}.txt"
        path = os.path.join(CHUNKS_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(c)
        saved_paths.append(path)

    return saved_paths
