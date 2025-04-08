import streamlit as st
import google.generativeai as genai

# Configure Gemini
API_KEY = "AIzaSyB3uidq20tP_lUTFxoN9Mvq4mgRLDSQ3Bk"  # Replace with your Gemini API Key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize memory
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "reminders" not in st.session_state:
    st.session_state.reminders = []
if "calendar_events" not in st.session_state:
    st.session_state.calendar_events = []

# Page title
st.title("🧠 AI Task Manager Chatbot")
st.write("Type things like: `Set task`, `Set reminder`, or `Add event`...")

# Display stored info
with st.expander("📋 Tasks"):
    if st.session_state.tasks:
        for task in st.session_state.tasks:
            st.write(f"✅ {task}")
    else:
        st.write("No tasks added yet.")

with st.expander("🔔 Reminders"):
    if st.session_state.reminders:
        for reminder in st.session_state.reminders:
            st.write(f"🔔 {reminder['note']} at {reminder['time']}")
    else:
        st.write("No reminders yet.")

with st.expander("📆 Calendar Events"):
    if st.session_state.calendar_events:
        for event in st.session_state.calendar_events:
            st.write(f"📅 {event['event']} on {event['date']} at {event['time']}")
    else:
        st.write("No events yet.")

# Chat interface
if prompt := st.chat_input("Say something..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    lower_prompt = prompt.lower()
    reply = ""

    if "set task" in lower_prompt:
        task = prompt.split("set task", 1)[-1].strip()
        if task:
            st.session_state.tasks.append(task)
            reply = f"✅ Task added: **{task}**"
        else:
            reply = "⚠️ Please provide a task after `set task`."

    elif "set reminder" in lower_prompt and "at" in lower_prompt:
        try:
            note = prompt.split("set reminder", 1)[-1].split("at")[0].strip()
            time = prompt.split("at", 1)[-1].strip()
            st.session_state.reminders.append({"note": note, "time": time})
            reply = f"🔔 Reminder set: **{note}** at `{time}`"
        except:
            reply = "⚠️ Format: `Set reminder <thing> at <time>`"

    elif "add event" in lower_prompt and "on" in lower_prompt and "at" in lower_prompt:
        try:
            event = prompt.split("add event", 1)[-1].split("on")[0].strip()
            date = prompt.split("on", 1)[-1].split("at")[0].strip()
            time = prompt.split("at", 1)[-1].strip()

            st.session_state.calendar_events.append({"event": event, "date": date, "time": time})
            st.session_state.reminders.append({"note": f"{event}", "time": f"{date} {time}"})
            reply = f"📅 Event added: **{event}** on `{date}` at `{time}`\n🔔 Reminder also created."
        except:
            reply = "⚠️ Format: `Add event <name> on <date> at <time>`"

    elif "show tasks" in lower_prompt:
        tasks = st.session_state.tasks
        if tasks:
            reply = "**Your tasks:**\n" + "\n".join([f"- {t}" for t in tasks])
        else:
            reply = "📭 No tasks added yet."

    elif "show reminders" in lower_prompt:
        reminders = st.session_state.reminders
        if reminders:
            reply = "**Your reminders:**\n" + "\n".join([f"- {r['note']} at {r['time']}" for r in reminders])
        else:
            reply = "🕐 No reminders set yet."

    elif "show calendar" in lower_prompt or "show events" in lower_prompt:
        events = st.session_state.calendar_events
        if events:
            reply = "**Your events:**\n" + "\n".join([f"- {e['event']} on {e['date']} at {e['time']}" for e in events])
        else:
            reply = "📆 No events yet."

    else:
        # Default Gemini response
        response = st.session_state.chat.send_message(prompt)
        reply = response.text

    # Show assistant message
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
