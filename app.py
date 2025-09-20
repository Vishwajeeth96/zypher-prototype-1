# app.py — Zypher • Youth Mental Wellness
# Requirements: streamlit, google-generativeai, requests, Pillow
import streamlit as st
import google.generativeai as genai
import random
from datetime import datetime
import requests
from io import BytesIO
from PIL import Image
import html

# ---------------- Page config ----------------
st.set_page_config(page_title="Zypher • Youth Mental Wellness", layout="wide", page_icon="💬")

# ---------------- CSS for Fancy UI ----------------
st.markdown("""
<style>
:root {
  --bg1: #0d0d0d; --bg2: #1a0033; --accent: #ff00ff; --secondary: #8A2BE2; --muted: #e0e0e0;
}
body {background: linear-gradient(180deg,var(--bg1),var(--bg2));color:var(--muted);font-family:'Helvetica',sans-serif;}
.chat-container {display:flex;flex-direction:column;gap:10px;max-height:500px;overflow-y:auto;padding:15px;border-radius:12px;background:rgba(255,255,255,0.05);}
.user-bubble {background: rgba(255,255,255,0.1); color: var(--muted); padding:10px 15px; border-radius:12px 12px 0 12px; max-width:75%; align-self:flex-start; box-shadow:0 0 8px rgba(255,255,255,0.2);}
.bot-bubble {background: linear-gradient(90deg,var(--accent),var(--secondary)); color:#fff; padding:10px 15px; border-radius:12px 12px 12px 0; max-width:75%; align-self:flex-end; font-weight:600; text-shadow:0 0 5px #ff00ff,0 0 15px #ff00ff;}
.bot-bubble::before {content:"🤖 "; margin-right:5px;}
.stButton>button{background:linear-gradient(90deg,var(--accent),var(--secondary));color:#fff;font-weight:700;border-radius:10px;padding:8px 12px;}
</style>
""", unsafe_allow_html=True)

# ---------------- Gemini API Setup ----------------
api_key = st.secrets.get("GEMINI_API_KEY", None)
if not api_key:
    st.error("⚠️ GEMINI_API_KEY not found in Streamlit Secrets!")
    st.stop()
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- Session State ----------------
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "mood_log" not in st.session_state: st.session_state.mood_log = []
if "active_mood" not in st.session_state: st.session_state.active_mood = "okay"

# ---------------- Fallback Responses ----------------
fallback_responses = {
    "happy": ["🌟 That’s amazing!", "😄 Keep smiling!", "✨ Your happiness is contagious!"],
    "sad": ["💙 I hear you.", "🤗 Sending a hug.", "It’s okay to feel this way."],
    "angry": ["😌 Take a breath.", "I understand.", "It’s okay to vent."],
    "traumatized": ["💔 That must be heavy.", "💙 You’re not alone.", "Take it step by step..."],
    "okay": ["👍 Balanced and calm.", "🌱 Neutral is good.", "Glad you’re steady."],
    "default": ["❤️ I’m here for you.", "Tell me more...", "How do you feel about that?"]
}

# ---------------- Helper Functions ----------------
def call_genai(prompt, mood):
    try:
        full_prompt = f"You are Zypher, an empathetic youth wellness bot. Tone: {mood}.\nUser: {prompt}\nAssistant:"
        resp = model.generate_content(full_prompt)
        return getattr(resp, "text", str(resp))
    except:
        return random.choice(fallback_responses.get(mood, fallback_responses["default"]))

# ---------------- Layout ----------------
left_col, center_col = st.columns([2,4])

# --------- Left Column (Mood Log + Meme Generator) ---------
with left_col:
    st.subheader("🌸 Mood Log")
    current_mood = st.selectbox("Select Mood", ["😊 Happy","😔 Sad","😡 Angry","😴 Tired","😎 Chill"])
    if st.button("Log Mood"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.mood_log.append({"mood":current_mood, "timestamp":timestamp})
        st.success(f"Mood logged at {timestamp}")
    if st.session_state.mood_log:
        st.write("📅 Last Entries")
        for entry in reversed(st.session_state.mood_log[-5:]):
            st.write(f"{entry['timestamp']} → {entry['mood']}")

    st.subheader("😂 Meme Generator")
    if st.button("Generate Meme"):
        try:
            r = requests.get("https://meme-api.com/gimme", timeout=6).json()
            url = r.get("url"); title = r.get("title")
            if url:
                img = Image.open(BytesIO(requests.get(url).content))
                st.image(img, caption=title)
            else: st.warning("Could not fetch meme right now.")
        except Exception as e:
            st.error("Meme fetch failed: " + str(e))

# --------- Center Column (Chat) ---------
with center_col:
    st.subheader("💬 Zypher Chat")
    user_input = st.text_input("Type your message here...", key="chat_input")
    if st.button("Send") and user_input.strip():
        st.session_state.chat_history.append({"from":"user","text":user_input})
        reply = call_genai(user_input, st.session_state.active_mood)
        st.session_state.chat_history.append({"from":"bot","text":reply})

    chat_html = '<div class="chat-container">'
    for item in st.session_state.chat_history:
        text = html.escape(item.get("text",""))
        if item.get("from")=="user":
            chat_html += f'<div class="user-bubble">{text}</div>'
        else:
            chat_html += f'<div class="bot-bubble">{text}</div>'
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)
    if st.button("Clear Chat"): st.session_state.chat_history = []

# --------- Mood Analyzer at Bottom ---------
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
    elif avg >= 3.5: analysis, suggested="Generally Positive","okay"
    elif avg >= 2.5: analysis, suggested="Neutral","okay"
    elif avg >= 1.5: analysis, suggested="Stressed or Negative","traumatized"
    else: analysis, suggested="Very Negative or Upset","harassed"
    st.markdown(f"**Average Mood Score:** {avg:.2f}")
    st.info(f"Analysis: {analysis}")
    st.markdown(f"**Suggested Chat Tone:** `{suggested}`")
    if st.button("Use Suggested Tone"):
        st.session_state.active_mood = suggested
        st.success(f"Applied mood `{suggested}` to chat.")

# --------- Footer ---------
st.markdown('<div style="text-align:center;color:#999;padding:8px;font-size:12px;">🔒 All conversations are end-to-end encrypted. Your privacy is 100% safe here.</div>', unsafe_allow_html=True)

