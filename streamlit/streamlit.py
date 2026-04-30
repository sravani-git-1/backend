import streamlit as st
import requests
import tempfile
import google.generativeai as genai
from faster_whisper import WhisperModel
from datetime import datetime
from gtts import gTTS

# ==============================
# CONFIG
# ==============================
N8N_WEBHOOK_URL = "https://sravani1.app.n8n.cloud/webhook/gemini_voice_test"

# ✅ DIRECT API KEY (no secrets file needed)
genai.configure(api_key="AIzaSyCAYU6-vJsZQrGbYVi2TnH7Pq6-_Y4E-KM")

# ✅ FIXED MODEL NAME
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# ==============================
# LOAD WHISPER
# ==============================
@st.cache_resource
def load_model():
    return WhisperModel("tiny", device="cpu", compute_type="int8")

whisper_model = load_model()

# ==============================
# SPEECH → TEXT
# ==============================
def speech_to_text(audio_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        audio_path = f.name

    segments, _ = whisper_model.transcribe(audio_path)
    return " ".join([seg.text for seg in segments]).strip()

# ==============================
# SEND TO N8N
# ==============================
def send_to_n8n(message):
    try:
        res = requests.post(N8N_WEBHOOK_URL, json={"message": message})

        if not res.text:
            return "❌ Empty response from server"

        try:
            data = res.json()
            return data.get("response") or data.get("output") or data.get("text") or str(data)
        except:
            return res.text

    except Exception as e:
        return f"❌ Error: {str(e)}"

# ==============================
# TEXT → SPEECH
# ==============================
def speak(text):
    if not text.strip():
        return

    tts = gTTS(text=text, lang="en")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        audio_file = open(fp.name, "rb")
        st.audio(audio_file.read(), format="audio/mp3")

# ==============================
# LOG
# ==============================
def save_chat(user, ai):
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}]\nUser: {user}\nAI: {ai}\n{'-'*40}\n")

# ==============================
# UI
# ==============================
st.set_page_config(layout="wide")

st.markdown("""
<h1 style='text-align:center;'>🎤 Smart ERP Assistant</h1>
<p style='text-align:center;color:gray;'>Voice + AI Assistant</p>
""", unsafe_allow_html=True)

# ==============================
# SESSION STATE
# ==============================
if "text_user" not in st.session_state:
    st.session_state.text_user = ""
if "text_response" not in st.session_state:
    st.session_state.text_response = ""

col1, col2 = st.columns(2)

# ==============================
# VOICE
# ==============================
with col1:
    st.markdown("## 🎙 Voice Assistant")

    audio = st.audio_input("Speak now")

    if audio:
        audio_bytes = audio.read()

        user_text = speech_to_text(audio_bytes)

        st.write("### 🧑 You said:")
        st.write(user_text)

        response = send_to_n8n(user_text)

        st.write("### 🤖 AI Response:")
        st.write(response)

        speak(response)
        save_chat(user_text, response)

# ==============================
# TEXT
# ==============================
with col2:
    st.markdown("## 💬 Text Assistant")

    user_input = st.text_input("Enter message")

    auto_speak = st.checkbox("🔊 Speak response")

    if st.button("Send"):
        if user_input.strip():
            response = send_to_n8n(user_input)

            st.session_state.text_user = user_input
            st.session_state.text_response = response

            save_chat(user_input, response)
        else:
            st.warning("Enter message")

    if st.session_state.text_user:
        st.write("### 🧑 You said:")
        st.write(st.session_state.text_user)

    if st.session_state.text_response:
        st.write("### 🤖 AI Response:")
        st.write(st.session_state.text_response)

        if auto_speak:
            speak(st.session_state.text_response)