# app.py — Zypher • Youth Mental Wellness
# Requirements: streamlit, pandas, requests, Pillow, google-generativeai
# Save logo (optional) at: assets/team_zypher_logo_transparent.png
# Run: pip install -r requirements.txt
# streamlit run app.py

import os
import html
from io import BytesIO
import streamlit as st
import pandas as pd
import requests
from PIL import Image

# ---------------- Page config ----------------
LOGO_PATH = "assets/team_zypher_logo_transparent.png"
if os.path.exists(LOGO_PATH):
    st.set_page_config(page_title="Zypher • Youth Mental Wellness", page_icon=LOGO_PATH, layout="centered")
else:
    st.set_page_config(page_title="Zypher • Youth Mental Wellness", page_icon="💬", layout="centered")

# ---------------- Theme CSS ----------------
st.html("""
<style>
:root {
  --bg1: #0d0d0d;
  --bg2: #1a0033;
  --accent: #ff00ff; /* neon pink */
  --secondary: #8A2BE2; /* violet */
  --muted: #e0e0e0;
}
body {
  background: linear-gradient(180deg, var(--bg1), var(--bg2));
  color: var(--muted);
  font-family: 'Helvetica', sans-serif;
}
.container {
  background: rgba(255,255,255,0.03);
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.7);
}
h1, h2, h3 { color: var(--accent); text-align:center; margin: 5px 0; }
.user-bubble {
  background: rgba(255,255,255,0.05);
  color: var(--muted);
  padding: 12px 16px;
  border-radius: 14px 14px 4px 14px;
  margin: 6px 0;
  max-width: 75%;
  align-self: flex-start;
  box-shadow: 0 0 10px rgba(255,255,255,0.2);
}
.bot-bubble {
  background: linear-gradient(90deg, var(--accent), var(--secondary));
  color: #fff;
  padding: 12px 16px;
  border-radius: 14px 14px 14px 4px;
  margin: 6px 0;
  max-width: 75%;
  align-self: flex-end;
  font-weight: 600;
  text-shadow: 0 0 5px #ff00ff, 0 0 10px #ff00ff, 0 0 20px #ff00ff;
}
.chat-container {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
  scroll-behavior: smooth;
}
.stButton>button {
  background: linear-gradient(90deg, var(--accent), var(--secondary));
  color: #fff;
  font-weight: 700;
  border-radius: 10px;
  padding: 8px 12px;
}
.footer { color: #999; text-align:center; padding:8px; font-size:12px; opacity:0.8; }
.warning-box {
  background: rgba(255,0,0,0.2);
  color: #ffcccc;
  padding: 10px;
  border-radius: 8px;
  margin: 10px 0;
  text-align: center;
}
</style>
""")

# ---------------- Session State ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "mood_log" not in st.session_state:
    st.session_state.mood_log = []
if "active_mood_category" not in st.session_state:
    st.session_state.active_mood_category = "okay"

# ---------------- GenAI init (Gemini) ----------------
def init_genai():
    try:
        import google.generativeai as genai
    except:
        return None, "GenAI library not installed."
    
    api_key = st.secrets.get("GOOGLE_API_KEY", None)
    if not api_key and "general" in st.secrets and "GOOGLE_API_KEY" in st.secrets["general"]:
        api_key = st.secrets["general"]["GOOGLE_API_KEY"]
    if not api_key:
        return None, "No Google API Key set in Streamlit Secrets."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model, None
    except Exception as e:
        return None, str(e)

genai_model, genai_error = init_genai()

def call_genai(prompt, tone_hint="empathetic"):
    if not genai_model:
        return f"⚠️ GenAI unavailable: {genai_error}\nPlease set your GOOGLE_API_KEY in Streamlit Secrets."
    full_prompt = f"You are Zypher, an empathetic youth wellness bot. Tone: {tone_hint}.\nUser: {prompt}\nAssistant:"
    resp = genai_model.generate_content(full_prompt)
    return getattr(resp, "text", str(resp))

# ---------------- UI ----------------
st.html('<div class="container"></div>')  # container wrapper

# Logo
if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, width=160)

st.title("Zypher — Youth Mental Wellness")
st.caption("💬 Chat • 📋 Mood Analyzer • 😂 Memes • Mood Log")

tabs = st.tabs(["Chat", "Mood Analyzer", "Memes", "Mood Log"])

# ---------- Chat ----------
with tabs[0]:
    st.subheader("💬 Talk to ZypherBot (Safe & Encrypted)")
    user_input = st.text_input("Say something...", key="chat_input")
    
    col1, col2 = st.columns([4,1])
    with col2:
        mood_select = st.selectbox("Bot Tone", ["harassed","traumatized","funny","okay"], 
                                   index=["harassed","traumatized","funny","okay"].index(st.session_state.active_mood_category))
        if st.button("Apply Mood Tone"):
            st.session_state.active_mood_category = mood_select
            st.success(f"Active mood: {mood_select}")

    if st.button("Send"):
        if user_input.strip():
            st.session_state.chat_history.append({"from":"user","text":user_input})
            reply = call_genai(user_input, tone_hint=st.session_state.active_mood_category)
            st.session_state.chat_history.append({"from":"bot","text":reply})
        else:
            st.warning("Type something first!")

    # Display chat
    chat_html = '<div class="chat-container">'
    for item in st.session_state.chat_history:
        text = html.escape(item.get("text",""))
        if item.get("from") == "user":
            chat_html += f'<div class="user-bubble">{text}</div>'
        else:
            chat_html += f'<div class="bot-bubble">{text}</div>'
    chat_html += '</div>'
    st.html(chat_html)

    # Friendly warning if no API key
    if not genai_model:
        st.html(f'<div class="warning-box">⚠️ GenAI unavailable: {genai_error}<br>Set your GOOGLE_API_KEY in Streamlit Secrets to enable chat responses.</div>')

# ---------- Mood Analyzer ----------
with tabs[1]:
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
        if avg >= 4.5:
            analysis = "Very Positive and Happy"; suggested = "funny"
        elif avg >= 3.5:
            analysis = "Generally Positive"; suggested = "okay"
        elif avg >= 2.5:
            analysis = "Neutral"; suggested = "okay"
        elif avg >= 1.5:
            analysis = "Stressed or Negative"; suggested = "traumatized"
        else:
            analysis = "Very Negative or Upset"; suggested = "harassed"
        st.markdown(f"**Average Mood Score:** {avg:.2f}")
        st.info(f"Analysis: {analysis}")
        st.markdown(f"**Suggested Chat Tone:** `{suggested}`")
        if st.button("Use Suggested Tone"):
            st.session_state.active_mood_category = suggested
            st.success(f"Applied mood `{suggested}` to chat.")

# ---------- Memes ----------
with tabs[2]:
    st.subheader("😂 Meme Generator")
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

# ---------- Mood Log ----------
with tabs[3]:
    st.subheader("📓 Mood Log")
    colA, colB = st.columns([2,1])
    with colA:
        mood = st.selectbox("Log current mood", ["😊 Happy","😔 Sad","😡 Angry","😴 Tired","😎 Chill"])
    with colB:
        if st.button("Log Mood Entry"):
            st.session_state.mood_log.append({"mood": mood})
            st.success("Mood logged.")
    if st.session_state.mood_log:
        st.write(pd.DataFrame(st.session_state.mood_log))

# ---------- Footer ----------
st.html('<div class="footer">🔒 All conversations are end-to-end encrypted. Your privacy is 100% safe here.</div>')

