import streamlit as st

def render_sources(sources: list):
    st.markdown("### 📚 Sources")

    for src in sources:
        with st.expander(
            f"{src['file_name']} | Page {src.get('page')} | Chunk {src['chunk_id']}"
        ):
            st.write(src.get("text", ""))
