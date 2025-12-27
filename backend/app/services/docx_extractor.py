import io
from docx import Document

def extract_text_from_docx(docx_bytes: bytes) -> dict:
    doc = Document(io.BytesIO(docx_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

    return {
        "pages": [{
            "page_number": 1,
            "text": "\n\n".join(paragraphs),
            "meta": {"paragraphs": len(paragraphs)}
        }],
        "meta": {}
    }
