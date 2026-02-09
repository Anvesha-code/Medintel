import streamlit as st


# -------------------------------------------------
# Initialize Session State
# -------------------------------------------------
def init_session():
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


# -------------------------------------------------
# Uploaded Files Handling
# -------------------------------------------------
def add_uploaded_file(file_info: dict):
    """
    Expected schema:
    {
        "file_name": str,
        "file_type": str,
        "summary": dict   # backend extraction response
    }
    """
    init_session()
    st.session_state.uploaded_files.append(file_info)


def get_uploaded_files():
    init_session()
    return st.session_state.uploaded_files


# -------------------------------------------------
# Chat History Handling (Day 15)
# -------------------------------------------------
def add_chat_message(role: str, content: dict):
    """
    role: 'user' | 'assistant'
    content:
    {
        "text": str,
        "sources": list (optional)
    }
    """
    init_session()
    st.session_state.chat_history.append({
        "role": role,
        "content": content
    })


def get_chat_history():
    init_session()
    return st.session_state.chat_history
