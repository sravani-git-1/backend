import streamlit as st
import requests
import tempfile
import google.generativeai as genai
from datetime import datetime
from gtts import gTTS

# ==============================
# CONFIG
# ==============================
N8N_WEBHOOK_URL = "https://sravani1.app.n8n.cloud/webhook/gemini_voice_test"
genai.configure(api_key="AIzaSyCAYU6-vJsZQrGbYVi2TnH7Pq6-_Y4E-KM")

model = genai.GenerativeModel("gemini-1.5-flash")

# ==============================
# SESSION STATE INIT
# ==============================
if "mode" not in st.session_state:
    st.session_state.mode = None

if "voice_user" not in st.session_state:
    st.session_state.voice_user = ""

if "voice_response" not in st.session_state:
    st.session_state.voice_response = ""

if "text_user" not in st.session_state:
    st.session_state.text_user = ""

if "text_response" not in st.session_state:
    st.session_state.text_response = ""

if "voice_played" not in st.session_state:
    st.session_state.voice_played = False

# ==============================
# SPEECH → TEXT (Gemini)
# ==============================
def speech_to_text(audio_bytes):
    response = model.generate_content([
        {"mime_type": "audio/wav", "data": audio_bytes},
        "Convert this speech to text"
    ])
    return response.text.strip()

# ==============================
# SEND TO N8N
# ==============================
def send_to_n8n(message):
    try:
        res = requests.post(N8N_WEBHOOK_URL, json={"message": message})

        if not res.text:
            return "❌ Empty response"

        try:
            data = res.json()
            return data.get("response") or data.get("output") or data.get("text") or str(data)
        except:
            return res.text

    except Exception as e:
        return f"❌ Error: {str(e)}"

# ==============================
# TEXT → SPEECH (AUTO PLAY ONCE)
# ==============================
def speak_once(text):
    if not text.strip():
        return

    tts = gTTS(text=text, lang="en")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)

        audio_bytes = open(fp.name, "rb").read()

        st.audio(audio_bytes, format="audio/mp3")

# ==============================
# UI
# ==============================
st.set_page_config(layout="wide")

st.markdown("""
<h1 style='text-align:center;'>🎤 Smart ERP Assistant</h1>
<p style='text-align:center;color:gray;'>Voice + Text AI Assistant</p>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# ==============================
# 🎙 VOICE SECTION
# ==============================
with col1:
    st.markdown("## 🎙 Voice Assistant")

    audio = st.audio_input("Speak now")

    if audio:
        st.session_state.mode = "voice"
        st.session_state.voice_played = False  # reset playback

        audio_bytes = audio.read()
        user_text = speech_to_text(audio_bytes)

        st.session_state.voice_user = user_text

        response = send_to_n8n(user_text)
        st.session_state.voice_response = response

# ==============================
# 💬 TEXT SECTION
# ==============================
with col2:
    st.markdown("## 💬 Text Assistant")

    user_input = st.text_input("Enter message")

    auto_speak = st.checkbox("🔊 Speak response")

    if st.button("Send"):
        if user_input.strip():
            st.session_state.mode = "text"

            response = send_to_n8n(user_input)

            st.session_state.text_user = user_input
            st.session_state.text_response = response

# ==============================
# DISPLAY RESULTS
# ==============================

# 🎙 VOICE OUTPUT
if st.session_state.mode == "voice":

    if st.session_state.voice_user:
        st.write("### 🧑 You said:")
        st.write(st.session_state.voice_user)

    if st.session_state.voice_response:
        st.write("### 🤖 AI Response:")
        st.write(st.session_state.voice_response)

        # ✅ AUTO PLAY ONLY ONCE
        if not st.session_state.voice_played:
            speak_once(st.session_state.voice_response)
            st.session_state.voice_played = True


# 💬 TEXT OUTPUT
if st.session_state.mode == "text":

    if st.session_state.text_user:
        st.write("### 🧑 You said:")
        st.write(st.session_state.text_user)

    if st.session_state.text_response:
        st.write("### 🤖 AI Response:")
        st.write(st.session_state.text_response)