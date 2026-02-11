import streamlit as st
from utils.session_state import (
    get_uploaded_files,
    get_chat_history,
    add_chat_message
)
from utils.api_client import query_chat, get_documents


def chat_section():
    st.subheader("💬 Chat with Your Documents")

    # -------------------------------------------------
    # 1️⃣ Fetch documents from backend (Knowledge Repo)
    # -------------------------------------------------
    try:
        documents = get_documents(user_id=5)
    except Exception as e:
        st.error(f"Failed to load documents: {e}")
        return

    if not documents:
        st.info("📚 No documents found in your Knowledge Repository. Please upload first.")
        return

    # -------------------------------------------------
    # 2️⃣ Document Selection
    # -------------------------------------------------
    doc_map = {doc["file_name"]: doc["id"] for doc in documents}

    selected_doc_name = st.selectbox(
        "📄 Select a document to chat with",
        options=list(doc_map.keys())
    )

    selected_doc_id = doc_map[selected_doc_name]

    st.success(f"Using document: {selected_doc_name}")

    # -----------------------------
    # Render Chat History
    # -----------------------------
    for msg in get_chat_history():
        role = msg["role"]
        content = msg["content"]

        with st.chat_message(role):
            st.write(content.get("text", ""))

    # -----------------------------
    # Chat Input
    # -----------------------------
    user_query = st.chat_input("Ask a question about the uploaded documents...")

    if not user_query:
        return

    with st.chat_message("user"):
        st.write(user_query)

    add_chat_message(
        role="user",
        content={"text": user_query}
    )

    # -----------------------------
    # Backend RAG Call
    # -----------------------------
    try:
        with st.spinner("Thinking..."):
            response = query_chat(
                question=user_query,
                user_id=5
            )
    except Exception as e:
        st.error(str(e))
        return

    # -----------------------------
    # ✅ CORRECT RESPONSE PARSING
    # -----------------------------
    answer_data = response.get("answer_chunks", {})
    answer_text = ""

    if isinstance(answer_data, dict):
        answer_text = answer_data.get("answer", "")

    # -----------------------------
    # Render Assistant Response
    # -----------------------------
    with st.chat_message("assistant"):
        if answer_text:
            st.write(answer_text)
        else:
            st.write("No answer generated.")

    # -----------------------------
    # Store Assistant Message
    # -----------------------------
    add_chat_message(
        role="assistant",
        content={
            "text": answer_text
        }
    )
