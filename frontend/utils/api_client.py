import requests
from typing import Dict

BACKEND_URL = "http://127.0.0.1:8000"


# -------------------------------------------------
# Upload Document (Day 14) – CORRECT
# -------------------------------------------------
def upload_file(
    file_bytes: bytes,
    file_name: str,
    file_type: str,
    user_id: int = 5
) -> Dict:
    url = f"{BACKEND_URL}/files/files/upload"

    files = {
        "file": (file_name, file_bytes, "application/octet-stream")
    }

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

    if not response.ok:
        raise Exception(
            f"Upload failed | "
            f"Status: {response.status_code} | "
            f"Response: {response.text}"
        )

    return response.json()


# -------------------------------------------------
# Chat Query (Day 15) – FIXED
# -------------------------------------------------
def query_chat(
    question: str,
    user_id: int = 5
) -> Dict:
    """
    Calls FastAPI /chat/ask
    Backend expects QUERY parameters, not JSON.
    """

    params = {
        "question": question,
        "user_id": user_id
    }

    response = requests.post(
        f"{BACKEND_URL}/chat/chat/ask",
        params=params,
        timeout=300
    )

    if not response.ok:
        raise Exception(
            f"Chat API failed | "
            f"Status: {response.status_code} | "
            f"Response: {response.text}"
        )

    return response.json()
