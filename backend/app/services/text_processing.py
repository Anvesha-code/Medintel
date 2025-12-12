# app/services/text_processing.py
import os
import re
from typing import List, Tuple

CHUNKS_DIR = os.path.join("data", "chunks")


def ensure_chunks_dir():
    os.makedirs(CHUNKS_DIR, exist_ok=True)


def normalize_whitespace(text: str) -> str:
    """
    Replace multiple whitespace characters with single spaces, but keep paragraph breaks.
    Also strip trailing/leading whitespace.
    """
    if text is None:
        return ""
    # Replace Windows/Mac line endings with \n
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse repeated spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Replace sequences of 3+ newlines with exactly two newlines (paragraph boundary)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Trim spaces at each line ends
    text = "\n".join(line.rstrip() for line in text.splitlines())

    # Collapse remaining multiple spaces
    text = re.sub(r" {2,}", " ", text)

    return text.strip()


def detect_repeated_lines(pages: List[str], min_pages_percent: float = 0.5) -> List[str]:
    """
    Very simple heuristic to detect repeated header/footer lines:
    - Look for short lines (<=200 chars) that appear on many pages.
    - If a line appears on >= min_pages_percent fraction of pages, mark it as repeated.
    """
    if not pages:
        return []

    counts = {}
    num_pages = len(pages)
    for page_text in pages:
        # take first 6 and last 6 lines of page as candidates
        lines = [l.strip() for l in page_text.splitlines() if l.strip()]
        candidates = lines[:6] + lines[-6:]
        seen_this_page = set()
        for l in candidates:
            if len(l) == 0 or len(l) > 200:
                continue
            # normalize slightly
            key = re.sub(r"\s+", " ", l.lower())
            if key in seen_this_page:
                continue
            seen_this_page.add(key)
            counts[key] = counts.get(key, 0) + 1

    repeated = []
    threshold = max(1, int(num_pages * min_pages_percent))
    for line, cnt in counts.items():
        if cnt >= threshold:
            repeated.append(line)

    return repeated


def remove_headers_footers_from_pages(pages: List[str]) -> List[str]:
    """
    Remove detected repeated header/footer lines from each page.
    """
    repeated = detect_repeated_lines(pages)
    if not repeated:
        return pages

    cleaned_pages = []
    for page_text in pages:
        lines = page_text.splitlines()
        new_lines = []
        for l in lines:
            key = re.sub(r"\s+", " ", l.strip().lower())
            if key and key in repeated:
                # skip repeated header/footer line
                continue
            new_lines.append(l)
        cleaned_pages.append("\n".join(new_lines))
    return cleaned_pages


def remove_long_empty_sections(text: str, max_empty_lines: int = 2) -> str:
    """
    Collapse sequences of empty lines to at most max_empty_lines.
    """
    if text is None:
        return ""
    # Replace sequences of more than max_empty_lines empty lines with max_empty_lines
    pattern = r"(\n\s*){" + str(max_empty_lines + 1) + r",}"
    repl = "\n" * max_empty_lines
    return re.sub(pattern, repl, text)


def clean_text_pages(pages: List[dict], source_type: str = None) -> Tuple[str, List[str]]:
    """
    pages: list of {"page_number": int, "text": str, "meta": {...} (optional)}
    Return:
      (full_text, cleaned_pages_list)

    Behavior adapts by source_type for structured inputs (spreadsheet/table).
    """
    # Defensive extraction of text strings
    raw_pages = []
    for p in pages:
        if isinstance(p, dict):
            raw_pages.append(p.get("text", "") or "")
        else:
            # fallback: page is already a string
            raw_pages.append(str(p or ""))

    # Remove obvious garbage pages (very short)
    raw_pages = [p if len(p.strip()) > 0 else "" for p in raw_pages]

    # For structured content (tables/spreadsheet) we may skip header/footer removal
    skip_hf = source_type in ("spreadsheet", "table")

    if not skip_hf:
        pages_no_hf = remove_headers_footers_from_pages(raw_pages)
    else:
        pages_no_hf = raw_pages

    # Normalize whitespace and remove long empty runs on each page
    cleaned_pages = []
    for p in pages_no_hf:
        p2 = normalize_whitespace(p)
        p2 = remove_long_empty_sections(p2, max_empty_lines=2)
        cleaned_pages.append(p2.strip())

    # Combine pages into a single full_text with page breaks
    full_text = "\n\n".join([p for p in cleaned_pages if p])

    return full_text, cleaned_pages


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into chunks of approximately `chunk_size` characters,
    with `overlap` characters overlap between chunks.
    """
    if not text:
        return []

    text = text.strip()

    # If text is short, return as single chunk
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]

        # Try to not cut mid-sentence: if possible, extend to nearest sentence end within 100 chars
        if end < text_len:
            tail = text[end:end + 100]
            m = re.search(r'[.!?]\s', tail)
            if m:
                # include up to the punctuation
                chunk += tail[:m.end()].rstrip()
                end = end + m.end()

        chunks.append(chunk.strip())

        # Move start forward with overlap
        start = end - overlap
        if start < 0:
            start = 0

    return [c for c in chunks if c]


def chunk_table_text(table_text: str, chunk_size: int = 300, overlap: int = 0) -> List[str]:
    """
    Split table-like text into row-aligned chunks. Each row should be a line in table_text.
    """
    if not table_text:
        return []
    rows = [r.strip() for r in table_text.splitlines() if r.strip()]
    chunks = []
    curr = []
    curr_len = 0
    for r in rows:
        r_len = len(r) + 1
        if curr and (curr_len + r_len > chunk_size):
            chunks.append("\n".join(curr))
            curr = [r]
            curr_len = r_len
        else:
            curr.append(r)
            curr_len += r_len
    if curr:
        chunks.append("\n".join(curr))
    return chunks


def chunk_audio_transcript(transcript_text: str, chunk_chars: int = 1500, overlap: int = 100) -> List[str]:
    """
    Split a long audio transcript into chunks of approx chunk_chars characters.
    """
    if not transcript_text:
        return []
    transcript_text = transcript_text.strip()
    if len(transcript_text) <= chunk_chars:
        return [transcript_text]

    chunks = []
    start = 0
    n = len(transcript_text)
    while start < n:
        end = start + chunk_chars
        chunk = transcript_text[start:end]
        # try to avoid mid-sentence split
        if end < n:
            tail = transcript_text[end:end + 100]
            m = re.search(r'[.!?]\s', tail)
            if m:
                chunk += tail[:m.end()].rstrip()
                end = end + m.end()
        chunks.append(chunk.strip())
        start = end - overlap
        if start < 0:
            start = 0
    return [c for c in chunks if c]


def save_chunks_locally(chunks: List[str], prefix: str = "chunk") -> List[str]:
    """
    Save each chunk as a text file under data/chunks/ and return list of file paths.
    """
    ensure_chunks_dir()
    saved_paths = []
    for i, c in enumerate(chunks, start=1):
        filename = f"{prefix}_{i:04d}.txt"
        full_path = os.path.join(CHUNKS_DIR, filename)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(c)
        saved_paths.append(full_path)
    return saved_paths
