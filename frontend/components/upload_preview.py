import streamlit as st
from PIL import Image
import io

def show_preview(file_type, file_bytes, preview_text=None):
    if file_type == "image":
        image = Image.open(io.BytesIO(file_bytes))
        st.image(image, caption="Image Preview", width=250)

    elif file_type == "audio":
        st.audio(file_bytes)
        if preview_text:
            st.caption(f"Transcript snippet: {preview_text[:200]}...")

    else:
        if preview_text:
            st.text_area(
                "Text Preview (First Section)",
                preview_text[:500],
                height=150
            )
