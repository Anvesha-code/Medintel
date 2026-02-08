import streamlit as st
from components.layout import render_layout
from utils.session_state import init_session


# -----------------------------
# App Configuration
# -----------------------------
st.set_page_config(
    page_title="MedIntel",
    page_icon="🩺",
    layout="wide"
)


def main():
    # 🔹 Initialize session state once
    init_session()

    # 🔹 App Header (global)
    st.markdown(
        "<h1 style='margin-bottom:0'>🩺 MedIntel</h1>"
        "<p style='color:gray;margin-top:0'>AI-powered medical document intelligence</p>",
        unsafe_allow_html=True
    )

    # 🔹 Render main layout
    render_layout()


# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    main()
