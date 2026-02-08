import streamlit as st

def init_session():
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

def add_uploaded_file(result: dict):
    init_session()
    st.session_state.uploaded_files.append(result)

def get_uploaded_files():
    init_session()
    return st.session_state.uploaded_files
