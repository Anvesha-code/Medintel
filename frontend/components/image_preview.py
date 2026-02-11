from PIL import Image
import streamlit as st
from io import BytesIO

def show_image_preview(file_bytes: bytes):
    image = Image.open(BytesIO(file_bytes))

    st.image(
        image,
        caption="🖼️ Click to zoom",
        use_column_width=True
    )
