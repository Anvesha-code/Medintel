# app/utils/file_type.py
import mimetypes
from typing import Tuple
try:
    import magic  # python-magic (libmagic wrapper)
except Exception:
    magic = None


def detect_file_type(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    """
    Return (mime_type, ext_lower).
    Prefer libmagic detection if available, otherwise fallback to mimetypes.
    """
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    mime_by_ext, _ = mimetypes.guess_type(filename)

    mime_by_magic = None
    if magic is not None:
        try:
            # use buffer sniffing
            mime_by_magic = magic.from_buffer(file_bytes, mime=True)
        except Exception:
            mime_by_magic = None

    mime = mime_by_magic or mime_by_ext or "application/octet-stream"
    return mime, ext
