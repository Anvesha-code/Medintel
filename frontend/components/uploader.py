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

        try:
            with st.spinner("Uploading document..."):
                upload_file(
                    file_name=file.name,
                    file_bytes=file_bytes,
                    file_type=file_type
                )

            # ✅ SUCCESS MESSAGE
            st.success("✅ Document uploaded successfully!")

            st.info(

                    "📚 The document has been successfully saved to your Knowledge Repository.\n\n"
                    "💬 You can now go to the Chat section and ask questions about this document.\n\n"
                    "You can return anytime — your document remains securely stored for future queries."


            )

        except Exception as e:
            # ❌ FAILURE MESSAGE
            st.error("❌ Failed to upload document.")
            st.error(str(e))