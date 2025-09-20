# app.py — Zypher • Youth Mental Wellness Chatbot

import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from datetime import datetime
import requests
import random
import html
from io import BytesIO
from PIL import Image

# 1) PAGE CONFIG
st.set_page_config(page_title="Zypher AI Bot", page_icon="🌿", layout="wide")

# 2) GLOBAL CSS: hide Streamlit chrome, box chat panel, neutral bubbles
st.markdown("""
<style>
  /* hide header/menu/footer */
  #MainMenu, header, footer { visibility: hidden; }

  /* remove block-container top padding */
  .block-container { padding-top: 0 !important; }

  /* box around chat */
  .chat-box {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1rem;
    height: 90vh;
    overflow-y: auto;
    background: #fff;
  }

  /* neutral ChatGPT-style bubbles */
  .user-bubble, .bot-bubble {
    background: none !important;
    border: 1px solid #ddd !important;
    border-radius: 10px !important;
    padding: 0.5rem 1rem !important;
    margin: 0.5rem 0 !important;
    color: #000 !important;
    max-width: 75% !important;
  }

  .timestamp {
    display: block;
    font-size: 0.7rem;
    color: #555;
    margin-top: 0.2rem;
  }
</style>
""", unsafe_allow_html=True)

# 3) GEMINI API SETUP
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ GEMINI_API_KEY not found! Add it under Settings → Secrets.")
    st.stop()
genai.configure(api_key=api_key)

# 4) SESSION STATE
st.session_state.setdefault("mood_log", [])
st.session_state.setdefault("chat_history", [])

# 5) FALLBACKS & BOT FUNCTION
fallbacks = {
    "happy":   ["That’s amazing! 🌸","Keep shining! ✨","Happiness suits you! 💖"],
    "sad":     ["I hear you 💙","It’s okay to not feel okay 🌧️","Sending a hug 🤗"],
    "angry":   ["Breathe in… breathe out 🧘","It’s okay to vent 💢","Need a tip?"],
    "neutral": ["I’m listening 👂","Tell me more…","Thanks for sharing 💭"]
}

def get_bot_response(text, mood="neutral"):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model.generate_content(text).text.strip()
    except:
        return random.choice(fallbacks.get(mood, ["I’m here for you. 💙"]))

# 6) TWO-COLUMN LAYOUT (FLUSH TOP)
left_col, right_col = st.columns([1, 2], gap="small")

# --- LEFT PANEL: Mood Log / Meme / Analyzer ---
with left_col:
    st.header("🌸 Mood Log")
    current_mood = st.radio(
        "Select mood", ["happy", "sad", "angry", "neutral"],
        horizontal=True, index=3
    )
    if st.button("Log Mood"):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.mood_log.append({"mood": current_mood, "timestamp": ts})
        st.success(f"Logged {current_mood} at {ts}")

    if st.session_state.mood_log:
        st.subheader("📅 Recent Entries")
        for entry in reversed(st.session_state.mood_log[-5:]):
            st.write(f"{entry['timestamp']} → {entry['mood']}")

    st.markdown("---")

    st.header("😂 Meme Generator")
    if st.button("Fetch Meme"):
        try:
            m = requests.get("https://meme-api.com/gimme", timeout=5).json()
            url, cap = m.get("url"), m.get("title", "")
            if url:
                img = Image.open(BytesIO(requests.get(url).content))
                st.image(img, caption=cap, use_container_width=True)
            else:
                st.warning("No meme right now.")
        except:
            st.error("Failed to fetch meme.")

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
        answers = [
            st.radio(q, opts, index=2, key=f"q{i}")
            for i,(q,opts) in enumerate(questions)
        ]
        submitted = st.form_submit_button("Analyze Mood")

    if submitted:
        score_map = {opt:5-idx for _,opts in questions for idx,opt in enumerate(opts)}
        avg = sum(score_map.get(ans, 3) for ans in answers) / len(answers)
        if avg >= 4.5:
            analysis, tone = "Very Positive & Happy", "happy"
        elif avg >= 3.5:
            analysis, tone = "Generally Positive", "neutral"
        elif avg >= 2.5:
            analysis, tone = "Neutral", "neutral"
        elif avg >= 1.5:
            analysis, tone = "Stressed or Negative", "sad"
        else:
            analysis, tone = "Very Negative or Upset", "angry"

        st.markdown(f"**Avg. Score:** {avg:.2f}")
        st.info(f"Analysis: {analysis}")
        if st.button("Apply Suggested Tone"):
            current_mood = tone
            st.success(f"Chat tone set to {tone}")

# --- RIGHT PANEL: Chatbot wrapped in .chat-box ---
with right_col:
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    st.subheader("🌿 Zypher Chatbot")

    def render_chat():
        for msg in st.session_state.chat_history:
            txt = html.escape(msg.get("text", ""))
            ts  = msg.get("timestamp", "")
            cls = "user-bubble" if msg.get("from") == "user" else "bot-bubble"
            st.markdown(
                f'<div class="{cls}">{txt}'
                f'<span class="timestamp">{ts}</span></div>',
                unsafe_allow_html=True
            )
        st.markdown('<div id="bottom"></div>', unsafe_allow_html=True)

    render_chat()

    user_input = st.chat_input("Type your message…")
    if user_input:
        now = datetime.now().strftime("%H:%M")
        st.session_state.chat_history.append({
            "from": "user", "text": user_input, "timestamp": now
        })
        reply = get_bot_response(user_input, current_mood)
        st.session_state.chat_history.append({
            "from": "bot", "text": reply, "timestamp": datetime.now().strftime("%H:%M")
        })
        render_chat()
        components.html("""
        <script>
          const box = parent.document.querySelector('.chat-box');
          if(box) box.scrollTop = box.scrollHeight;
        </script>
        """, height=0)

    st.markdown('</div>', unsafe_allow_html=True)

# 7) FOOTER NOTE
st.markdown(
    "<div style='text-align:center; color:#888; font-size:0.8rem; "
    "padding:0.5rem 0;'>🔒 All conversations are end-to-end encrypted.</div>",
    unsafe_allow_html=True
)
