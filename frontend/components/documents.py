import streamlit as st
from utils.session_state import get_uploaded_files

def documents_section():
    st.subheader("📄 Extraction Summary")

    files = get_uploaded_files()

    if not files:
        st.info("No documents processed yet.")
        return

    for f in files:
        file_name = f.get("file_name", "Unknown File")
        file_type = f.get("file_type", "unknown")
        summary = f.get("summary", {})

        with st.expander(f"📄 {file_name}"):
            st.write(f"**Type:** {file_type.upper()}")
            st.write(f"**Pages / Units:** {summary.get('pages', 0)}")
            st.write(f"**Chunks:** {summary.get('chunks', 0)}")

            text_len = summary.get("extracted_text_length")
            if text_len:
                st.write(f"**Text Length:** {text_len} chars")
