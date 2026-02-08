import requests
from typing import Dict

BACKEND_URL = "http://127.0.0.1:8000"

def upload_file(
    file_bytes: bytes,
    file_name: str,
    file_type: str,
    user_id: int = 5
) -> Dict:
    """
    Uploads a document to backend and returns extraction summary.
    """

    url = f"{BACKEND_URL}/files/files/upload"

    print(f"DEBUG: Calling URL -> {url}")
    print(f"DEBUG: File -> {file_name}, Type -> {file_type}, User -> {user_id}")

    files = {
        "file": (file_name, file_bytes, "application/octet-stream")
    }

    # Backend-readable metadata
    data = {
        "file_type": file_type,
        "user_id": user_id
    }

    response = requests.post(
        url,
        files=files,
        data=data,
        timeout=120
    )

    response.raise_for_status()
    return response.json()
