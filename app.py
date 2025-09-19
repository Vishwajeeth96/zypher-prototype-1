# app.py — Zypher • Youth Mental Wellness (Animated UI + Meme + Mood Log)
# Requirements: streamlit, requests, Pillow, google-generativeai

import os
import random
from io import BytesIO

import streamlit as st
from PIL import Image
import requests

# ---------------- Page config ----------------
st.set_page_config(
    page_title="Zypher • Youth Mental Wellness",
    page_icon="💬",
    layout="centered"
)

# ---------------- Theme / CSS ----------------
st.markdown("""
<style>
body {
    background: linear-gradient(160deg,#0b0c2a,#1a1a3d);
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
}
h1,h2,h3 { color: #a29bfe; text-align:center; margin:5px 0; }

/* Chat bubbles */
.user-bubble {
    background: linear-gradient(90deg,#ff9ff3,#f368e0);
    color: #fff;
    padding:12px;
    border-radius:20px 20px 4px 20px;
    margin:6px 0;
    max-width:75%;
    float:right;
    clear:both;
    animation: slideRight 0.5s ease-out;
    transition: transform 0.2s;
}
.user-bubble:hover { transform: scale(1.03); }

.bot-bubble {
    background: linear-gradient(90deg,#48dbfb,#1dd1a1);
    color:#fff;
    padding:12px;
    border-radius:20px 20px 20px 4px;
    margin:6px 0;
    max-width:75%;
    float:left;
    clear:both;
    animation: slideLeft 0.5s ease-out;
    box-shadow: 0 0 8px rgba(72,219,251,0.6);
}

/* Animations */
@keyframes slideRight {
    0% { opacity:0; transform: translateX(50px);}
    100% { opacity:1; transform: translateX(0);}
}
@keyframes slideLeft {
    0% { opacity:0; transform: translateX(-50px);}
    100% { opacity:1; transform: translateX(0);}
}

.chat-container::after { content:""; display:table; clear:both; }

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg,#a29bfe,#00d2d3);
    color: #00110a;
    font-weight:600;
    border-radius:12px;
    padding:8px 12px;
    transition: transform 0.2s;
}
.stButton>button:hover { transform: scale(1.05); }

/* Tabs */
.stTabs [role="tablist"] button { color:#e0e0e0; }

/* Glassmorphic container for main content */
.main-container {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(10px);
    border-radius:16px;
    padding:16px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.6);
    margin-bottom:20px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Session state ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "mood_log" not in st.session_state:
    st.session_state.mood_log = []
if "active_mood_category" not in st.session_state:
    st.session_state.active_mood_category = "okay"

# ---------------- GenAI init ----------------
try:
    import google.generativeai as genai
    genai.configure(api_key=st.secrets["GENAI_API_KEY"])
    genai_model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    genai_model = None
    st.warning("⚠️ GenAI not configured: " + str(e))

def call_genai(prompt, tone="empathetic"):
    if genai_model is None:
        return "⚠️ GenAI not available."
    full_prompt = f"You are Zypher, an empathetic youth mental wellness assistant. Tone: {tone}.\nUser: {prompt}\nAssistant:"
    resp = genai_model.generate_content(full_prompt)
    return resp.text.strip() if resp else "⚠️ No response generated."

# ---------------- Meme generator ----------------
MEME_API = "https://meme-api.com/gimme"
def get_meme_image():
    try:
        r = requests.get(MEME_API, timeout=6).json()
        url = r.get("url")
        title = r.get("title")
        return url, title
    except:
        return None, None

# ---------------- Main UI ----------------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.title("Zypher — Youth Mental Wellness")
st.caption("Chat • Meme Generator • Mood Log — Prototype")
tabs = st.tabs(["Chat", "Memes", "Mood Log"])

# ---------- Chat ----------
with tabs[0]:
    st.subheader("💬 Talk to ZypherBot")
    user_input = st.text_input("Say something...", key="chat_input")
    mood_select = st.selectbox("Bot Tone", ["harassed","notwilling","traumatized","funny","okay"], index=["harassed","notwilling","traumatized","funny","okay"].index(st.session_state.active_mood_category))
    if st.button("Apply Mood"):
        st.session_state.active_mood_category = mood_select
        st.success(f"Active mood: {mood_select}")

    if st.button("Send"):
        if user_input.strip():
            st.session_state.chat_history.append({"from":"user","text":user_input})
            reply = call_genai(user_input, tone=st.session_state.active_mood_category)
            st.session_state.chat_history.append({"from":"bot","text":reply})
        else:
            st.warning("Type something first!")

    st.markdown("**Conversation**")
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for item in st.session_state.chat_history[::-1]:
        text = item.get("text","")
        if item.get("from")=="user":
            st.markdown(f'<div class="user-bubble">{text}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-bubble">{text}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Memes ----------
with tabs[1]:
    st.subheader("😂 Meme Generator")
    if st.button("Generate Meme"):
        url, title = get_meme_image()
        if url:
            try:
                resp = requests.get(url, timeout=8)
                img = Image.open(BytesIO(resp.content))
                st.image(img, caption=title)
            except:
                st.warning("Failed to load meme image.")
        else:
            st.warning("Could not fetch meme right now.")

# ---------- Mood Log ----------
with tabs[2]:
    st.subheader("📓 Mood Log")
    mood = st.selectbox("Log current mood", ["😊 Happy","😔 Sad","😡 Angry","😴 Tired","😎 Chill"])
    if st.button("Log Mood"):
        st.session_state.mood_log.append({"mood": mood})
        st.success("Mood logged.")
    if st.session_state.mood_log:
        st.write(st.session_state.mood_log)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#7fffd4; font-size:12px; opacity:0.9;'>✨ Built by Team Zypher — Hackathon Prototype</div>", unsafe_allow_html=True)

       
