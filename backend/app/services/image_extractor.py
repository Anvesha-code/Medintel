# app/services/image_extractor.py
import io
from typing import Dict
from PIL import Image
import pytesseract

def extract_text_from_image(image_bytes: bytes) -> Dict:
    """
    OCR an image and return single-page result.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
    except Exception:
        # try forcing binary read
        img = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(img)
    meta = {"format": img.format, "size": img.size}
    return {"pages": [{"page_number": 1, "text": text or "", "meta": meta}], "meta": meta}
