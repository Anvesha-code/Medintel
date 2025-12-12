# app/services/audio_transcriber.py
import io
import tempfile
from typing import Dict
try:
    import whisper  # openai/whisper
except Exception:
    whisper = None
import os
import subprocess

def transcribe_audio(audio_bytes: bytes, filename: str = None) -> Dict:
    """
    Transcribe using Whisper model 'small' if installed. Returns {"pages":[...],"meta":{}}.
    If whisper not available, raise an error (or implement alternative).
    """
    if whisper is None:
        raise RuntimeError("Whisper is not installed. Please install 'whisper' to enable audio transcription.")

    # write to temp file
    suffix = "." + (filename.split(".")[-1] if filename and "." in filename else "wav")
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        tmp_path = tmp.name

    try:
        model = whisper.load_model("small")  # choose appropriate model for accuracy vs speed
        result = model.transcribe(tmp_path)
        text = result.get("text", "").strip()
        meta = {"duration": result.get("duration", None), "language": result.get("language", None)}
        return {"pages": [{"page_number": 1, "text": text, "meta": meta}], "meta": meta}
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
