def detect_file_type(filename: str) -> str:
    ext = filename.lower().split(".")[-1]

    if ext in ["pdf"]:
        return "pdf"
    if ext in ["png", "jpg", "jpeg"]:
        return "image"
    if ext in ["wav", "mp3"]:
        return "audio"
    if ext in ["txt"]:
        return "text"

    return "unknown"
