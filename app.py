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
    layout="wide",
)

# ---------------- Nuke All Top Padding/Margins ----------------
st.markdown("""
<style>
  /* Remove default Streamlit header/menu/footer */
  #MainMenu, header, footer { visibility: hidden !important; }

  /* Ensure app container has zero top & bottom padding */
  [data-testid="stAppViewContainer"] {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
  }

  /* Ensure the main “block-container” is flush */
  .block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
  }

  /* Force all column children to start at top with no extra padding */
  [data-testid="stColumns"] > div {
    margin-top: 0 !important;
    padding-top: 0 !important;
  }
  
  /* PANEL STYLES */
  .left-panel, .chat-panel {
    border-radius: 8px;
    padding: 1rem;
    height: 90vh;
    overflow-y: auto;
  }
  .left-panel { background: #f0f2f6; }
  .chat-panel { background: #ffffff; }

  /* MESSAGE BUBBLES */
  .user-bubble, .bot-bubble {
    margin: 0.5rem 0;
    padding: 0.5rem 1rem;
    max-width: 75%;
    display: inline-block;
    line-height: 1.4;
  }
  .user-bubble {
    background: #e1f5fe;
    border-radius: 1rem 1rem 0.5rem 1rem;
  }
  .bot-bubble {
    background: #c8e6c9;
    border-radius: 1rem 1rem 1rem 0.5rem;
  }
  .timestamp {
    display: block;
    font-size: 0.7rem;
    color: #555;
    margin-top: 0.2rem;
  }

  /* Tight header margins */
  h1,h2,h3,h4,h5,h6 {
    margin-top: 0.2rem !important;
    margin-bottom: 0.5rem !important;
  }
</style>
""", unsafe_allow_html=True)

# ---------------- Gemini API Setup ----------------
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ GEMINI_API_KEY not found in Secrets!")
    st.stop()
genai.configure(api_key=api_key)

# ---------------- Fallback Responses ----------------
fallback_responses = {
    "happy":   ["That’s amazing! 🌸","Keep shining! ✨","Happiness looks good on you! 💖"],
    "sad":     ["I hear you 💙","It’s okay to not feel okay 🌧️","Sending a virtual hug 🤗"],
    "angry":   ["Take a deep breath 🧘","It’s okay to vent 💢","Want a calming tip?"],
    "neutral": ["I’m listening 👂","Tell me more…","Thanks for sharing 💭"],
}

# ---------------- Session State ----------------
st.session_state.setdefault("chat_history", [])
st.session_state.setdefault("mood_log", [])

# ---------------- Bot Response Helper ----------------
def get_bot_response(text: str, mood: str="neutral") -> str:
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content(text)
        return resp.text.strip()
    except Exception:
        return random.choice(fallback_responses.get(mood, ["I’m here for you. 💙"]))

# ---------------- Two-Column Layout ----------------
left_col, right_col = st.columns([1, 2], gap="small")

# ===== LEFT PANEL =====
with left_col:
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)

    # Mood Log
    st.header("🌸 Mood Log")
    current_mood = st.radio(
        "Select mood", ["happy","sad","angry","neutral"],
        horizontal=True, index=3
    )
    if st.button("Log Mood"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.mood_log.append({"mood": current_mood, "timestamp": now})
        st.success(f"Logged '{current_mood}' at {now}")

    if st.session_state.mood_log:
        st.subheader("📅 Recent Entries")
        for entry in reversed(st.session_state.mood_log[-5:]):
            st.write(f"{entry.get('timestamp','')} → {entry.get('mood','')}")

    st.markdown("---")

    # Meme Generator
    st.header("😂 Meme Generator")
    if st.button("Fetch Meme"):
        try:
            meme = requests.get("https://meme-api.com/gimme", timeout=5).json()
            url, title = meme.get("url"), meme.get("title","")
            if url:
                img = Image.open(BytesIO(requests.get(url).content))
                st.image(img, caption=title, use_column_width=True)
            else:
                st.warning("No meme available.")
        except:
            st.error("Failed to fetch meme.")

    st.markdown("---")

    # Mood Analyzer
    st.header("📋 Mood Analyzer")
    questions = [
        {"q":"How have you felt today?","opts":["Very good","Good","Neutral","Bad","Very bad"]},
        {"q":"Motivation level?","opts":["Very high","High","Neutral","Low","Very low"]},
        {"q":"Sleep quality?","opts":["Excellent","Good","Average","Poor","Very poor"]},
        {"q":"Stress level?","opts":["Very low","Low","Moderate","High","Very high"]},
        {"q":"Social connection?","opts":["Very connected","Connected","Neutral","Disconnected","Very disconnected"]},
    ]
    with st.form("mood_form"):
        answers = [
            st.radio(item["q"], item["opts"], index=2, key=f"q{i}")
            for i, item in enumerate(questions)
        ]
        analyze = st.form_submit_button("Analyze Mood")
    if analyze:
        # Score mapping
        score_map = {opt:5-idx for q in questions for idx,opt in enumerate(q["opts"])}
        avg = sum(score_map.get(ans,3) for ans in answers) / len(answers)

        if   avg>=4.5: analysis,tone="Very Positive & Happy","happy"
        elif avg>=3.5: analysis,tone="Generally Positive","neutral"
        elif avg>=2.5: analysis,tone="Neutral","neutral"
        elif avg>=1.5: analysis,tone="Stressed or Negative","sad"
        else:          analysis,tone="Very Negative or Upset","angry"

        st.markdown(f"**Avg. Score:** {avg:.2f}")
        st.info(f"Analysis: {analysis}")
        if st.button("Apply Suggested Tone"):
            current_mood = tone
            st.success(f"Chat tone set to '{tone}'")

    st.markdown('</div>', unsafe_allow_html=True)

# ===== RIGHT PANEL =====
with right_col:
    st.markdown('<div class="chat-panel" id="chat-panel">', unsafe_allow_html=True)
    st.markdown("### 🌿 Zypher Chatbot")

    # Render chat history safely
    def render_chat():
        for msg in st.session_state.chat_history:
            txt = html.escape(msg.get("text",""))
            ts  = msg.get("timestamp","")
            cls = "user-bubble" if msg.get("from","bot")=="user" else "bot-bubble"
            st.markdown(
                f'<div class="{cls}">{txt}'
                f'<span class="timestamp">{ts}</span></div>',
                unsafe_allow_html=True
            )
        # bottom anchor for auto-scroll
        st.markdown('<div id="bottom"></div>', unsafe_allow_html=True)

    render_chat()
    st.markdown('</div>', unsafe_allow_html=True)

    # Input & generate response
    user_input = st.chat_input("Type your message…")
    if user_input:
        ts = datetime.now().strftime("%H:%M")
        st.session_state.chat_history.append({
            "from":"user","text":user_input,"timestamp":ts
        })
        bot_txt = get_bot_response(user_input, current_mood)
        st.session_state.chat_history.append({
            "from":"bot","text":bot_txt,"timestamp":datetime.now().strftime("%H:%M")
        })
        render_chat()
        # auto-scroll via JS
        components.html(
            """
            <script>
              const p = parent.document.getElementById('chat-panel');
              if (p) p.scrollTop = p.scrollHeight;
            </script>
            """,
            height=0
        )

# ---------------- Footer ----------------
st.markdown(
    "<div style='text-align:center; color:#888; font-size:0.8rem;"
    " padding:0.5rem 0;'>🔒 Conversations are end-to-end encrypted.</div>",
    unsafe_allow_html=True
)

