# app/services/pptx_extractor.py
import io
from typing import Dict, List
from pptx import Presentation

def extract_text_from_pptx(pptx_bytes: bytes) -> Dict:
    f = io.BytesIO(pptx_bytes)
    prs = Presentation(f)
    pages = []
    for i, slide in enumerate(prs.slides, start=1):
        texts = []
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                t = shape.text.strip()
                if t:
                    texts.append(t)
        # slide notes
        notes = ""
        if slide.has_notes_slide:
            notes_slide = slide.notes_slide
            notes_text = []
            for p in notes_slide.notes_text_frame.paragraphs:
                if p.text:
                    notes_text.append(p.text.strip())
            notes = "\n".join(notes_text)
        slide_text = "\n\n".join(texts + ([notes] if notes else []))
        pages.append({"page_number": i, "text": slide_text or "", "meta": {"has_notes": bool(notes)}})
    meta = {"slide_count": len(pages)}
    return {"pages": pages, "meta": meta}
