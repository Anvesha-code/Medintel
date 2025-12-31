from app.services.pdf_extractor import extract_text_from_pdf
from app.services.image_extractor import extract_text_from_image
from app.services.docx_extractor import extract_text_from_docx
from app.services.pptx_extractor import extract_text_from_pptx
from app.services.spreadsheet_extractor import extract_text_from_spreadsheet
from app.services.html_extractor import extract_text_from_html
from app.services.audio_transcriber import transcribe_audio
from app.services.txt_extractor import extract_text_from_txt


def extract_text(file_bytes: bytes, filename: str, mime: str) -> dict:
    ext = filename.split(".")[-1].lower()

    # ------------------------------
    # 1. Route to extractor
    # ------------------------------
    if "pdf" in mime or ext == "pdf":
        raw = extract_text_from_pdf(file_bytes)
        source = "pdf"

    elif mime.startswith("image/"):
        raw = extract_text_from_image(file_bytes)
        source = "image"

    elif ext in ("doc", "docx"):
        raw = extract_text_from_docx(file_bytes)
        source = "docx"

    elif ext in ("ppt", "pptx"):
        raw = extract_text_from_pptx(file_bytes)
        source = "pptx"

    elif ext in ("xls", "xlsx", "csv"):
        raw = extract_text_from_spreadsheet(file_bytes, filename)
        source = "spreadsheet"

    elif ext in ("html", "htm"):
        raw = extract_text_from_html(file_bytes)
        source = "html"

    elif mime.startswith("audio/"):
        raw = transcribe_audio(file_bytes, filename)
        source = "audio"

    else:
        raw = extract_text_from_txt(file_bytes)
        source = "text"

    # ------------------------------
    # 2. Normalize pages safely
    # ------------------------------
    pages = raw.get("pages", []) if isinstance(raw, dict) else []

    # ------------------------------
    # 3. Build text blocks
    # ------------------------------
    blocks = []
    for idx, p in enumerate(pages):
        blocks.append({
            "source_type": source,
            "index": p.get("page_number", idx + 1),
            "raw_text": p.get("text", ""),
            "structured": source == "spreadsheet",
            "headers": p.get("meta", {}).get("headers"),
            "meta": p.get("meta", {})
        })

    # ------------------------------
    # 4. Metadata (NO NULLS)
    # ------------------------------
    meta_from_extractor = raw.get("meta", {}) if isinstance(raw, dict) else {}

    # Page count
    if source in ("pdf", "docx", "pptx", "html", "text", "image"):
        page_count = len(pages) if pages else 1
    else:
        page_count = 0

    # Sheet count
    if source == "spreadsheet":
        sheet_count = meta_from_extractor.get("sheet_count", len(pages) if pages else 1)
    else:
        sheet_count = 0

    # Language
    language = "eng"

    # ------------------------------
    # 5. Final return (NO NULLS)
    # ------------------------------
    return {
        "text_blocks": blocks,
        "meta": {
            "page_count": page_count,
            "sheet_count": sheet_count,
            "language": language
        }
    }
