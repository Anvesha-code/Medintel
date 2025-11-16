import streamlit as st
from gtts import gTTS
import os

st.title("Text-to-Speech Converter (Streamlit Cloud Compatible)")
st.write("Convert text to speech with options for gender, language, and speed.")

# Input text
text = st.text_area("Enter the text (Hindi/English):", height=200, placeholder="Type your text here...")

# Language selection
language = st.selectbox("Select Language:", ["English", "Hindi"])

# Gender selection (Note: gTTS doesn't provide real gender control, but we simulate using accents)
voice_gender = st.radio("Select Voice Gender:", ["Male", "Female"])

# Speed selection (gTTS supports only 'slow=True/False')
voice_speed = st.slider("Voice Speed:", 1, 5, 3)
slow_speed = True if voice_speed <= 2 else False

# Accent Mapping (simulated gender difference)
def get_tts_voice(text, language, gender, slow_speed):
    lang_map = {
        "English": "en",
        "Hindi": "hi"
    }
    lang_code = lang_map[language]

    # Simulated gender-based accents
    if language == "English":
        if gender == "Male":
            tts = gTTS(text=text, lang=lang_code, slow=slow_speed, tld="co.uk")
        else:
            tts = gTTS(text=text, lang=lang_code, slow=slow_speed, tld="com")
    else:
        # Hindi has only one voice but we keep structure same
        tts = gTTS(text=text, lang=lang_code, slow=slow_speed)
    return tts


# Convert Button
if st.button("Convert to Speech"):
    if text.strip():

        file_path = "speech_output.mp3"

        # Generate audio
        tts = get_tts_voice(text, language, voice_gender, slow_speed)
        tts.save(file_path)

        # Play audio
        audio_file = open(file_path, "rb")
        st.audio(audio_file.read(), format="audio/mp3")

        # Download link
        st.download_button(
            label="Download Audio File",
            data=open(file_path, "rb"),
            file_name="speech_output.mp3",
            mime="audio/mp3"
        )

        st.success("Speech generated successfully!")
    else:
        st.warning("Please enter text before converting.")
