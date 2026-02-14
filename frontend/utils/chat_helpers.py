import requests
from typing import Optional

BACKEND_URL = "http://localhost:8000"


def ask_chat(
    question: str,
    token: str,
    document_id: Optional[int] = None
):
    """
    Calls JWT-protected chat endpoint.
    Token must be a valid Supabase access_token.
    document_id is optional.
    """
    url = f"{BACKEND_URL}/chat/chat/ask"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "question": question
    }

    # ✅ Attach document_id only if provided
    if document_id is not None:
        params["document_id"] = document_id

    try:
        response = requests.post(
            url,
            headers=headers,
            params=params,
            timeout=300
        )
    except requests.RequestException as e:
        raise Exception(f"Backend not reachable: {e}")

    if response.status_code != 200:
        raise Exception(
            f"Chat request failed | "
            f"Status: {response.status_code} | "
            f"Response: {response.text}"
        )

    return response.json()
