# app/services/docx_extractor.py
from docx import Document
from pathlib import Path

def extract_text_from_docx(path: Path) -> str:
    path = Path(path)
    doc = Document(str(path))
    return "\n".join([p.text for p in doc.paragraphs if p.text])
