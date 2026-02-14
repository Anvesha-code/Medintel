import streamlit as st

from components.uploader import upload_section
from components.chat import chat_section
from components.documents import documents_section
from components.media import media_section


def render_layout():
    # -----------------------------
    # Sidebar (Branding only)
    # -----------------------------
    with st.sidebar:
        st.title("🩺 MedIntel")
        st.markdown("AI-Powered Medical Document Intelligence")
        st.divider()

    # -----------------------------
    # Main Tabs
    # -----------------------------
    tabs = st.tabs(["📤 Upload", "💬 Chat", "📄 Documents", "🎧 Media"])

    with tabs[0]:
        upload_section()

    with tabs[1]:
        chat_section()

    with tabs[2]:
        documents_section()

    with tabs[3]:
        media_section()
