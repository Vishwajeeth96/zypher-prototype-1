# app.py — Zypher • Youth Mental Wellness
# Requirements: streamlit, pandas, requests, Pillow, google-generativeai
# Save logo (optional) at: assets/team_zypher_logo_transparent.png
# Run: pip install -r requirements.txt
# streamlit run app.py

import os
import random
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
st.markdown(
    """
    <style>
      :root {
        --bg1: #1e003f;  /* deep purple */
        --bg2: #2c0052;
        --accent: #8A2BE2; /* electric violet */
        --neon: #FF69B4; /* neon pink */
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
        box-shadow: 0 8px 30px rgba(0,0,0,0.7);
      }
      h1, h2, h3 { color: var(--accent); text-align:center; margin: 5px 0; }
      .user-bubble {
        background: linear-gradient(90deg, var(--neon), var(--accent));
        color: #1e003f;
        padding: 12px 16px;
        border-radius: 14px 14px 4px 14px;
        margin: 6px 0;
        max-width: 75%;
        float: right;
        clear: both;
        font-weight:600;
      }
      .bot-bubble {
        background: rgba(255,255,255,0.05);
        color: var(--muted);
        padding: 12px 16px;
        border-radius: 14px 14px 14px 4px;
        margin: 6px 0;
        max-width: 75%;
        float: left;
        clear: both;
      }
      .chat-container::after { content: ""; display: table; clear: both; }
      .stButton>button {
        background: linear-gradient(90deg, var(--accent), var(--neon));
        color: #fff;
        font-weight: 700;
        border-radius: 10px;
        padding: 8px 12px;
      }
      .footer { color: #dda0dd; text-align:center; padding:8px; font-size:12px; opacity:0.8; }
      .stFileUploader > div { background: rgba(255,255,255,0.01); border-radius:8px; padding:6px; }
      .tab-card { background: rgba(255,255,255,0.03); padding:15px; border-radius:12px; margin:10px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Session State ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "mood_log" not in st.session_state:
    st.session_state.mood_log = []
if "active_mood_category" not in st.session_state:
    st.session_state.active_mood_category = "okay"
if "use_ai" not in st.session_state:
    st.session_state.use_ai = True

# ---------------- GenAI init ----------------
def init_genai():
    try:
        import google.generativeai as genai
    except:
        return None, "genai-not-installed"

    api_key = st.secrets.get("GENAI_API_KEY", None)
    if not api_key:
        pasted = st.sidebar.text_input("Paste GenAI key (dev only)", type="password")
        if pasted:
            api_key = pasted
    if not api_key:
        return None, "no-api-key"

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model, None
    except Exception as e:
        return None, str(e)

genai_model, genai_error = init_genai()

def call_genai(prompt, tone_hint="empathetic"):
    if not genai_model:
        return f"⚠️ GenAI unavailable: {genai_error}"
    full_prompt = f"You are Zypher, an empathetic youth wellness bot. Tone: {tone_hint}.\nUser: {prompt}\nAssistant:"
    resp = genai_model.generate_content(full_prompt)
    return getattr(resp, "text", str(resp))

# ---------------- UI ----------------
st.markdown('<div class="container">', unsafe_allow_html=True)

# logo
if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, width=160)

st.title("Zypher — Youth Mental Wellness")
st.caption("💬 Chat • 📋 Mood Analyzer • 😂 Memes • Mood Log")

tabs = st.tabs(["Chat", "Mood Analyzer", "Memes", "Mood Log"])

# ---------- Chat ----------
with tabs[0]:
    st.subheader("💬 Talk to ZypherBot")
    col1, col2 = st.columns([4,1])
    with col1:
        user_input = st.text_input("Say something...", key="chat_input")
    with col2:
        mood_select = st.selectbox("Bot Tone", ["harassed","traumatized","funny","okay"], index=["harassed","traumatized","funny","okay"].index(st.session_state.active_mood_category))
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

    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for item in st.session_state.chat_history[::-1]:
        text = html.escape(item.get("text",""))
        if item.get("from") == "user":
            st.markdown(f"<div class='user-bubble'>{text}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-bubble'>{text}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

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



       
