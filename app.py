# app.py — Zypher • Youth Mental Wellness (Fixed & Ready for Free Gemini API)
# Requirements: streamlit, pandas, requests, Pillow, google-generativeai
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
st.markdown("""
<style>
:root {
  --bg1: #000000;
  --bg2: #001a00;
  --neon: #00FF7F;
  --accent: #00C98A;
  --muted: #bfbfbf;
}
body {
  background: linear-gradient(180deg, var(--bg1), var(--bg2));
  color: var(--muted);
}
.container {
  background: rgba(255,255,255,0.02);
  padding: 18px;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.6);
}
h1, h2 { color: var(--neon); text-align:center; margin: 2px 0; }
.user-bubble {
  background: linear-gradient(90deg, rgba(0,255,127,1), rgba(0,201,138,1));
  color: #00110a;
  padding: 10px 14px;
  border-radius: 14px 14px 4px 14px;
  margin: 6px 0;
  max-width: 78%;
  float: right;
  clear: both;
  font-weight:600;
}
.bot-bubble {
  background: rgba(255,255,255,0.03);
  color: var(--muted);
  padding: 10px 14px;
  border-radius: 14px 14px 14px 4px;
  margin: 6px 0;
  max-width: 78%;
  float: left;
  clear: both;
}
.chat-container::after { content: ""; display: table; clear: both; }
.stButton>button {
  background: linear-gradient(90deg, var(--neon), var(--accent));
  color: #00110a;
  font-weight: 700;
  border-radius: 10px;
  padding: 8px 12px;
}
.footer { color: #7fffd4; text-align:center; padding:8px; font-size:12px; opacity:0.9; }
.small-muted { color: #9dbda3; font-size:13px; }
.stFileUploader > div { background: rgba(255,255,255,0.01); border-radius:8px; padding:6px; }
</style>
""", unsafe_allow_html=True)

# ---------------- Defaults ----------------
PREDEFINED_REPLIES = {
    "happy": ["That's great! Keep smiling 😄", "Yay! Stay happy 🌟"],
    "sad": ["I’m sorry you're feeling sad. Take a deep breath 🌱", "It's okay to feel down sometimes 💙"],
    "stressed": ["Try a short breathing break 🧘", "You've made it this far — be kind to yourself 💪"],
    "default": ["I hear you. Keep sharing if you want 💬", "I’m here to listen 🌱"]
}

MOOD_DICT = {
    "harassed": {"i feel disgusting": "You’re not disgusting. The shame belongs to the person who hurt you, not you."},
    "okay": {"i feel fine": "Fine is enough. No need to force amazing every day."}
}

MEME_API = "https://meme-api.com/gimme"

# ---------------- Session State ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "canned_df" not in st.session_state:
    st.session_state.canned_df = None
if "active_mood_category" not in st.session_state:
    st.session_state.active_mood_category = "okay"
if "mood_log" not in st.session_state:
    st.session_state.mood_log = []

# ---------------- Helpers ----------------
def load_canned_from_file(uploaded_file):
    try:
        if uploaded_file is None: return None
        name = uploaded_file.name.lower()
        if name.endswith(".csv"): df = pd.read_csv(uploaded_file)
        elif name.endswith(".json"): df = pd.read_json(uploaded_file)
        else: st.error("Upload a .csv or .json"); return None
        if "user_phrase" in df.columns and "bot_reply" in df.columns:
            df["user_phrase_norm"] = df["user_phrase"].astype(str).str.lower()
            return df
        else:
            st.error("File must contain columns: user_phrase, bot_reply")
            return None
    except Exception as e:
        st.error("Failed to load canned responses: " + str(e))
        return None

def find_canned_reply(user_text):
    df = st.session_state.canned_df
    if df is None: return None
    txt = user_text.strip().lower()
    exact = df[df["user_phrase_norm"] == txt]
    if not exact.empty: return exact.iloc[0]["bot_reply"]
    for idx, phrase in enumerate(df["user_phrase_norm"].tolist()):
        if phrase in txt or txt in phrase:
            return df.iloc[idx]["bot_reply"]
    return None

def baseline_keyword_reply(user_text):
    t = user_text.lower()
    for key, replies in PREDEFINED_REPLIES.items():
        if key in t: return random.choice(replies)
    return random.choice(PREDEFINED_REPLIES["default"])

def get_meme_image():
    try:
        r = requests.get(MEME_API, timeout=6).json()
        return r.get("url"), r.get("title")
    except Exception:
        return None, None

# ---------------- GenAI ----------------
def init_genai():
    try:
        import google.generativeai as genai
    except:
        return None, "genai-not-installed"
    api_key = st.secrets.get("GENAI_API_KEY") or os.getenv("GENAI_API_KEY") or ""
    if not api_key:
        api_key = st.sidebar.text_input("Paste GenAI key (dev only)", type="password")
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
    if genai_model is None: return f"⚠️ GenAI unavailable: {genai_error}"
    full_prompt = f"You are Zypher, an empathetic youth mental wellness assistant. Tone: {tone_hint}.\nUser: {prompt}\nAssistant:"
    resp = genai_model.generate_content(full_prompt)
    try: return resp.text.strip()
    except: return str(resp)

def get_reply(user_text):
    canned = find_canned_reply(user_text)
    if canned: return canned
    mood_reply = None
    dict_for_mood = MOOD_DICT.get(st.session_state.active_mood_category, {})
    txt = user_text.strip().lower()
    for phrase, response in dict_for_mood.items():
        if phrase == txt or phrase in txt or txt in phrase:
            mood_reply = response
            break
    if mood_reply: return mood_reply
    if st.session_state.get("use_ai", True):
        try:
            tone = st.session_state.active_mood_category
            ai_resp = call_genai(user_text, tone_hint=tone)
            if ai_resp: return ai_resp
        except: pass
    return baseline_keyword_reply(user_text)

# ---------------- Sidebar ----------------
with st.sidebar:
    st.title("👋 Zypher Setup")
    st.checkbox("Use GenAI (Gemini)", value=True, key="use_ai")
    st.markdown("---")
    st.markdown("**Upload canned responses (optional)**")
    uploaded = st.file_uploader("CSV/JSON Q→A", type=["csv", "json"])
    if uploaded:
        df = load_canned_from_file(uploaded)
        if df is not None:
            st.session_state.canned_df = df
            st.success(f"Loaded {len(df)} canned pairs.")

# ---------------- Main ----------------
st.markdown('<div class="container">', unsafe_allow_html=True)
if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=180)
st.title("Zypher — Youth Mental Wellness")
st.caption("Chat • Mood Analyzer • Memes — Prototype")

tabs = st.tabs(["Chat", "Mood Analyzer", "Memes", "Mood Log"])

# Chat
with tabs[0]:
    st.subheader("💬 Talk to ZypherBot")
    col1, col2 = st.columns([4,1])
    with col1: user_input = st.text_input("Say something...", key="chat_input")
    with col2:
        mood_select = st.selectbox("Bot tone", ["harassed","notwilling","traumatized","funny","okay"], index=["harassed","notwilling","traumatized","funny","okay"].index(st.session_state.active_mood_category))
        if st.button("Apply mood"): st.session_state.active_mood_category = mood_select

    if st.button("Send"):
        if user_input.strip()!="":
            st.session_state.chat_history.append({"from":"user","text":user_input})
            reply = get_reply(user_input)
            st.session_state.chat_history.append({"from":"bot","text":reply})
        else: st.warning("Type something first!")

    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for item in st.session_state.chat_history[::-1]:
        text = item.get("text","")
        if item.get("from") == "user":
            st.markdown(f"<div class='user-bubble'>{html.escape(text)}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-bubble'>ZypherBot: {html.escape(text)}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Mood Analyzer
with tabs[1]:
    st.subheader("📋 Mood Analyzer")
    questions = [
        {"q":"How have you been feeling generally today?","opts":["Very good","Good","Neutral","Bad","Very bad"]},
        {"q":"How motivated do you feel right now?","opts":["Very motivated","Somewhat motivated","Neutral","Little motivated","Not motivated at all"]},
        {"q":"How well did you sleep last night?","opts":["Very well","Well","Average","Poorly","Very poorly"]},
        {"q":"How would you rate your stress level currently?","opts":["Very low","Low","Moderate","High","Very high"]},
        {"q":"How connected have you felt with others recently?","opts":["Very connected","Somewhat connected","Neutral","Somewhat disconnected","Very disconnected"]}
    ]
    with st.form("mood_form"):
        answers=[]
        for i,qq in enumerate(questions):
            answers.append(st.radio(qq["q"], qq["opts"], index=2, key=f"q{i}"))
        submit = st.form_submit_button("Analyze Mood")
    if submit:
        score_map = {"Very good":5,"Good":4,"Neutral":3,"Average":3,"Bad":2,"Very bad":1,
                     "Very motivated":5,"Somewhat motivated":4,"Little motivated":2,"Not motivated at all":1,
                     "Very well":5,"Well":4,"Poorly":2,"Very poorly":1,
                     "Very low":5,"Low":4,"Moderate":3,"High":2,"Very high":1,
                     "Very connected":5,"Somewhat connected":4,"Somewhat disconnected":2,"Very disconnected":1}
        total = sum(score_map.get(a,3) for a in answers)
        avg = total / len(questions)
        if avg >= 4.5: analysis, suggested = "Very Positive and Happy","funny"
        elif avg >= 3.5: analysis, suggested = "Generally Positive","okay"
        elif avg >= 2.5: analysis, suggested = "Neutral","okay"
        elif avg >= 1.5: analysis, suggested = "Stressed or Negative","traumatized"
        else: analysis, suggested = "Very Negative or Upset","harassed"
        st.markdown(f"**Average mood score:** {avg:.2f}")
       
