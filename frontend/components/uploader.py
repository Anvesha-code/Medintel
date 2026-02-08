import streamlit as st
from utils.file_detector import detect_file_type
from utils.api_client import upload_file
from utils.summary_parser import parse_summary
from components.upload_progress import show_progress
from components.upload_preview import show_preview
from utils.session_state import add_uploaded_file

def upload_section():
    st.subheader("📤 Upload Medical Documents")

    uploaded_files = st.file_uploader(
        "Upload PDF / Image / Audio / Text",
        type=["pdf", "png", "jpg", "jpeg", "wav", "mp3", "txt"],
        accept_multiple_files=True
    )

    if not uploaded_files:
        st.info("Upload files to extract and analyze medical data.")
        return

    for file in uploaded_files:
        st.divider()
        st.markdown(f"### 📄 {file.name}")

        file_type = detect_file_type(file.name)
        file_bytes = file.read()

        show_progress(file.name)

        with st.spinner("Sending to backend..."):
            response = upload_file(
                file_name=file.name,
                file_bytes=file_bytes,
                file_type=file_type
            )

        summary = parse_summary(response)

        add_uploaded_file(file.name, file_type, file_bytes)

        # Summary UI
        col1, col2, col3 = st.columns(3)
        col1.metric("Pages / Slides", summary["pages"])
        col2.metric("Chunks", summary["chunks"])
        col3.metric("Text Length", summary["text_length"])

        # Preview UI
        show_preview(
            file_type=file_type,
            file_bytes=file_bytes,
            preview_text=summary["preview"]
        )
