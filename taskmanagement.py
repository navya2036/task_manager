import streamlit as st
import google.generativeai as genai
from datetime import datetime

# Configure Gemini
API_KEY = "AIzaSyB3uidq20tP_lUTFxoN9Mvq4mgRLDSQ3Bk"  # Replace with your actual API key
# Replace with your Gemini API Key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize session state
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "reminders" not in st.session_state:
    st.session_state.reminders = []

if "calendar" not in st.session_state:
    st.session_state.calendar = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# Streamlit UI
st.title("📅 Task Manager Chatbot - Gemini Powered")
st.write("Hi! I'm your assistant. I can manage tasks, reminders, and calendar events.")

# Display existing tasks
with st.expander("📋 View Tasks"):
    if st.session_state.tasks:
        for i, task in enumerate(st.session_state.tasks, 1):
            st.write(f"{i}. {task}")
    else:
        st.write("📭 No tasks available.")

# Display existing reminders
with st.expander("⏰ View Reminders"):
    if st.session_state.reminders:
        for rem in st.session_state.reminders:
            st.write(f"🔔 Reminder: **{rem['note']}** at `{rem['time']}`")
    else:
        st.write("🕐 No reminders set.")

# Display calendar events
with st.expander("📆 View Calendar Events"):
    if st.session_state.calendar:
        for evt in st.session_state.calendar:
            st.write(f"📅 **{evt['event']}** on `{evt['date']}` at `{evt['time']}`")
    else:
        st.write("📌 No calendar events yet.")

# Chat Input
if prompt := st.chat_input("Say something! ...."):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check for command keywords
    if "set task" in prompt.lower():
        task = prompt.split("set task", 1)[-1].strip()
        if task:
            st.session_state.tasks.append(task)
            reply = f"✅ Task added: **{task}**"
        else:
            reply = "⚠️ Please specify the task."

    elif "set reminder" in prompt.lower():
        try:
            parts = prompt.split("at")
            note = parts[0].split("set reminder", 1)[-1].strip()
            time = parts[1].strip()
            st.session_state.reminders.append({"note": note, "time": time})
            reply = f"🔔 Reminder set: **{note}** at `{time}`"
        except:
            reply = "⚠️ Please provide reminder in format: `Set reminder [note] at [time]`"

    elif "add event" in prompt.lower():
        try:
            parts = prompt.lower().split("on")
            event = parts[0].split("add event", 1)[-1].strip()
            date_time = parts[1].strip().split("at")
            date = date_time[0].strip()
            time = date_time[1].strip()
            st.session_state.calendar.append({"event": event, "date": date, "time": time})
            reply = f"📅 Event added: **{event}** on `{date}` at `{time}`"
        except:
            reply = "⚠️ Please provide event in format: `Add event [event name] on [date] at [time]`"

    elif "show tasks" in prompt.lower():
        if st.session_state.tasks:
            reply = "**Your tasks:**\n" + "\n".join([f"- {task}" for task in st.session_state.tasks])
        else:
            reply = "📭 No tasks available right now."

    elif "show reminders" in prompt.lower():
        if st.session_state.reminders:
            reply = "**Your reminders:**\n" + "\n".join([f"- {r['note']} at {r['time']}" for r in st.session_state.reminders])
        else:
            reply = "🕐 No reminders set."

    elif "show calendar" in prompt.lower():
        if st.session_state.calendar:
            reply = "**Your calendar events:**\n" + "\n".join([f"- {e['event']} on {e['date']} at {e['time']}" for e in st.session_state.calendar])
        else:
            reply = "📌 No calendar events."

    else:
        # Use Gemini response if it's not a task/reminder/calendar command
        response = st.session_state.chat.send_message(prompt)
        reply = response.text

    # Show assistant reply
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
