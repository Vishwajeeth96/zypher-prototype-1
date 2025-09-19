import streamlit as st
import google.generativeai as genai
import random

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Zypher AI Bot",
    page_icon="🤖",
    layout="wide",
)

# ---------- CUSTOM STYLING ----------
st.markdown("""
<style>
    body {
        background-color: #0d0d0d;
        color: #00ff88;
    }
    .main {
        background-color: #0d0d0d;
        color: #00ff88;
    }
    .stButton button {
        background-color: #00ff88;
        color: black;
        border-radius: 10px;
        font-weight: bold;
    }
    .user-bubble {
        background: #1a1a1a;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        color: #00ff88;
    }
    .bot-bubble {
        background: #003300;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        color: #00ff88;
    }
</style>
""", unsafe_allow_html=True)

# ---------- LOAD API KEY ----------
api_key = st.secrets.get("GOOGLE_API_KEY", None)

if not api_key:
    st.error("⚠️ No API key found. Please add it in Streamlit Secrets as GOOGLE_API_KEY.")
else:
    genai.configure(api_key=api_key)

# ---------- SIDEBAR ----------

st.sidebar.title("⚡ Zypher Control Panel")
st.sidebar.markdown("Black & Green Theme Active ✅")

# ---------- SESSION STATE ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- CHAT UI ----------
st.title("🤖 ZypherBot")
st.markdown("Your AI teammate, always ready.")

user_input = st.text_input("💬 Ask Zypher something...")

if st.button("Send") and user_input:
    st.session_state.chat_history.append({"from": "user", "text": user_input})
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(user_input)
        bot_reply = response.text if response else "⚠️ No reply generated."
    except Exception as e:
        bot_reply = f"⚠️ Error: {e}"

    st.session_state.chat_history.append({"from": "bot", "text": bot_reply})

# ---------- DISPLAY CHAT ----------
for msg in st.session_state.chat_history:
    if msg["from"] == "user":
        st.markdown(f"<div class='user-bubble'>👤 You: {msg['text']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'>🤖 ZypherBot: {msg['text']}</div>", unsafe_allow_html=True)

# ---------- MEME GENERATOR ----------
st.subheader("🎭 Meme Generator")
meme_prompts = [
    "When you debug for 5 hours and realize it's a missing semicolon.",
    "POV: The code worked on your machine but not in production.",
    "When AI writes better code than your team lead 😂",
    "Trying to explain recursion like...",
    "Deploy on Friday evening, what could go wrong?"
]

if st.button("Generate Meme"):
    prompt = random.choice(meme_prompts)
    st.success(f"💡 Meme Idea: {prompt}")
    try:
        meme_model = genai.GenerativeModel("gemini-1.5-flash")
        meme_response = meme_model.generate_content(prompt)
        st.write(meme_response.text if meme_response else "⚠️ Meme failed to generate.")
    except:
        st.error("⚠️ Meme generator failed. Check your API key.")

