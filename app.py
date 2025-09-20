# app.py — Zypher • Youth Mental Wellness
# Requirements: streamlit, google-generativeai

import streamlit as st
import google.generativeai as genai
from datetime import datetime
import random

# ---------------------------
# Configure page
# ---------------------------
st.set_page_config(
    page_title="Zypher - Youth Mental Wellness",
    page_icon="🌿",
    layout="wide",
)

# ---------------------------
# Load Gemini API Key
# ---------------------------
api_key = st.secrets.get("GEMINI_API_KEY", None)
if api_key:
    genai.configure(api_key=api_key)
else:
    st.sidebar.error("⚠️ Gemini API key not found in secrets!")
    st.stop()

# ---------------------------
# Fallback Responses (if API fails)
# ---------------------------
fallback_responses = {
    "happy": [
        "That’s amazing! 🌸 Keep shining today!",
        "I’m really glad you’re feeling good. ✨",
        "Happiness looks good on you! 💖",
    ],
    "sad": [
        "I hear you 💙, tough times don’t last forever.",
        "It’s okay to not feel okay sometimes 🌧️.",
        "Sending you a virtual hug 🤗.",
    ],
    "angry": [
        "Take a deep breath 🧘, I’m here for you.",
        "It’s okay to let it out 💢.",
        "Want to try calming down with a quick exercise?",
    ],
    "neutral": [
        "Got it. I’m listening 👂.",
        "I understand. Tell me more…",
        "Thanks for sharing that with me 💭.",
    ],
}

# ---------------------------
# Initialize session state
# ---------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "mood_log" not in st.session_state:
    st.session_state.mood_log = []

# ---------------------------
# Chatbot response function
# ---------------------------
def get_bot_response(user_input, mood="neutral"):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        # Use fallback response
        return random.choice(fallback_responses.get(mood, ["I’m here for you. 💙"]))

# ---------------------------
# Sidebar - Mood logging
# ---------------------------
with st.sidebar:
    st.header("🌸 Mood Log")
    current_mood = st.radio(
        "How are you feeling?",
        ["happy", "sad", "angry", "neutral"],
        horizontal=True,
    )
    if st.button("Log Mood"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.mood_log.append((current_mood, timestamp))
        st.success(f"Mood '{current_mood}' logged at {timestamp}")

    if st.session_state.mood_log:
        st.subheader("📅 Previous Entries")
        for mood, ts in reversed(st.session_state.mood_log[-5:]):
            st.write(f"{ts} → {mood}")

# ---------------------------
# Main Chat Interface
# ---------------------------
st.title("🌿 Zypher — Youth Mental Wellness Chatbot")

user_input = st.chat_input("Type your message...")
if user_input:
    # Save user input
    st.session_state.chat_history.append(("user", user_input))

    # Generate bot response
    bot_reply = get_bot_response(user_input, current_mood)
    st.session_state.chat_history.append(("bot", bot_reply))

# Display chat history
for role, text in st.session_state.chat_history:
    if role == "user":
        with st.chat_message("user"):
            st.markdown(f"👤 **You:** {text}")
    else:
        with st.chat_message("assistant"):
            st.markdown(f"🤖 **Zypher:** {text}")
