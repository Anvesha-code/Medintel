# app/services/pdf_extractor.py
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from typing import Optional
from pathlib import Path

def extract_text_from_pdf(path: Path) -> str:
    path = Path(path)
    if not path.exists():
        raise ValueError("PDF path does not exist")

    try:
        reader = PdfReader(str(path))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts)
    except PdfReadError:
        raise ValueError("PDF is corrupted or unreadable")
    except Exception as e:
        raise ValueError(f"Error reading PDF: {e}")
