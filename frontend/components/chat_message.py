import streamlit as st

def render_message(role: str, text: str):
    if role == "user":
        st.chat_message("user").write(text)
    else:
        st.chat_message("assistant").write(text)
