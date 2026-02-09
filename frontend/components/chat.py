import streamlit as st
from utils.session_state import (
    get_uploaded_files,
    get_chat_history,
    add_chat_message
)
from utils.api_client import query_chat


def chat_section():
    st.subheader("💬 Chat with Your Documents")

    uploaded_files = get_uploaded_files()
    if not uploaded_files:
        st.info("Upload documents first to enable chat.")
        return

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
