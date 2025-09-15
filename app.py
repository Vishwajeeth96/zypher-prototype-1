# app.py — Zypher Youth Mental-Wellness Prototype
# Run: streamlit run app.py
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Zypher - Mental Wellness", page_icon="🌱", layout="centered")

# =========================
# CUSTOM BLUE GLASS THEME
# =========================
st.markdown(
    """
    <style>
        body {
            background: linear-gradient(135deg, #0f2027, #2c5364);
            color: white;
        }
        .main {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(12px);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0px 8px 30px rgba(0,0,0,0.35);
        }
        h1, h2, h3, h4 {
            color: #E0EFFF;
            text-align: center;
        }
        .stButton>button {
            background: linear-gradient(90deg, #1E90FF, #00BFFF);
            color: white;
            border-radius: 15px;
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            box-shadow: 0px 5px 15px rgba(0,0,0,0.2);
            transition: transform 0.2s;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #00BFFF, #1E90FF);
            transform: scale(1.05);
        }
        .stTextInput>div>div>input, .stSelectbox>div>div>select {
            background: rgba(255,255,255,0.15);
            color: white;
            border-radius: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# HUGGING FACE API
# =========================
HF_TOKEN = "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"  # YOUR TOKEN HERE
API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"

def query(payload):
    try:
        response = requests.post(API_URL, headers={"Authorization": f"Bearer {HF_TOKEN}"}, json=payload)
        data = response.json()
        return data[0].get('generated_text', "Sorry, I couldn't generate a response. 😔")
    except:
        return "Sorry, I couldn't generate a response. 😔"

# Meme API
MEME_API = "https://meme-api.com/gimme"

# =========================
# HEADER
# =========================
st.markdown(
    """
    <div style="padding: 20px;">
        <h1>🌱 Team Zypher</h1>
        <h2>Youth Mental Wellness Prototype</h2>
        <p style="font-size:18px;">💬 Chat • 😂 Memes • 📊 Mood Tracker</p>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# =========================
# CHATBOT
# =========================
st.markdown('<div class="main">', unsafe_allow_html=True)
st.subheader("💬 Talk to ZypherBot")
user_input = st.text_input("How are you feeling today? (Type your thoughts here...)")
if st.button("Send to Bot"):
    if user_input:
        reply = query({"inputs": user_input})
        st.success("🤖 ZypherBot: " + reply)
    else:
        st.warning("Please type something first!")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# =========================
# MEME GENERATOR
# =========================
st.markdown('<div class="main">', unsafe_allow_html=True)
st.subheader("😂 Need a laugh? Here's a meme!")
if st.button("Generate Meme"):
    try:
        meme = requests.get(MEME_API).json()
        st.image(meme["url"], caption=meme["title"])
    except:
        st.warning("Oops! Could not load a meme right now. 😅")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# =========================
# MOOD TRACKER
# =========================
st.markdown('<div class="main">', unsafe_allow_html=True)
st.subheader("📊 Track Your Mood")
if "mood_log" not in st.session_state:
    st.session_state["mood_log"] = []

mood = st.selectbox("How do you feel right now?", ["😊 Happy", "😔 Sad", "😡 Angry", "😴 Tired", "😎 Chill"])
if st.button("Log Mood"):
    st.session_state["mood_log"].append(mood)
    st.success(f"Mood '{mood}' logged!")

if st.session_state["mood_log"]:
    st.write("### 🌟 Mood History")
    df = pd.DataFrame(st.session_state["mood_log"], columns=["Mood"])
    st.dataframe(df)

    st.write("### 📊 Mood Chart")
    mood_counts = df["Mood"].value_counts()
    fig, ax = plt.subplots()
    mood_counts.plot(kind="bar", ax=ax, color="#1E90FF")
    ax.set_ylabel("Frequency")
    ax.set_xlabel("Mood")
    ax.set_title("Mood Tracker Chart")
    st.pyplot(fig)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# =========================
# FOOTER
# =========================
st.markdown(
    """
    <div style="text-align:center; padding: 20px; font-size:14px; color:#E0EFFF;">
        ✨ Built by <b>Team Zypher</b> | Youth Hackathon Prototype 2025 ✨
    </div>
    """,
    unsafe_allow_html=True
)
