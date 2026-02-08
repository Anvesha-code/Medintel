def parse_summary(response_json):
    return {
        "pages": response_json.get("pages", 0),
        "chunks": response_json.get("chunks", 0),
        "text_length": response_json.get("extracted_text_length", 0),
        "preview": response_json.get("preview", "")
    }
