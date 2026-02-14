import streamlit as st

# --------------------------------------------------
# INIT
# --------------------------------------------------
def init_session_state():
    # ---------- AUTH ----------
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # ✅ STANDARD TOKEN NAME (IMPORTANT)
    if "token" not in st.session_state:
        st.session_state.token = None

    # (Optional: backward compatibility)
    if "access_token" not in st.session_state:
        st.session_state.access_token = None

    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    # ---------- UPLOADS ----------
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    # ---------- CHAT ----------
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


# --------------------------------------------------
# UPLOAD HELPERS
# --------------------------------------------------
def add_uploaded_file(file_info: dict):
    init_session_state()
    st.session_state.uploaded_files.append(file_info)


def get_uploaded_files():
    init_session_state()
    return st.session_state.uploaded_files


# --------------------------------------------------
# CHAT HELPERS
# --------------------------------------------------
def add_chat_message(role: str, content: str):
    """
    role: 'user' | 'assistant'
    """
    init_session_state()
    st.session_state.chat_history.append({
        "role": role,
        "content": content
    })


def get_chat_history():
    init_session_state()
    return st.session_state.chat_history


def clear_chat_history():
    init_session_state()
    st.session_state.chat_history = []
