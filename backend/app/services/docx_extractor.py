# app/services/docx_extractor.py
import io
from typing import Dict, List
from docx import Document

def extract_text_from_docx(docx_bytes: bytes) -> Dict:
    """
    Return pages as logical blocks (we use a single page per document unless we detect page breaks).
    """
    f = io.BytesIO(docx_bytes)
    doc = Document(f)
    paragraphs = []
    for p in doc.paragraphs:
        t = p.text.strip()
        if t:
            paragraphs.append(t)
    # join paragraphs with double newline
    text = "\n\n".join(paragraphs)
    meta = {"paragraphs": len(paragraphs)}
    return {"pages": [{"page_number": 1, "text": text, "meta": meta}], "meta": meta}
