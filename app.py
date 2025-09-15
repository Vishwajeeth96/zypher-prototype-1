# app.py — Zypher Youth Mental-Wellness Prototype
# Run: streamlit run app.py
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import random

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Zypher - Mental Wellness", page_icon="🌱", layout="centered")

# =========================
# BLUE GLASSMORPHIC THEME
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
            margin-bottom: 20px;
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
# PREDEFINED RESPONSES (100+)
# =========================
predefined_replies = {
    # Moods
    "happy": ["That's great! Keep smiling 😄", "Yay! Stay happy 🌟", "Awesome! Happiness looks good on you 😃"],
    "sad": ["I’m sorry you’re feeling sad. Take a deep breath 🌱", "It’s okay to feel down sometimes 💙", "Hugs! Things will get better 🤗"],
    "stressed": ["Try to relax and take a short break 🧘‍♂️", "Stress is temporary. You got this 💪", "Breathe in… breathe out… 🌿"],
    "anxious": ["It’s okay to feel anxious. You’re not alone 💙", "Focus on the present moment 🌸", "Anxiety comes and goes, stay calm 🧘‍♀️"],
    "tired": ["Make sure to rest and recharge 😴", "Even superheroes need sleep 🛌", "Take a short nap, your mind will thank you 🌙"],
    "bored": ["Try learning something new today 📚", "Maybe a fun meme can cheer you up 😂", "Go for a short walk and refresh! 🌳"],

    # School/College
    "exam": ["Focus on one topic at a time 📝", "Don't forget to take short breaks!", "Believe in your preparation 💪"],
    "study": ["Set small goals and reward yourself 🎯", "Consistency beats cramming 🌟", "Remember to sleep well too 💤"],
    "homework": ["Break tasks into smaller chunks 📝", "Stay organized, it makes things easier ✨", "Ask friends if you’re stuck 🤝"],

    # Friendship
    "friend": ["Talk to your friend honestly 💬", "Friendship needs understanding ❤️", "A small gesture can fix a lot 🌸"],
    "lonely": ["You are never truly alone 🌱", "Reach out to someone you trust 🤗", "Try journaling your thoughts ✍️"],

    # Self-esteem / motivation
    "confidence": ["Believe in yourself! 💪", "You are capable of amazing things 🌟", "Small steps every day build confidence 🚀"],
    "motivation": ["Set clear goals and start small 🏁", "Remember why you began 💡", "Every effort counts, keep going 🔥"],

    # Sleep/Health
    "sleep": ["Try to maintain a sleep schedule 💤", "Avoid screens 30 mins before bed 🌙", "Relaxation techniques help 🧘‍♀️"],
    "eat": ["Eat healthy and stay hydrated 🥗💧", "Balance is key for energy ⚡", "Don’t skip meals, fuel your mind! 🍎"],

    # Relaxation / coping
    "relax": ["Listen to your favorite music 🎶", "Try a short meditation session 🧘‍♂️", "Go outside and take deep breaths 🌿"],
    "angry": ["Count to ten and breathe 🔥", "Take a short walk to calm down 🌳", "Write down what’s bothering you ✍️"],

    # Default / fallback
    "default": ["I hear you! Keep talking to me 💬", "Thank you for sharing 🌱", "I’m here to listen 🧡"]
}

# Expand keywords for 100+ entries
keywords_list = [
    "happy","sad","stressed","anxious","tired","bored",
    "exam","study","homework","friend","lonely",
    "confidence","motivation","sleep","eat","relax","angry"
]

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
# CHATBOT (PROTOTYPE)
# =========================
st.markdown('<div class="main">', unsafe_allow_html=True)
st.subheader("💬 Talk to ZypherBot (Prototype)")
user_input = st.text_input("How are you feeling today? (Type your thoughts here...)")

if st.button("Send to Bot"):
    if user_input:
        user_lower = user_input.lower()
        reply_found = False
        for key in keywords_list:
            if key in user_lower:
                reply = random.choice(predefined_replies[key])
                reply_found = True
                break
        if not reply_found:
            reply = random.choice(predefined_replies["default"])
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

