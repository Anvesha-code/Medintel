import streamlit as st
from utils.file_detector import detect_file_type
from utils.api_client import upload_file
from utils.session_state import add_uploaded_file


def upload_section():
    st.subheader("📤 Upload Medical Documents")

    # --------------------------------------------------
    # ✅ AUTH CHECK (STANDARDIZED)
    # --------------------------------------------------
    if not st.session_state.logged_in:
        st.error("You must be logged in to upload documents.")
        return

    token = st.session_state.token
    if not token:
        st.error("Authentication token missing. Please login again.")
        return

    # --------------------------------------------------
    # 📤 FILE UPLOADER
    # --------------------------------------------------
    uploaded_files = st.file_uploader(
        "Upload PDF / Image / Audio / Text",
        type=["pdf", "png", "jpg", "jpeg", "wav", "mp3", "txt"],
        accept_multiple_files=True
    )

    if not uploaded_files:
        st.info("Upload files to extract and analyze medical data.")
        return

    # --------------------------------------------------
    # 🚀 PROCESS FILES
    # --------------------------------------------------
    for file in uploaded_files:
        st.divider()
        st.markdown(f"### 📄 {file.name}")

        file_type = detect_file_type(file.name)

        try:
            with st.spinner("Uploading document..."):
                upload_file(
                    file=file,
                    token=token,
                    file_type=file_type
                )

            # --------------------------------------------------
            # ✅ SUCCESS
            # --------------------------------------------------
            st.success("✅ Document uploaded successfully!")

            add_uploaded_file({
                "filename": file.name,
                "file_type": file_type
            })

            st.info(
                "📚 The document has been successfully saved to your Knowledge Repository.\n\n"
                "💬 You can now go to the Chat section and ask questions about this document.\n\n"
                "You can return anytime — your document remains securely stored for future queries."
            )

        except Exception as e:
            st.error("❌ Failed to upload document.")
            st.error(str(e))
