import streamlit as st
import google.generativeai as genai
from datetime import datetime

# Google API Key Configuration
API_KEY = "AIzaSyB3uidq20tP_lUTFxoN9Mvq4mgRLDSQ3Bk"  # Replace with your actual API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Start a new chat session if not in state
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# Task data storage
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# Streamlit App UI
st.title("📅 Task Manager Chatbot")
st.write("Hi! I'm your assistant. I can help you manage tasks, reminders, and events!")

# Chat History Display
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input Handling
if prompt := st.chat_input("What would you like to do? (e.g., Add task, Show tasks, Set reminder)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Task Parsing Logic
    def handle_task_input(user_input):
        lower_input = user_input.lower()

        # Add a task
        if "add task" in lower_input or "new task" in lower_input:
            task = user_input.split("task")[-1].strip(": ")
            st.session_state.tasks.append({"task": task, "added": str(datetime.now())})
            return f"✅ Task added: **{task}**"

        # Set reminder
        elif "remind" in lower_input or "reminder" in lower_input:
            reminder = user_input.split("remind")[-1].strip(": ")
            st.session_state.tasks.append({"task": f"Reminder: {reminder}", "added": str(datetime.now())})
            return f"⏰ Reminder set: **{reminder}**"

        # Add calendar event
        elif "event" in lower_input or "calendar" in lower_input:
            event = user_input.split("event")[-1].strip(": ")
            st.session_state.tasks.append({"task": f"Calendar Event: {event}", "added": str(datetime.now())})
            return f"📆 Calendar event added: **{event}**"

        # Show all tasks
        elif "show tasks" in lower_input or "list" in lower_input:
            if not st.session_state.tasks:
                return "📭 No tasks available right now."
            task_list = "\n".join([f"- {t['task']} (added on {t['added']})" for t in st.session_state.tasks])
            return f"📝 Here are your current tasks:\n\n{task_list}"

        else:
            return None  # If not handled manually

    custom_reply = handle_task_input(prompt)

    if custom_reply:
        st.session_state.messages.append({"role": "assistant", "content": custom_reply})
        with st.chat_message("assistant"):
            st.markdown(custom_reply)
    else:
        # Fallback to Gemini API if input is general
        response = st.session_state.chat.send_message(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"):
            st.markdown(response.text)
