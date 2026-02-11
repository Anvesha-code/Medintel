import streamlit as st

def show_audio(audio_bytes: bytes, transcript: list):
    st.audio(audio_bytes)

    st.subheader("📝 Transcript")
    for seg in transcript:
        if st.button(
            f"[{seg['start']}s] {seg['text']}",
            key=f"seg_{seg['start']}"
        ):
            st.info(f"Jump to {seg['start']}s")
