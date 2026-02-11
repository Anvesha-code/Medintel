import streamlit as st
import base64


def show_pdf_preview(file_bytes: bytes):
    """
    Displays PDF inline inside Streamlit using iframe.
    """
    base64_pdf = base64.b64encode(file_bytes).decode("utf-8")

    pdf_display = f"""
        <iframe
            src="data:application/pdf;base64,{base64_pdf}"
            width="100%"
            height="600px"
            type="application/pdf">
        </iframe>
    """

    st.markdown(pdf_display, unsafe_allow_html=True)
