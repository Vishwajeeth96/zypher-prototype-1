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

# Custom CSS (Blue + Transparent Theme)
st.markdown(
    """
    <style>
        body {
            background: linear-gradient(135deg, #1e3c72, #2a5298); 
            color: white;
        }
        .main {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
        }
        h1, h2, h3, h4 {
            color: #E0EFFF;
            text-align: center;
        }
        .stButton>button {
            background: linear-gradient(90deg, #1E90FF, #00BFFF);
            color: white;
            border-radius: 12px;
            padding: 8px 16px;
            font-size: 16px;
            border: none;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #00BFFF, #1E90FF);
            transform: scale(1.03);
        }
        .stTextInput>div>div>input, .stSelectbox>div>div>select {
            background: rgba(255,255,255,0.15);
            color: white;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Hugging Face API (Chatbot)
HF_TOKEN = "your_hf_token_here"  # replace with your Hugging Face token
API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# Meme API
MEME_API = "https://meme-api.com/gimme"

# =========================
# APP HEADER
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
# FEATURE 1: Chatbot
# =========================
st.subheader("💬 Talk to ZypherBot")

user_input = st.text_input("How are you feeling today? (Type your thoughts here...)")

if st.button("Send to Bot"):
    if user_input:
        output = query({"inputs": user_input})
        st.success("🤖 ZypherBot: " + output[0]['generated_text'])
    else:
        st.warning("Please type something first!")

st.markdown("---")

# =========================
# FEATURE 2: Meme Generator
# =========================
st.subheader("😂 Need a laugh? Here's a meme!")

if st.button("Generate Meme"):
    meme = requests.get(MEME_API).json()
    st.image(meme["url"], caption=meme["title"])

st.markdown("---")

# =========================
# FEATURE 3: Mood Tracker
# =========================
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

    # Mood frequency chart
    st.write("### 📊 Mood Chart")
    mood_counts = df["Mood"].value_counts()
    fig, ax = plt.subplots()
    mood_counts.plot(kind="bar", ax=ax)
    ax.set_ylabel("Frequency")
    ax.set_xlabel("Mood")
    ax.set_title("Mood Tracker Chart")
    st.pyplot(fig)

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
