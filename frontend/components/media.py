import streamlit as st
from utils.session_state import get_uploaded_files
from components.upload_preview import show_preview


def media_section():
    st.subheader("🔍 Previews")

    files = get_uploaded_files()

    if not files:
        st.info("No previews available.")
        return

    for f in files:
        file_name = f.get("file_name", "Unknown File")
        file_type = f.get("file_type", "unknown")
        summary = f.get("summary", {})

        st.markdown(f"### 📄 {file_name}")

        preview_text = summary.get("preview", "")

        # Reuse Day-14 preview renderer
        show_preview(
            file_type=file_type,
            file_bytes=None,          # bytes already shown during upload
            preview_text=preview_text
        )

        st.divider()
