# app/services/html_extractor.py
from bs4 import BeautifulSoup
from typing import Dict

def extract_text_from_html(html_bytes: bytes) -> Dict:
    try:
        text = html_bytes.decode("utf-8")
    except Exception:
        text = html_bytes.decode("latin-1", errors="ignore")
    soup = BeautifulSoup(text, "html.parser")
    # remove scripts and styles
    for s in soup(["script", "style", "noscript"]):
        s.decompose()
    visible_text = soup.get_text(separator="\n")
    # normalize multiple blank lines
    lines = [ln.strip() for ln in visible_text.splitlines() if ln.strip()]
    out = "\n\n".join(lines)
    return {"pages": [{"page_number": 1, "text": out, "meta": {"title": soup.title.string if soup.title else None}}], "meta": {"type": "html"}}
