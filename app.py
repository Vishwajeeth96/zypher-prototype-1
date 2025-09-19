# app.py — Zypher Youth Mental-Wellness Prototype with GenAI + Mood Tools
# Run locally:
#   pip install streamlit google-generativeai pillow pandas requests
# Then:
#   streamlit run app.py

import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import random
from io import BytesIO
from PIL import Image
import datetime

# ====== CONFIG ======
st.set_page_config(page_title="Zypher • Youth Mental Wellness", page_icon="🌱", layout="centered")

# 🔑 Your GenAI API Key (replace with your own)
genai.configure(api_key=AIzaSyCiKzF8VZhUMFMUqoppQAQWED4zcl_rAlc)
MODEL = genai.GenerativeModel("gemini-1.5-flash")

# ====== HELPERS ======
def get_ai_reply(prompt: str) -> str:
    """Get a reply from Google GenAI."""
    try:
        response = MODEL.generate_content(prompt)
        return response.text if response.text else "Hmm, I couldn’t generate a reply right now 🌱"
    except Exception as e:
        return f"⚠️ Error from GenAI: {str(e)}"

def get_meme():
    """Fetch a meme from meme-api."""
    try:
        meme = requests.get("https://meme-api.com/gimme", timeout=6).json()
        return meme.get("url"), meme.get("title")
    except:
        return None, None

# ====== SESSION ======
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "mood_log" not in st.session_state:
    st.session_state.mood_log = []

# ====== MAIN UI ======
st.title("🌱 Zypher — Youth Mental Wellness")
st.caption("Prototype • Powered by Google GenAI")

tabs = st.tabs(["💬 Chat", "🧠 Mood Analyzer", "😂 Memes", "📓 Mood Log", "⚙️ Settings"])

# -----------------
# TAB 1: Chat
# -----------------
with tabs[0]:
    st.subheader("Talk to ZypherBot")
    user_input = st.text_input("Type something...", key="chat_input")

    if st.button("Send", key="send_chat"):
        if not user_input.strip():
            st.warning("Type something first!")
        else:
            st.session_state.chat_history.append({"from": "user", "text": user_input})
            reply = get_ai_reply(user_input)
            st.session_state.chat_history.append({"from": "bot", "text": reply})

    # Show chat history
    for item in st.session_state.chat_history[::-1]:
        if item["from"] == "user":
            st.markdown(f"**You:** {item['text']}")
        else:
            st.markdown(f"**ZypherBot:** {item['text']}")

# -----------------
# TAB 2: Mood Analyzer
# -----------------
with tabs[1]:
    st.subheader("🧠 Mood Analyzer")
    q1 = st.radio("How are you feeling today?", ["Happy 😀", "Sad 😔", "Stressed 😣", "Angry 😡", "Lonely 😞"])
    q2 = st.slider("Energy Level", 0, 10, 5)
    q3 = st.slider("Mood Level", 0, 10, 5)

    if st.button("Analyze Mood", key="mood_button"):
        mood_summary = f"You feel {q1.lower()} with energy {q2}/10 and mood {q3}/10."
        st.success(mood_summary)
        st.session_state.mood_log.append(
            {"date": datetime.date.today().isoformat(), "mood": q1, "energy": q2, "level": q3}
        )

# -----------------
# TAB 3: Memes
# -----------------
with tabs[2]:
    st.subheader("😂 Random Meme Generator")
    if st.button("Generate Meme", key="meme_button"):
        url, title = get_meme()
        if url:
            resp = requests.get(url, timeout=8)
            img = Image.open(BytesIO(resp.content))
            st.image(img, caption=title)
        else:
            st.warning("Couldn’t fetch meme right now 😅")

# -----------------
# TAB 4: Mood Log
# -----------------
with tabs[3]:
    st.subheader("📓 Mood Log")
    if st.session_state.mood_log:
        df = pd.DataFrame(st.session_state.mood_log)
        st.table(df)
    else:
        st.info("No moods logged yet.")

# -----------------
# TAB 5: Settings
# -----------------
with tabs[4]:
    st.subheader("⚙️ Settings")
    st.markdown("Upload canned responses (optional, CSV with `user_phrase, bot_reply, category`).")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.dataframe(df.head())
        st.success("Responses uploaded successfully ✅")



