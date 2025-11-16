import streamlit as st
import pyttsx3


def get_voice_options(engine):
    """Retrieve available voices from pyttsx3 engine."""
    voices = engine.getProperty("voices")
    voice_options = []
    for voice in voices:
        voice_options.append(
            {"name": voice.name, "id": voice.id, "gender": "male" if "male" in voice.name.lower() else "female"})
    return voice_options

# using texttospeach  module

def generate_tts_with_options(text, voice_id, rate, filename):
    """
    Generate text-to-speech audio with specific voice and rate options and save it as an MP3 file.
    """
    engine = pyttsx3.init()
    engine.setProperty("voice", voice_id)  # Set selected voice
    engine.setProperty("rate", rate)  # Set speech rate
    engine.save_to_file(text, filename)  # Save to file
    engine.runAndWait()

#
# Streamlit App
st.title("Text-to-Speech Converter with Voice Customization")
st.write("Convert text to speech with options for voice gender, speed, and language.")

# Input for text
text = st.text_area("Enter the text (Hindi/English):", height=200, placeholder="Type or paste your text here...")

# Initialize pyttsx3 engine and fetch voice options
engine = pyttsx3.init()
voice_options = get_voice_options(engine)

# Language selection
language = st.selectbox("Select Language:", options=["English", "Hindi"])

# Voice selection
voice_gender = st.radio("Select Voice Gender:", options=["Male", "Female"])
filtered_voices = [voice for voice in voice_options if voice["gender"] == voice_gender.lower()]

selected_voice = st.selectbox("Select Voice Variant:", options=filtered_voices, format_func=lambda x: x["name"])

# Voice speed selection
voice_speed = st.slider("Select Voice Speed (Words per Minute):", min_value=100, max_value=300, value=150)

# Generate and play audio
if st.button("Convert to Speech"):
    if text.strip():
        filename = "speech_output.mp3"
        generate_tts_with_options(
            text=text.strip(),
            voice_id=selected_voice["id"],
            rate=voice_speed,
            filename=filename,
        )

        # Provide option to download the file
        with open(filename, "rb") as audio_file:
            st.audio(audio_file.read(), format="audio/mp3")
            st.download_button(label="Download Audio File", data=audio_file, file_name="speech_output.mp3",
                               mime="audio/mp3")

        st.success("Audio file generated successfully!")
    else:
        st.warning("Please enter text to convert into speech.")