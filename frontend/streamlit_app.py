# app.py
import streamlit as st
import requests
from pathlib import Path
from typing import Any, Dict, List

# ----------------------
# Config
# ----------------------
# Change this to where your FastAPI app is running
BACKEND_URL = "http://localhost:8000"

UPLOAD_ENDPOINT = f"{BACKEND_URL}/upload/"
ASK_ENDPOINT = f"{BACKEND_URL}/chat/ask"

# small helper
def post_file_upload(filepath: Path) -> Dict[str, Any]:
    with filepath.open("rb") as f:
        files = {"file": (filepath.name, f, "application/pdf")}
        resp = requests.post(UPLOAD_ENDPOINT, files=files, timeout=60)
    resp.raise_for_status()
    return resp.json()

def ask_question(question: str, timeout: int = 60) -> Any:
    # Ask route is a POST with query param ?question=...
    params = {"question": question}
    resp = requests.post(ASK_ENDPOINT, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

# ----------------------
# Streamlit UI
# ----------------------
st.set_page_config(page_title="RAG Demo UI", layout="centered")

st.title("RAG Demo — Upload & Ask")
st.write(
    "Upload a PDF to index it in the vector DB, then ask questions. "
    "Make sure your FastAPI backend is running and endpoints match the URL above."
)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1) Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    if uploaded_file:
        save_path = Path("tmp_uploads")
        save_path.mkdir(exist_ok=True)
        local_path = save_path / uploaded_file.name

        # Save to disk first (so requests can read it)
        with open(local_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Saved locally to {local_path}")

        if st.button("Upload & Index PDF"):
            try:
                with st.spinner("Uploading and indexing..."):
                    resp = post_file_upload(local_path)
                st.success("Upload successful!")
                st.json(resp)
            except requests.exceptions.RequestException as e:
                st.error(f"Upload failed: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

with col2:
    st.subheader("2) Ask a Question")
    question = st.text_area("Type your question", height=120)
    top_k = st.number_input("Top K results", min_value=1, max_value=20, value=5)
    cols = st.columns([1, 1, 1])
    if cols[0].button("Ask"):
        if not question or not question.strip():
            st.warning("Please type a question first.")
        else:
            try:
                with st.spinner("Searching..."):
                    # The backend's ask route in our code took question param and returned answer_chunks
                    # If your backend expects JSON body instead, adjust accordingly.
                    resp = ask_question(question)
                # resp may be {"answer_chunks": [...] } or a list. handle both
                data = resp
                if isinstance(resp, dict) and "answer_chunks" in resp:
                    data = resp["answer_chunks"]

                if not data:
                    st.info("No results returned.")

                # If results are objects with provenance, render nicely
                for i, item in enumerate(data):
                    # If item is a dict with text + source
                    if isinstance(item, dict) and "text" in item:
                        st.markdown(f"**Result {i+1}**")
                        st.write(item.get("text", ""))
                        source = item.get("source")
                        if source:
                            st.caption(f"Source — filename: {source.get('filename')}, page: {source.get('page')}, chunk: {source.get('chunk_index')}")
                        st.divider()
                    else:
                        # plain string
                        st.markdown(f"**Result {i+1}**")
                        st.write(str(item))
                        st.divider()
            except requests.exceptions.Timeout:
                st.error("Search timed out. Try again or increase backend timeout.")
            except requests.exceptions.RequestException as e:
                st.error(f"Search request failed: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

st.markdown("---")
st.caption(f"Backend URL: `{BACKEND_URL}`. Edit BACKEND_URL at the top of the file or set Streamlit secret BACKEND_URL.")
