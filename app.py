import os
import random
from datetime import datetime
import streamlit as st
import google.generativeai as genai

# ---------------- Page Config ----------------
st.set_page_config(page_title="Zypher • Youth Mental Wellness", page_icon="💬", layout="wide")

# ---------------- CSS for Fancy UI ----------------
st.markdown("""
<style>
:root {
  --bg1: #0d0d0d;
  --bg2: #1a0033;
  --accent: #ff00ff;
  --secondary: #8A2BE2;
  --muted: #e0e0e0;
}
body {
  background: linear-gradient(180deg, var(--bg1), var(--bg2));
  color: var(--muted);
  font-family: 'Helvetica', sans-serif;
}
.chat-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 500px;
  overflow-y: auto;
  padding: 15px;
  border-radius: 12px;
  background: rgba(255,255,255,0.05);
}
.user-bubble {
  background: rgba(255,255,255,0.1);
  color: var(--muted);
  padding: 10px 15px;
  border-radius: 12px 12px 0 12px;
  max-width: 75%;
  align-self: flex-start;
  box-shadow: 0 0 8px rgba(255,255,255,0.2);
}
.bot-bubble {
  background: linear-gradient(90deg, var(--accent), var(--secondary));
  color: #fff;
  padding: 10px 15px;
  border-radius: 12px 12px 12px 0;
  max-width: 75%;
  align-self: flex-end;
  font-weight: 600;
  text-shadow: 0 0 5px #ff00ff, 0 0 15px #ff00ff;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Gemini Setup ----------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-pro")

# ---------------- Fallback Responses ----------------
fallback_responses = {
    "happy": [
        "🌟 That’s amazing!", "😄 Keep smiling!", "✨ Your happiness is contagious!"
    ],
    "sad": [
        "💙 I hear you.", "🤗 Sending a hug.", "It’s okay to feel this way."
    ],
    "angry": [
        "😌 Take a breath.", "I understand your frustration.", "It’s okay to vent."
    ],
    "traumatized": [
        "💔 That must be heavy.", "💙 You’re not alone.", "Take it step by step..."
    ],
    "okay": [
        "👍 Balanced and calm.", "🌱 Neutral is good.", "Glad you’re steady."
    ],
    "default": [
        "❤️ I’m here for you.", "Tell me more...", "How do you feel about that?"
    ]
}

# ---------------- Session State ----------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "mood_logs" not in st.session_state:
    st.session_state["mood_logs"] = []

if "active_mood" not in st.session_state:
    st.session_state["active_mood"] = "default"

# ---------------- Sidebar ----------------
with st.sidebar:
    st.title("💬 Zypher AI")
    st.caption("Youth Mental Wellness Chatbot")

    # Mood selector
    mood = st.radio(
        "How are you feeling?",
        ["happy", "sad", "angry", "traumatized", "okay", "default"],
        index=["happy","sad","angry","traumatized","okay","default"].index(st.session_state["active_mood"])
    )
    st.session_state["active_mood"] = mood

    # Log mood with timestamp
    if not st.session_state["mood_logs"] or st.session_state["mood_logs"][-1]["mood"] != mood:
        st.session_state["mood_logs"].append({
            "mood": mood,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    st.subheader("🕒 Mood Log")
    for log in st.session_state["mood_logs"]:
        st.write(f"{log['timestamp']} — **{log['mood']}**")

    if st.button("Clear Chat"):
        st.session_state["messages"] = []
        st.success("Chat history cleared ✅")

# ---------------- Main Chat ----------------
st.title("🌱 Zypher Wellness Chat")
chat_html = '<div class="chat-container">'
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        chat_html += f'<div class="user-bubble">{msg["content"]}</div>'
    else:
        chat_html += f'<div class="bot-bubble">{msg["content"]}</div>'
chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

# ---------------- Chat Input ----------------
if user_input := st.chat_input("Type your message..."):
    st.session_state["messages"].append({"role": "user", "content": user_input})

    try:
        response = model.generate_content(user_input)
        reply = response.text
    except Exception:
        reply = random.choice(fallback_responses.get(st.session_state["active_mood"], fallback_responses["default"]))

    st.session_state["messages"].append({"role": "bot", "content": reply})
    st.experimental_rerun()
