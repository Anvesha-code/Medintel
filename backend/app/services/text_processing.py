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
    # Replace Windows/Mac line endings with \n
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse repeated spaces (but keep newlines for paragraph separation)
    # First, collapse spaces/tabs
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
    # Replace sequences of more than max_empty_lines empty lines with max_empty_lines
    pattern = r"(\n\s*){" + str(max_empty_lines + 1) + r",}"
    repl = "\n" * max_empty_lines
    return re.sub(pattern, repl, text)


def clean_text_pages(pages: List[dict]) -> Tuple[str, List[str]]:
    """
    pages: list of {"page_number": int, "text": str}
    Return:
      (full_text, cleaned_pages_list)
    Steps:
      - Extract page texts
      - Remove headers/footers heuristically
      - Normalize whitespace and remove long empty sections
      - Recombine to full_text
    """
    raw_pages = [p.get("text", "") or "" for p in pages]
    # Remove obvious garbage pages (very short)
    raw_pages = [p if len(p.strip()) > 0 else "" for p in raw_pages]

    # Detect and remove repeated header/footer lines
    pages_no_hf = remove_headers_footers_from_pages(raw_pages)

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

    Returns a list of chunk strings.
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
