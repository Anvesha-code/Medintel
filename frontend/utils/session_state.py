# frontend/utils/session_state.py
import streamlit as st

def init_state():
    if "docs" not in st.session_state:
        st.session_state.docs = []
    if "chat" not in st.session_state:
        st.session_state.chat = []
