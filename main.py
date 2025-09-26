import os
import streamlit as st
import speech_recognition as sr
from pathlib import Path
from st_audiorec import st_audiorec  

# --- Custom CSS ---
st.markdown("""
    <style>
    /* Dark purple background */
    body, .stApp {
        background: linear-gradient(135deg, #2d0036 0%, #4b006e 100%);
    }
    /* Make all Streamlit buttons pink */
    button, .stButton>button {
        background-color: #ff69b4 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
        box-shadow: 0 2px 8px rgba(255,105,180,0.15);
        transition: background 0.2s;
    }
    button:hover, .stButton>button:hover {
        background-color: #ff1493 !important;
        color: #fff !important;
    }
    /* Optional: Make expander headers pink */
    .streamlit-expanderHeader {
        color: #ff69b4 !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Directory to store uploaded & recorded audio
AUDIO_DIR = Path("recordings")
AUDIO_DIR.mkdir(exist_ok=True)

st.title("🎙️ Speech-to-Text Transcription Tool")

# ===============================
# 1. Upload audio
# ===============================
uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "flac"])

if uploaded_file:
    file_path = AUDIO_DIR / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"Uploaded & saved: {file_path.name}")

# ===============================
# 2. Record audio with mic
# ===============================
st.subheader("🎤 Record Audio")
wav_audio_data = st_audiorec()

if wav_audio_data is not None:
    file_path = AUDIO_DIR / "recorded_audio.wav"
    with open(file_path, "wb") as f:
        f.write(wav_audio_data)
    st.audio(file_path, format="audio/wav")
    st.success("Recording saved as recorded_audio.wav")

# ===============================
# 3. Show stored recordings
# ===============================
st.subheader("Stored Recordings")
files = list(AUDIO_DIR.glob("*"))

if not files:
    st.info("No recordings found yet.")
else:
    for idx, file in enumerate(files):
        with st.expander(f"🎵 {file.name}", expanded=False):
            st.audio(str(file))

            # Convert to text
            if st.button(f"Convert {file.name} to Text", key=f"convert_{idx}"):
                recognizer = sr.Recognizer()
                with sr.AudioFile(str(file)) as source:
                    audio_data = recognizer.record(source)

                try:
                    text = recognizer.recognize_google(audio_data)
                    st.success("Transcription:")
                    st.write(text)

                    # Save transcription
                    txt_file = file.with_suffix(".txt")
                    with open(txt_file, "w", encoding="utf-8") as f:
                        f.write(text)

                    st.download_button(
                        "📥 Download Text File",
                        text,
                        file_name=txt_file.name,
                        key=f"dl_{idx}"
                    )
                except sr.UnknownValueError:
                    st.error("Could not understand the audio.")
                except sr.RequestError:
                    st.error("Speech Recognition service unavailable.")

            # Delete recording
            if st.button(f"🗑️ Delete {file.name}", key=f"delete_{idx}"):
                try:
                    os.remove(file)  # delete audio
                    txt_file = file.with_suffix(".txt")
                    if txt_file.exists():
                        os.remove(txt_file)  # delete transcription if exists
                    st.warning(f"{file.name} deleted!")
                    st.experimental_rerun()  # refresh the app
                except Exception as e:
                    st.error(f"Error deleting file: {e}")
