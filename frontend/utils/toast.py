import streamlit as st

def success(message: str):
    st.toast(f"✅ {message}")

def error(message: str):
    st.toast(f"❌ {message}")
