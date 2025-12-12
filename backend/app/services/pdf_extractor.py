# app/services/pdf_extractor.py
import io
from typing import List, Dict
try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None
from PIL import Image
import pytesseract

def _ocr_image_bytes(image_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(img)
    return text or ""

def extract_text_from_pdf(pdf_bytes: bytes) -> Dict:
    """
    Returns dict {"pages": [{"page_number":i, "text": "...", "meta": {...}}, ...], "meta": {...}}
    """
    pages = []
    meta = {"is_scanned": False}
    if fitz is None:
        raise RuntimeError("PyMuPDF (fitz) is required for PDF extraction")

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for i, page in enumerate(doc, start=1):
        try:
            text = page.get_text().strip()
        except Exception:
            text = ""
        if not text:
            # likely scanned page -> rasterize and OCR
            meta["is_scanned"] = True
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")
            ocr_text = _ocr_image_bytes(img_bytes)
            page_text = ocr_text
        else:
            page_text = text
        pages.append({"page_number": i, "text": page_text, "meta": {"is_scanned_page": bool(not text)}})
    doc.close()
    meta["page_count"] = len(pages)
    return {"pages": pages, "meta": meta}
