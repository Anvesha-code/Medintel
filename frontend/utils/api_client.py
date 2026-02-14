import requests
import os
from dotenv import load_dotenv
from typing import Dict

# --------------------------------------------------
# ENV
# --------------------------------------------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

BACKEND_URL = "http://127.0.0.1:8000"

# --------------------------------------------------
# SUPABASE AUTH
# --------------------------------------------------
HEADERS_SUPABASE = {
    "apikey": SUPABASE_ANON_KEY,
    "Content-Type": "application/json"
}

def supabase_signup(email: str, password: str) -> Dict:
    url = f"{SUPABASE_URL}/auth/v1/signup"
    response = requests.post(
        url,
        headers=HEADERS_SUPABASE,
        json={"email": email, "password": password}
    )

    if response.status_code not in (200, 201):
        raise Exception(response.json())

    return response.json()


def supabase_login(email: str, password: str) -> Dict:
    response = requests.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers=HEADERS_SUPABASE,
        json={"email": email, "password": password}
    )

    if not response.ok:
        raise Exception(response.json())

    data = response.json()

    # Normalize response for frontend usage
    return {
        "user": data.get("user"),
        "session": {
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token")
        }
    }

# --------------------------------------------------
# BACKEND AUTH HEADER
# --------------------------------------------------
def _auth_headers(token: str):
    return {
        "Authorization": f"Bearer {token}"
    }

# --------------------------------------------------
# DOCUMENT UPLOAD
# --------------------------------------------------
def upload_file(
    file,
    token: str,
    file_type: str | None = None
) -> Dict:
    url = f"{BACKEND_URL}/files/files/upload"

    files = {
        "file": (file.name, file.getvalue(), "application/octet-stream")
    }

    data = {}
    if file_type:
        data["file_type"] = file_type

    response = requests.post(
        url,
        headers=_auth_headers(token),
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

# --------------------------------------------------
# CHAT (JWT PROTECTED)
# --------------------------------------------------
def ask_chat(
    question: str,
    token: str,
    document_id: int | None = None
) -> Dict:
    params = {"question": question}
    if document_id:
        params["document_id"] = document_id

    response = requests.post(
        f"{BACKEND_URL}/chat/ask",
        headers=_auth_headers(token),
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

# --------------------------------------------------
# DOCUMENTS
# --------------------------------------------------
def get_documents(token: str) -> Dict:
    response = requests.get(
        f"{BACKEND_URL}/documents/",
        headers=_auth_headers(token),
        timeout=30
    )

    if not response.ok:
        raise Exception(
            f"Failed to fetch documents | "
            f"Status: {response.status_code} | "
            f"Response: {response.text}"
        )

    return response.json()


def delete_document(doc_id: int, token: str) -> Dict:
    response = requests.delete(
        f"{BACKEND_URL}/documents/{doc_id}",
        headers=_auth_headers(token),
        timeout=30
    )

    if not response.ok:
        raise Exception(response.text)

    return response.json()


def reprocess_document(doc_id: int, token: str) -> Dict:
    response = requests.post(
        f"{BACKEND_URL}/documents/{doc_id}/reprocess",
        headers=_auth_headers(token),
        timeout=30
    )

    if not response.ok:
        raise Exception(response.text)

    return response.json()

# --------------------------------------------------
# DOWNLOAD DOCUMENT FILE
# --------------------------------------------------
def download_document_file(doc_id: int, token: str) -> bytes:
    response = requests.get(
        f"{BACKEND_URL}/documents/{doc_id}/download",
        headers=_auth_headers(token),
        timeout=60
    )

    if not response.ok:
        raise Exception(
            f"Download failed | "
            f"Status: {response.status_code} | "
            f"Response: {response.text}"
        )

    return response.content
