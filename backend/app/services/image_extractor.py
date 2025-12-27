import io
from PIL import Image
import pytesseract

def extract_text_from_image(image_bytes: bytes) -> dict:
    img = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(img)

    return {
        "pages": [{
            "page_number": 1,
            "text": text,
            "meta": {"format": img.format}
        }],
        "meta": {}
    }
