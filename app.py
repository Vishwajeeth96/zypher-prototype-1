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
st.markdown(
    """
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

# ---------------- GenAI init ----------------
def init_genai():
    try:
        import google.generativeai as genai
    except:
        return None, "GenAI library not installed."

    # Try top-level secret first
    api_key = st.secrets.get("GOOGLE_API_KEY", None)

    # Fallback to [general] section
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
st.markdown('<div class="container">', unsafe_allow_html=True)

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
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for item in st.session_state.chat_history:  # newest at bottom
        text = html.escape(item.get("text",""))
        if item.get("from") == "user":
            st.markdown(f"<div class='user-bubble'>{text}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-bubble'>{text}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Auto-scroll to bottom
    st.markdown(
        """
        <script>
        const chat = window.parent.document.querySelector('.chat-container');
        if(chat){chat.scrollTop = chat.scrollHeight;}
        </script>
        """,
        unsafe_allow_html=True
    )

    # Friendly warning if no API key
    if not genai_model:
        st.markdown

