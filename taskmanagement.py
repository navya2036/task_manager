import streamlit as st
import google.generativeai as genai
import datetime
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av
import queue
import google.cloud.speech as speech
import os

# --- CONFIG ---
API_KEY = "AIzaSyB3uidq20tP_lUTFxoN9Mvq4mgRLDSQ3Bk"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- STATE INIT ---
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "reminders" not in st.session_state:
    st.session_state.reminders = []

if "events" not in st.session_state:
    st.session_state.events = []

# --- TITLE ---
st.title("🤖 Chatbot - Your AI Assistant with Voice")
st.write("Welcome! You can chat, add/view tasks, reminders, and events. Now with 🗣️ voice support!")

# --- SHOW MESSAGES ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- PARSE TEXT ---
def handle_input(text):
    text = text.lower()
    if text.startswith("add task"):
        task = text.replace("add task", "").strip()
        st.session_state.tasks.append(task)
        return f"✅ Task added: {task}"
    
    elif text == "show tasks":
        if not st.session_state.tasks:
            return "📭 No tasks available right now."
        return "📋 Tasks:\n" + "\n".join(f"- {t}" for t in st.session_state.tasks)
    
    elif text.startswith("set reminder"):
        reminder = text.replace("set reminder", "").strip()
        st.session_state.reminders.append(reminder)
        return f"🔔 Reminder set: {reminder}"
    
    elif text == "show reminders":
        if not st.session_state.reminders:
            return "📭 No reminders set."
        return "🔔 Reminders:\n" + "\n".join(f"- {r}" for r in st.session_state.reminders)
    
    elif text.startswith("add event"):
        event = text.replace("add event", "").strip()
        st.session_state.events.append(event)
        return f"📅 Event added: {event}"
    
    elif text == "show events":
        if not st.session_state.events:
            return "📭 No events scheduled."
        return "📅 Events:\n" + "\n".join(f"- {e}" for e in st.session_state.events)
    
    else:
        response = st.session_state.chat.send_message(text)
        return response.text

# --- TEXT INPUT ---
if prompt := st.chat_input("Say something! (or use voice input 👇)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reply = handle_input(prompt)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

# --- VOICE ASSISTANT ---
st.subheader("🎤 Voice Assistant")

audio_queue = queue.Queue()

class AudioProcessor(AudioProcessorBase):
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio_queue.put(frame.to_ndarray().flatten().tolist())
        return frame

webrtc_streamer(
    key="voice",
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)

if st.button("🎙️ Transcribe Voice Input"):
    client = speech.SpeechClient()
    audio_content = b"".join(
        [bytes(int(sample).to_bytes(2, 'little', signed=True)) for sample in audio_queue.queue]
    )
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
        language_code="en-US",
    )

    try:
        response = client.recognize(config=config, audio=audio)
        for result in response.results:
            transcribed_text = result.alternatives[0].transcript
            st.success(f"🗣️ You said: {transcribed_text}")

            st.session_state.messages.append({"role": "user", "content": transcribed_text})
            reply = handle_input(transcribed_text)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
    except Exception as e:
        st.error(f"⚠️ Voice recognition failed: {e}")
