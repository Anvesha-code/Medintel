# app/services/txt_extractor.py
from pathlib import Path

def extract_text_from_txt(file_bytes: bytes) -> dict:
    text = file_bytes.decode("utf-8", errors="ignore")
    return {
        "pages": [
            {"page_number": 1, "text": text, "meta": {}}
        ],
        "meta": {}
    }

    with open(path, "r", encoding="utf-8") as f:
        return f.read()
