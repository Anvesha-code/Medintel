from app.core.config import settings


def transcribe_audio(file_path: str) -> dict:
    if not settings.ENABLE_AUDIO:
        return {
            "text": "",
            "language": None,
            "status": "audio_disabled"
        }

    try:
        import whisper  # 🔥 lazy import (ONLY when enabled)
    except Exception as e:
        return {
            "text": "",
            "language": None,
            "status": f"whisper_unavailable: {e}"
        }

    model = whisper.load_model("tiny")
    result = model.transcribe(file_path)

    return {
        "text": result.get("text", ""),
        "language": result.get("language"),
        "status": "ok"
    }
