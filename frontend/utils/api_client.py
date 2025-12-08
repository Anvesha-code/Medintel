# frontend/utils/api_client.py
import os
import requests

API_URL = os.environ.get("MEDINTEL_API_URL", "http://localhost:8000")
UPLOAD_ENDPOINT = f"{API_URL}/upload"
ASK_ENDPOINT = f"{API_URL}/ask"

def upload_file(file):
    files = {"file": (file.name, file.getvalue(), file.type)}
    r = requests.post(UPLOAD_ENDPOINT, files=files, timeout=60)
    r.raise_for_status()
    return r.json()

def ask(question, doc_ids=None, max_results=5):
    payload = {"question": question, "doc_ids": doc_ids or [], "max_results": max_results}
    r = requests.post(ASK_ENDPOINT, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()
