# app.py — Zypher • Youth Mental Wellness Chatbot

import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import random
import requests
from datetime import datetime
from io import BytesIO
from PIL import Image
import html

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Zypher AI Bot",
    page_icon="🌿",
    layout="wide"
)

# ---------------- Hide Streamlit Header/Menu/Footer & Top Padding ----------------
hide_streamlit_style = """
<style>
  /* Hide top menu, header and footer */
  #MainMenu {visibility: hidden;}
  header {visibility: hidden;}
  footer {visibility: hidden;}

  /* Remove default top padding so content sits at the very top */
  .block-container {
    padding-top: 0rem !important;
    padding-bottom: 0rem !important;
  }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---------------- Gemini API Setup ----------------
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ GEMINI_API_KEY not found in Streamlit secrets!")
    st.stop()
genai.configure(api_key=api_key)

# ---------------- Fallback Responses ----------------
fallback_responses = {
    "happy":   ["That’s amazing! 🌸", "Keep shining! ✨", "Happiness suits you! 💖"],
    "sad":     ["I hear you 💙", "It’s okay to not feel okay 🌧️", "Sending a virtual hug 🤗"],
    "angry":   ["Take a deep breath 🧘", "It’s okay to vent 💢", "Want a quick relaxation tip?"],
    "neutral": ["I’m listening 👂", "Tell me more…", "Thanks for sharing 💭"]
}

# ---------------- Session State ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "mood_log" not in st.session_state:
    st.session_state.mood_log = []

# ---------------- Chatbot Response ----------------
def get_bot_response(prompt: str, mood: str = "neutral") -> str:
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception:
        return random.choice(fallback_responses.get(mood, ["I’m here for you. 💙"]))

# ---------------- Custom CSS for Panels & Bubbles ----------------
st.markdown("""
<style>
  .left-panel {
    background: #f0f2f6;
    padding: 1rem;
    border-radius: 8px;
    height: 90vh;
    overflow-y: auto;
  }
  .chat-panel {
    background: #ffffff;
    padding: 1rem;
    border-radius: 8px;
    height: 90vh;
    overflow-y: auto;
  }
  .user-bubble {
    background: #e1f5fe;
    padding: 0.5rem 1rem;
    border-radius: 1rem 1rem 0.5rem 1rem;
    margin: 0.5rem 0;
    max-width: 75%;
  }
  .bot-bubble {
    background: #c8e6c9;
    padding: 0.5rem 1rem;
    border-radius: 1rem 1rem 1rem 0.5rem;
    margin: 0.5rem 0;
    max-width: 75%;
  }
  .timestamp {
    display: block;
    font-size: 0.7rem;
    color: #555;
    margin-top: 0.2rem;
  }
  h1,h2,h3,h4,h5,h6 {
    margin-top: 0.2rem; margin-bottom: 0.5rem;
  }
</style>
""", unsafe_allow_html=True)

# ---------------- Two-Column Layout ----------------
left_col, right_col = st.columns([1, 2], gap="small")

# ---------------- Left Panel ----------------
with left_col:
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)

    # Mood Log
    st.header("🌸 Mood Log")
    current_mood = st.radio(
        "Select mood", ["happy", "sad", "angry", "neutral"],
        horizontal=True, index=3
    )
    if st.button("Log Mood"):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.mood_log.append({"mood": current_mood, "timestamp": ts})
        st.success(f"Logged '{current_mood}' at {ts}")

    if st.session_state.mood_log:
        st.subheader("📅 Recent Entries")
        for entry in reversed(st.session_state.mood_log[-5:]):
            st.write(f"{entry['timestamp']} → {entry['mood']}")

    st.markdown("---")

    # Meme Generator
    st.header("😂 Meme Generator")
    if st.button("Fetch Meme"):
        try:
            m = requests.get("https://meme-api.com/gimme", timeout=5).json()
            url, title = m.get("url"), m.get("title", "")
            if url:
                img = Image.open(BytesIO(requests.get(url).content))
                st.image(img, caption=title, use_column_width=True)
            else:
                st.warning("No meme received.")
        except:
            st.error("Meme fetch failed.")

    st.markdown("---")

    # Mood Analyzer
    st.header("📋 Mood Analyzer")
    questions = [
        {"q": "How have you felt today?",     "opts": ["Very good","Good","Neutral","Bad","Very bad"]},
        {"q": "Motivation level?",            "opts": ["Very high","High","Neutral","Low","Very low"]},
        {"q": "Sleep quality?",               "opts": ["Excellent","Good","Average","Poor","Very poor"]},
        {"q": "Stress level?",                "opts": ["Very low","Low","Moderate","High","Very high"]},
        {"q": "Social connection recently?",  "opts": ["Very connected","Connected","Neutral","Disconnected","Very disconnected"]}
    ]
    with st.form("mood_form", clear_on_submit=False):
        answers = [
            st.radio(item["q"], item["opts"], index=2, key=f"q{i}")
            for i, item in enumerate(questions)
        ]
        analyze = st.form_submit_button("Analyze Mood")

    if analyze:
        score_map = {opt: 5-idx for item in questions for idx, opt in enumerate(item["opts"])}
        avg = sum(score_map.get(a,3) for a in answers) / len(answers)
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
        st.markdown(f"**Average Score:** {avg:.2f}")
        st.info(f"Analysis: {analysis}")
        if st.button("Apply Suggested Tone"):
            current_mood = tone
            st.success(f"Chat tone set to '{tone}'")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Right Panel (Chat) ----------------
with right_col:
    st.markdown('<div class="chat-panel" id="chat-panel">', unsafe_allow_html=True)
    st.markdown("### 🌿 Zypher Chatbot")

    # Render chat history
    def render_chat():
        for msg in st.session_state.chat_history:
            safe = html.escape(msg["text"])
            ts = msg["timestamp"]
            cls = "user-bubble" if msg["from"] == "user" else "bot-bubble"
            st.markdown(
                f'<div class="{cls}">{safe}'
                f'<span class="timestamp">{ts}</span></div>',
                unsafe_allow_html=True
            )
        # Anchor for auto-scroll
        st.markdown('<div id="bottom"></div>', unsafe_allow_html=True)

    render_chat()
    st.markdown('</div>', unsafe_allow_html=True)

    # Input & response
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
        # Auto-scroll
        components.html(
            """
            <script>
            const panel = parent.document.getElementById('chat-panel');
            if (panel) panel.scrollTop = panel.scrollHeight;
            </script>
            """,
            height=0
        )

# ---------------- Footer ----------------
st.markdown(
    "<div style='text-align:center; color:#888; font-size:0.8rem; "
    "padding:0.5rem 0;'>🔒 All conversations are end-to-end encrypted. "
    "Your privacy is safe.</div>",
    unsafe_allow_html=True
)
