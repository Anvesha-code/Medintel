import streamlit as st
from utils.session_state import (
    get_chat_history,
    add_chat_message
)
from utils.api_client import get_documents
from utils.chat_helpers import ask_chat


def chat_section():
    st.subheader("💬 Chat with Your Documents")

    # -------------------------------------------------
    # 0️⃣ AUTH CHECK (STANDARDIZED)
    # -------------------------------------------------
    if not st.session_state.logged_in:
        st.error("Please login to use chat.")
        return

    token = st.session_state.token
    if not token:
        st.error("Authentication token missing. Please login again.")
        return

    # -------------------------------------------------
    # 1️⃣ FETCH DOCUMENTS (JWT PROTECTED)
    # -------------------------------------------------
    try:
        documents = get_documents(token)
    except Exception as e:
        st.error(f"Failed to load documents: {e}")
        return

    if not documents:
        st.info("📚 No documents found. Please upload first.")
        return

    # -------------------------------------------------
    # 2️⃣ DOCUMENT SELECTION
    # -------------------------------------------------
    doc_map = {
        (
            doc.get("file_name")
            or doc.get("filename")
            or doc.get("original_filename")
            or f"Document {doc['id']}"
        ): doc["id"]
        for doc in documents
    }

    selected_doc_name = st.selectbox(
        "📄 Select a document to chat with",
        options=list(doc_map.keys())
    )

    selected_doc_id = doc_map[selected_doc_name]
    st.success(f"Using document: {selected_doc_name}")

    # -------------------------------------------------
    # 3️⃣ RENDER CHAT HISTORY
    # -------------------------------------------------
    for msg in get_chat_history():
        with st.chat_message(msg["role"]):
            content = msg["content"]
            if isinstance(content, dict):
                st.write(content.get("text", ""))
            else:
                st.write(content)

    # -------------------------------------------------
    # 4️⃣ CHAT INPUT
    # -------------------------------------------------
    user_query = st.chat_input("Ask a question about the selected document...")

    if not user_query:
        return

    with st.chat_message("user"):
        st.write(user_query)

    add_chat_message(
        role="user",
        content={"text": user_query}
    )

    # -------------------------------------------------
    # 5️⃣ BACKEND RAG CALL (JWT)
    # -------------------------------------------------
    try:
        with st.spinner("Thinking..."):
            response = ask_chat(
                question=user_query,
                token=token,
                document_id=selected_doc_id
            )
    except Exception as e:
        st.error(str(e))
        return

    # -------------------------------------------------
    # 6️⃣ PARSE RAG RESPONSE
    # -------------------------------------------------
    answer_chunks = response.get("answer_chunks", [])

    answer_text = ""
    sources = []

    if isinstance(answer_chunks, list) and answer_chunks:
        answer_text = answer_chunks[0].get("answer", "")
        sources = answer_chunks[0].get("sources", [])

    # -------------------------------------------------
    # 7️⃣ RENDER ASSISTANT RESPONSE
    # -------------------------------------------------
    with st.chat_message("assistant"):
        if answer_text:
            st.write(answer_text)
        else:
            st.write("No answer generated.")

        # if sources:
        #     st.markdown("**Sources:**")
        #     for src in sources:
        #         st.write(src)

    # -------------------------------------------------
    # 8️⃣ STORE ASSISTANT MESSAGE
    # -------------------------------------------------
    add_chat_message(
        role="assistant",
        content={"text": answer_text}
    )
