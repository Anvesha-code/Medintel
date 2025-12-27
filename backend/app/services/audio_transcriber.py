# app/services/audio_transcriber.py

import tempfile
import os
from typing import Dict

from app.core.config import settings

try:
    import whisper  # openai/whisper
except Exception:
    whisper = None

_WHISPER_MODEL = None  # cache model


def transcribe_audio(audio_bytes: bytes, filename: str = None) -> Dict:
    """
    Transcribe audio using Whisper.
    Returns: {"pages": [...], "meta": {...}}
    """

    # Feature flag check
    if not settings.ENABLE_AUDIO:
        raise RuntimeError("Audio transcription is disabled by configuration")

    if whisper is None:
        raise RuntimeError("Whisper is not installed. Please install 'whisper'.")

    # File size guard
    if len(audio_bytes) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise RuntimeError("Audio file exceeds allowed size limit")

    # Write temp file
    suffix = "." + (filename.split(".")[-1] if filename and "." in filename else "wav")
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        global _WHISPER_MODEL
        if _WHISPER_MODEL is None:
            _WHISPER_MODEL = whisper.load_model(settings.WHISPER_MODEL)

        result = _WHISPER_MODEL.transcribe(tmp_path)

        text = result.get("text", "").strip()
        meta = {
            "duration": result.get("duration"),
            "language": result.get("language"),
            "model": settings.WHISPER_MODEL
        }

        return {
            "pages": [
                {"page_number": 1, "text": text, "meta": meta}
            ],
            "meta": meta
        }

    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
