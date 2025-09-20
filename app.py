# app.py — Zypher • Youth Mental Wellness
# Requirements: streamlit, google-generativeai, requests, Pillow

import streamlit as st
import google.generativeai as genai
from datetime import datetime
import random
import requests
from io import BytesIO
from PIL import Image

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="Zypher - Youth Mental Wellness",
    page_icon="🌿",
    layout="wide",
)

# ---------------------------
# Gemini API Setup
# ---------------------------
api_key = st.secrets.get("GEMINI_API_KEY", None)
if api_key:
    genai.configure(api_key=api_key)
else:
    st.sidebar.error("⚠️ Gemini API key not found in secrets!")
    st.stop()

# ---------------------------
# Fallback Responses
# ---------------------------
fallback_responses = {
    "happy": ["That’s amazing! 🌸", "Keep shining today! ✨", "Happiness looks good on you! 💖"],
    "sad": ["I hear you 💙", "It’s okay to not feel okay 🌧️", "Sending you a virtual hug 🤗"],
    "angry": ["Take a deep breath 🧘", "It’s okay to vent 💢", "Want a quick calming exercise?"],
    "neutral": ["Got it. I’m listening 👂", "I understand. Tell me more…", "Thanks for sharing 💭"],
}

# ---------------------------
# Session State
# ---------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "mood_log" not in st.session_state:
    st.session_state.mood_log = []

# ---------------------------
# Chatbot Response Function
# ---------------------------
def get_bot_response(user_input, mood="neutral"):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(user_input)
        return response.text
    except:
        return random.choice(fallback_responses.get(mood, ["I’m here for you. 💙"]))

# ---------------------------
# Sidebar - Mood Log + Meme Generator
# ---------------------------
with st.sidebar:
    st.header("🌸 Mood Log")
    current_mood = st.radio("How are you feeling?", ["happy","sad","angry","neutral"], horizontal=True)
    if st.button("Log Mood"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.mood_log.append((current_mood, timestamp))
        st.success(f"Mood '{current_mood}' logged at {timestamp}")

    if st.session_state.mood_log:
        st.subheader("📅 Previous Entries")
        for mood, ts in reversed(st.session_state.mood_log[-5:]):
            st.write(f"{ts} → {mood}")

    st.header("😂 Meme Generator")
    if st.button("Generate Meme"):
        try:
            r = requests.get("https://meme-api.com/gimme", timeout=6).json()
            url = r.get("url")
            title = r.get("title")
            if url:
                img = Image.open(BytesIO(requests.get(url).content))
                st.image(img, caption=title)
            else:
                st.warning("Could not fetch meme right now.")
        except Exception as e:
            st.error("Meme fetch failed: " + str(e))

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

# ---------------------------
# Mood Analyzer
# ---------------------------
st.subheader("📋 Mood Analyzer")
questions = [
    {"q":"How have you been feeling today?","opts":["Very good","Good","Neutral","Bad","Very bad"]},
    {"q":"How motivated are you?","opts":["Very motivated","Somewhat motivated","Neutral","Little motivated","Not motivated at all"]},
    {"q":"How well did you sleep?","opts":["Very well","Well","Average","Poorly","Very poorly"]},
    {"q":"Rate your stress level:","opts":["Very low","Low","Moderate","High","Very high"]},
    {"q":"Connected with others recently?","opts":["Very connected","Somewhat connected","Neutral","Somewhat disconnected","Very disconnected"]}
]

with st.form("mood_form"):
    answers=[]
    for i,qq in enumerate(questions):
        answers.append(st.radio(qq["q"], qq["opts"], index=2, key=f"q{i}"))
    submit = st.form_submit_button("Analyze Mood")

if submit:
    score_map = {"Very good":5,"Good":4,"Neutral":3,"Bad":2,"Very bad":1,
                 "Very motivated":5,"Somewhat motivated":4,"Neutral":3,"Little motivated":2,"Not motivated at all":1,
                 "Very well":5,"Well":4,"Average":3,"Poorly":2,"Very poorly":1,
                 "Very low":5,"Low":4,"Moderate":3,"High":2,"Very high":1,
                 "Very connected":5,"Somewhat connected":4,"Neutral":3,"Somewhat disconnected":2,"Very disconnected":1}
    total = sum(score_map.get(a,3) for a in answers)
    avg = total / len(questions)
    if avg >= 4.5: analysis, suggested="Very Positive and Happy","happy"
    elif avg >= 3.5: analysis, suggested="Generally Positive","neutral"
    elif avg >= 2.5: analysis, suggested="Neutral","neutral"
    elif avg >= 1.5: analysis, suggested="Stressed or Negative","sad"
    else: analysis, suggested="Very Negative or Upset","angry"

    st.markdown(f"**Average Mood Score:** {avg:.2f}")
    st.info(f"Analysis: {analysis}")
    st.markdown(f"**Suggested Chat Tone:** `{suggested}`")
    if st.button("Use Suggested Tone"):
        current_mood = suggested
        st.success(f"Applied mood `{suggested}` to chat.")
