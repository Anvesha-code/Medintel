import streamlit as st
from utils.api_client import (
    get_documents,
    delete_document,
    reprocess_document
)

ICON_MAP = {
    "pdf": "📄",
    "image": "🖼️",
    "audio": "🎧",
    "text": "📝"
}


def documents_section():
    st.subheader("📄 Documents")

    # 🔹 Fetch from backend DB (NOT session state)
    try:
        documents = get_documents(user_id=5)
    except Exception as e:
        st.error(f"Failed to load documents: {e}")
        return

    if not documents:
        st.info("No documents uploaded yet.")
        return

    # 🔍 Search
    search_query = st.text_input("🔍 Search documents by name")

    for doc in documents:
        file_name = doc.get("file_name", "Unknown")
        file_type = doc.get("file_type", "unknown")
        pages = doc.get("pages", 0)
        chunks = doc.get("chunks", 0)

        # ✅ Safe status handling
        status = (doc.get("status") or "unknown").upper()
        doc_id = doc.get("id")

        if search_query and search_query.lower() not in file_name.lower():
            continue

        icon = ICON_MAP.get(file_type, "📁")

        with st.expander(f"{icon} {file_name}"):
            col1, col2, col3 = st.columns(3)

            col1.metric("Pages / Units", pages)
            col2.metric("Chunks", chunks)
            col3.metric("Status", status)

            st.divider()

            col_a, col_b = st.columns(2)

            with col_a:
                if st.button("🔁 Reprocess", key=f"re_{doc_id}"):
                    try:
                        reprocess_document(doc_id, user_id=5)
                        st.success("Reprocessing started")
                        st.experimental_rerun()   # ✅ FIX
                    except Exception as e:
                        st.error(str(e))

            with col_b:
                if st.button("🗑 Delete", key=f"del_{doc_id}"):
                    try:
                        delete_document(doc_id, user_id=5)
                        st.success("Document deleted")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(str(e))
