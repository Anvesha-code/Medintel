import streamlit as st
import time

def show_progress(file_name):
    progress = st.progress(0)
    status = st.empty()

    for i in range(1, 101, 10):
        progress.progress(i)
        status.text(f"Processing {file_name}... {i}%")
        time.sleep(0.05)

    status.text(f"Completed {file_name}")
    progress.empty()
