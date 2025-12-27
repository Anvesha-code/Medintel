def extract_text_from_txt(file_bytes: bytes) -> dict:
    text = file_bytes.decode("utf-8", errors="ignore")
    return {
        "pages": [{
            "page_number": 1,
            "text": text,
            "meta": {}
        }],
        "meta": {}
    }
