# app/services/pdf_extractor.py

import io
from typing import Dict, List, Any

import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import easyocr

from pypdf import PdfReader
from pypdf.errors import PdfReadError


# Initialize OCR once (slow first time, then reused)
ocr_reader = easyocr.Reader(['en'], gpu=False)


def _ocr_page(pix: fitz.Pixmap) -> str:
    """
    Run OCR on a rendered PDF page.
    """
    mode = "RGB"
    if pix.alpha:
        mode = "RGBA"

    img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
    img_np = np.array(img)

    results = ocr_reader.readtext(img_np, detail=0, paragraph=True)
    return "\n".join(results).strip()


def extract_text_from_pdf(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Extract text from a PDF given as raw bytes.

    Strategy:
    1. Try pypdf for normal text PDFs (fast).
    2. If little/no text → fallback to PyMuPDF + OCR for scanned PDFs.
    3. Return:
       {
         "full_text": "...",
         "pages": [
             {"page_number": 1, "text": "..."},
             ...
         ]
       }
    """

    try:
        pages: List[Dict[str, Any]] = []

        # ✅ Step 1: normal text extraction using pypdf
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages.append({
                    "page_number": idx + 1,
                    "text": text.strip()
                })
        except PdfReadError:
            # Corrupted / unreadable by pypdf → we’ll try OCR path
            pages = []

        # ✅ Step 2: fallback to PyMuPDF + OCR if needed
        if not pages or sum(len(p["text"]) for p in pages) < 50:
            pages = []
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

            for idx in range(len(doc)):
                page = doc.load_page(idx)

                text = page.get_text("text").strip()
                if len(text) < 20:  # assume scanned / image-only
                    pix = page.get_pixmap()
                    text = _ocr_page(pix)

                pages.append({
                    "page_number": idx + 1,
                    "text": text
                })

        # ✅ Combine all text
        full_text = "\n\n".join(
            page["text"] for page in pages if page["text"]
        )

        return {
            "full_text": full_text,
            "pages": pages
        }

    except PdfReadError:
        raise ValueError("PDF is corrupted or unreadable")

    except Exception as e:
        raise ValueError(f"Error reading PDF: {str(e)}")
