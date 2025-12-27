import os
import re
from typing import List, Dict
from app.core.config import settings

CHUNKS_DIR = os.path.join("data", "chunks")

def ensure_chunks_dir():
    os.makedirs(CHUNKS_DIR, exist_ok=True)


# ---------------- CLEANING ----------------

def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def remove_repeated_headers_footers(pages: List[str]) -> List[str]:
    if len(pages) <= 1:
        return pages

    counts = {}
    for p in pages:
        for line in p.splitlines()[:5] + p.splitlines()[-5:]:
            key = line.strip().lower()
            if key:
                counts[key] = counts.get(key, 0) + 1

    repeated = {k for k, v in counts.items() if v > len(pages) * 0.5}

    cleaned = []
    for p in pages:
        lines = [
            l for l in p.splitlines()
            if l.strip().lower() not in repeated
        ]
        cleaned.append("\n".join(lines))
    return cleaned


def clean_text_blocks(blocks: List[Dict]) -> List[Dict]:
    pages = [b["raw_text"] for b in blocks]
    pages = remove_repeated_headers_footers(pages)

    cleaned_blocks = []
    for b, p in zip(blocks, pages):
        b["raw_text"] = normalize_whitespace(p)
        cleaned_blocks.append(b)

    return cleaned_blocks


# ---------------- CHUNKING ----------------

def chunk_text(text: str,
               chunk_size: int = settings.CHUNK_SIZE,
               overlap: int = settings.CHUNK_OVERLAP) -> List[str]:
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start = max(0, end - overlap)
    return chunks


def chunk_table_text(table_text: str,
                     headers: List[str] = None,
                     chunk_size: int = 300) -> List[str]:
    rows = [r.strip() for r in table_text.splitlines() if r.strip()]
    chunks, curr, size = [], [], 0

    prefix = ""
    if headers:
        prefix = " | ".join(headers) + "\n"

    for r in rows:
        if size + len(r) > chunk_size:
            chunks.append(prefix + "\n".join(curr))
            curr, size = [], 0
        curr.append(r)
        size += len(r)

    if curr:
        chunks.append(prefix + "\n".join(curr))

    return chunks


# ---------------- STORAGE ----------------

def save_chunks_locally(chunks: List[str], prefix: str) -> List[str]:
    ensure_chunks_dir()
    paths = []

    for i, c in enumerate(chunks, 1):
        path = os.path.join(CHUNKS_DIR, f"{prefix}_{i:04d}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(c)
        paths.append(path)

    return paths
