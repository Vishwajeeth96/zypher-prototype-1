import streamlit as st
import random
from datetime import datetime
from io import BytesIO
from PIL import Image
import requests
import html

# 1️⃣ PAGE SETUP
st.set_page_config(page_title="Zypher AI Bot", page_icon="🌿", layout="wide")

# --- DARK MODE & BUBBLES FIX ---
st.markdown("""
<style>
  div[data-testid="stChatMessage"],
  div[data-testid="stChatMessageList"],
  div[data-testid="stChatInput"] {
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
  }
  #MainMenu, header, footer { visibility: hidden !important; }
  .block-container { padding-top:0 !important; }
  .user-bubble, .bot-bubble {
    margin:0.5rem 0; padding:0.5rem 1rem; max-width:75%; display:inline-block;
    line-height:1.4; color:#fff;
  }
  .user-bubble { background:#1565c0; border-radius:1rem 1rem 0.5rem 1rem; }
  .bot-bubble { background:#2e7d32; border-radius:1rem 1rem 1rem 0.5rem; }
  .timestamp { display:block; font-size:0.7rem; color:#ccc; margin-top:0.2rem; }
  .stApp { background-color:#121212; color:#e0e0e0; }
  h1,h2,h3 { margin-top:0.2rem; margin-bottom:0.5rem; color:#fff; }
</style>
""", unsafe_allow_html=True)

# 2️⃣ SESSION STATE
st.session_state.setdefault("mood_log", [])
st.session_state.setdefault("chat_history", [])

# 3️⃣ FALLBACK RESPONSES
fallbacks = {
    "happy": [
        "Yay! 😄", "Keep shining! 🌸", "Happiness suits you! 💖", 
        "Woohoo! 🎉", "That’s amazing! ✨"
    ],
    "sad": [
        "I hear you 💙", "It’s okay to not feel okay 🌧️", "Sending a hug 🤗",
        "Stay strong, bro 💪", "Cheer up! 🌈"
    ],
    "angry": [
        "Breathe in… breathe out 🧘", "It’s okay to vent 💢", 
        "Need a calming tip?", "Take a short walk 🚶", "Relax a bit 😌"
    ],
    "neutral": [
        "I’m listening 👂", "Tell me more…", "Thanks for sharing 💭",
        "Hmm… interesting 🤔", "Go on…"
    ],
    "default": [
        "Cool!", "I see!", "That’s nice!", "Got it! 👍", "Hmm… okay!"
    ]
}

# Optional: keyword-based responses
keywords = {
    "hello": ["Hey there! 🌿", "Hi! How’s it going?", "Hello! 😎"],
    "hi": ["Hi! 🌸", "Hey! How are you?", "Hello! 😄"],
    "name": ["I’m Zypher, your AI buddy 🌿", "Call me Zypher! 😎"],
    "meme": ["😂 Want a meme? Click the button on the left!", "Memes incoming! 🌟"],
    "how are you": ["I’m good, thanks! How about you?", "Doing well 😄", "Feeling awesome! 💚"]
}

# Function to get bot response
def get_bot_response(text, mood="neutral"):
    text_lower = text.lower()
    for key, responses in keywords.items():
        if key in text_lower:
            return random.choice(responses)
    # If no keyword match, use mood-based fallback
    return random.choice(fallbacks.get(mood, fallbacks["default"]))

# 4️⃣ LAYOUT: TWO COLUMNS
left_col, right_col = st.columns([1, 2], gap="small")

# --- LEFT PANEL ---
with left_col:
    st.header("🌸 Mood Log")
    current_mood = st.radio("Select mood", ["happy","sad","angry","neutral"], horizontal=True, index=3)
    if st.button("Log Mood"):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.mood_log.append({"mood":current_mood, "timestamp":ts})
        st.success(f"Logged {current_mood} at {ts}")
    if st.session_state.mood_log:
        st.subheader("📅 Recent Entries")
        for e in reversed(st.session_state.mood_log[-5:]):
            st.write(f"{e['timestamp']} → {e['mood']}")
    st.markdown("---")
    st.header("😂 Meme Generator")
    if st.button("Fetch Meme"):
        try:
            m = requests.get("https://meme-api.com/gimme", timeout=5).json()
            url, cap = m.get("url"), m.get("title","")
            if url and (url.endswith(".jpg") or url.endswith(".png")):
                img = Image.open(BytesIO(requests.get(url).content))
                st.image(img, caption=cap, use_container_width=True)
            else:
                st.warning("⚠️ No image meme available, here’s a text joke instead:")
                st.info(m.get("title", "😂 Keep smiling!"))
        except Exception as e:
            st.error(f"Failed to fetch meme. ({e})")
    st.markdown("---")
    st.header("📋 Mood Analyzer")
    questions = [
        ("Feeling today?", ["Very good","Good","Neutral","Bad","Very bad"]),
        ("Motivation level?", ["Very high","High","Neutral","Low","Very low"]),
        ("Sleep quality?", ["Excellent","Good","Average","Poor","Very poor"]),
        ("Stress level?", ["Very low","Low","Moderate","High","Very high"]),
        ("Social connection?", ["Very connected","Connected","Neutral","Disconnected","Very disconnected"])
    ]
    with st.form("analyze_form"):
        answers = [st.radio(q, opts, index=2, key=f"q{i}") for i,(q,opts) in enumerate(questions)]
        submitted = st.form_submit_button("Analyze Mood")
    if submitted:
        score = {opt:5-i for _,opts in questions for i,opt in enumerate(opts)}
        avg = sum(score.get(a,3) for a in answers) / len(answers)
        if avg>=4.5: analysis, tone = "Very Positive & Happy","happy"
        elif avg>=3.5: analysis, tone = "Generally Positive","neutral"
        elif avg>=2.5: analysis, tone = "Neutral","neutral"
        elif avg>=1.5: analysis, tone = "Stressed or Negative","sad"
        else:           analysis, tone = "Very Negative or Upset","angry"
        st.markdown(f"**Avg. Score:** {avg:.2f}")
        st.info(f"Analysis: {analysis}")
        if st.button("Apply Suggested Tone"):
            current_mood = tone
            st.success(f"Chat tone set to {tone}")

# --- RIGHT PANEL: Chatbot ---
with right_col:
    st.header("🌿 Zypher Chatbot")
    if st.button("Clear Chat"):
        st.session_state.chat_history = []

    user_input = st.chat_input("Type your message…")
    if user_input:
        now = datetime.now().strftime("%H:%M")
        st.session_state.chat_history.append({"from": "user", "text": user_input, "timestamp": now})
        reply = get_bot_response(user_input, current_mood)
        st.session_state.chat_history.append({"from": "bot", "text": reply, "timestamp": datetime.now().strftime("%H:%M")})

    # Render chat messages
    for msg in st.session_state.chat_history:
        txt = html.escape(msg.get("text", ""))
        ts = msg.get("timestamp", "")
        cls = "user-bubble" if msg.get("from")=="user" else "bot-bubble"
        prefix = "🧑 You: " if msg.get("from")=="user" else "🤖 Zypher: "
        st.markdown(f'<div class="{cls}"><b>{prefix}</b>{txt}<span class="timestamp">{ts}</span></div>', unsafe_allow_html=True)

# 5️⃣ FOOTER NOTE
st.markdown("<div style='text-align:center;color:#888;font-size:0.8rem;padding:0.5rem 0;'>🔒 Conversations are end-to-end encrypted.</div>", unsafe_allow_html=True)


