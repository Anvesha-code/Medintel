# app/services/txt_extractor.py
from pathlib import Path

def extract_text_from_txt(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
