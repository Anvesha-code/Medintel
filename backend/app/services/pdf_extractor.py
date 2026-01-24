import io
import fitz
from PIL import Image
import pytesseract


pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

def extract_text_from_pdf(pdf_bytes: bytes) -> dict:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    is_scanned = False

    for i, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        print(f"[PDF] Page {i} text length: {len(text)}")
        if not text:
            print(f"[PDF] Page {i} is scanned. OCR triggered.")
            is_scanned = True
            pix = page.get_pixmap(dpi=200)
            img = Image.open(io.BytesIO(pix.tobytes("png")))

            # DEBUG IMAGE
            img.save(f"debug_page_{i}.png")
            text = pytesseract.image_to_string(img)

        pages.append({
            "page_number": i,
            "text": text,
            "meta": {"scanned": not bool(page.get_text())}
        })

    return {
        "pages": pages,
        "meta": {"page_count": len(pages), "is_scanned": is_scanned}
    }
