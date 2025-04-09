import streamlit as st
import google.generativeai as genai

# Set your Gemini API key
API_KEY = "AIzaSyB3uidq20tP_lUTFxoN9Mvq4mgRLDSQ3Bk"  # Replace with your actual API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Start Gemini chat session
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "reminders" not in st.session_state:
    st.session_state.reminders = []

if "events" not in st.session_state:
    st.session_state.events = []

# App Title
st.title("🤖 Task Manager Chatbot")
st.write("Welcome! I can help you manage tasks, reminders, and events.")

# Expander UI for stored data
with st.expander("📝 Tasks"):
    if st.session_state.tasks:
        for task in st.session_state.tasks:
            st.write(f"✅ {task}")
    else:
        st.write("No tasks yet.")

with st.expander("🔔 Reminders"):
    if st.session_state.reminders:
        for rem in st.session_state.reminders:
            st.write(f"🔔 {rem['note']} at {rem['time']}")
    else:
        st.write("No reminders yet.")

with st.expander("📅 Events"):
    if st.session_state.events:
        for evt in st.session_state.events:
            st.write(f"📅 {evt['title']} on {evt['date']}")
    else:
        st.write("No events yet.")

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input prompt
if prompt := st.chat_input("Say something!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    lower_prompt = prompt.lower()
    reply = ""

    # Task logic
    if "set task" in lower_prompt:
        task = prompt.lower().split("set task", 1)[-1].strip()
        if task:
            st.session_state.tasks.append(task)
            reply = f"✅ Task added: *{task}*"
        else:
            reply = "⚠ Please provide a task. Example: Set task complete homework"

    elif "show tasks" in lower_prompt:
        tasks = st.session_state.tasks
        if tasks:
            reply = "📝 Your Tasks:\n" + "\n".join([f"- {t}" for t in tasks])
        else:
            reply = "📭 No tasks added yet."

    # Reminder logic
    elif "set reminder" in lower_prompt:
        reminder_part = prompt.lower().split("set reminder", 1)[-1].strip()
        if "at" in reminder_part:
            note = reminder_part.split("at")[0].strip()
            time = reminder_part.split("at")[1].strip()
            if note and time:
                st.session_state.reminders.append({"note": note, "time": time})
                reply = f"🔔 Reminder set: *{note}* at {time}"
            else:
                reply = "⚠ Format should be: Set reminder <note> at <time>"
        else:
            reply = "⚠ Include time with at. Example: Set reminder drink water at 4pm"

    elif "show reminders" in lower_prompt:
        reminders = st.session_state.reminders
        if reminders:
            reply = "🔔 Your Reminders:\n" + "\n".join(
                [f"- *{r['note']}* at {r['time']}" for r in reminders]
            )
        else:
            reply = "📭 No reminders set yet."

    # Event logic
    elif "add event" in lower_prompt:
        event_part = prompt.lower().split("add event", 1)[-1].strip()
        if "on" in event_part:
            title = event_part.split("on")[0].strip()
            date = event_part.split("on")[1].strip()
            if title and date:
                st.session_state.events.append({"title": title, "date": date})
                reply = f"📅 Event added: *{title}* on {date}"
            else:
                reply = "⚠ Format should be: Add event <title> on <date>"
        else:
            reply = "⚠ Include date with on. Example: Add event demo day on April 12"

    elif "show events" in lower_prompt:
        events = st.session_state.events
        if events:
            reply = "📅 Your Events:\n" + "\n".join(
                [f"- *{e['title']}* on {e['date']}" for e in events]
            )
        else:
            reply = "📭 No events added yet."

    # If no match, fall back to Gemini
    else:
        response = st.session_state.chat.send_message(prompt)
        reply = response.text

    # Show assistant reply
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
