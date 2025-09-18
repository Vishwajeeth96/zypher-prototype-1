# app.py — Zypher Youth Mental-Wellness Prototype (Integrated + Mood Analyzer)
# Run locally: pip install -r requirements.txt
# then: streamlit run app.py

import streamlit as st
import pandas as pd
import requests
import random
from io import BytesIO
from PIL import Image
import difflib
import json

# ====== PAGE CONFIG ======
st.set_page_config(page_title="Zypher • Youth Mental Wellness", page_icon="🌱", layout="centered")

# ====== CSS / THEME (glassmorphic, youth colors) ======
st.markdown(
    """
    <style>
      :root {
        --bg1: #0f1724;   /* deep */
        --bg2: #0b3954;   /* teal/blue */
        --accent1: #6EE7B7; /* mint */
        --accent2: #8A2BE2; /* violet */
      }
      body {
        background: linear-gradient(135deg, var(--bg1), var(--bg2));
        color: #E6F2F1;
      }
      .main {
        background: rgba(255,255,255,0.04);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.4);
      }
      h1, h2, h3 { color: #EAFDFC; text-align:center; margin:0; }
      .stButton>button {
        background: linear-gradient(90deg, #6EE7B7, #8A2BE2);
        color: #042027;
        font-weight: 600;
        border-radius: 12px;
        padding: 8px 14px;
      }
      .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>select {
        background: rgba(255,255,255,0.06);
        color: #EAFDFC;
        border-radius: 10px;
      }
      .footer { color: #CFEFE6; text-align:center; padding:8px; font-size:13px; }
    </style>
    """,
    unsafe_allow_html=True
)

# ====== Built-in small reply sets (you can replace with full ones in responses.json) ======
PREDEFINED_REPLIES = {
    "happy": ["That's great! Keep smiling 😄", "Yay! Stay happy 🌟"],
    "sad": ["I’m sorry you’re feeling sad. Take a deep breath 🌱", "It's okay to feel down sometimes 💙"],
    "stressed": ["Try to relax and take a short break 🧘‍♂️", "Stress is temporary. You got this 💪"],
    "anxious": ["It’s okay to feel anxious. You’re not alone 💙", "Focus on breathing — small steps."],
    "default": ["I hear you. Keep sharing if you want 💬", "I’m here to listen 🌱"]
}

# Minimal mood dictionaries. Replace/expand by adding a file `responses.json` to your repo or upload via UI.
MOOD_DICT = {
    "harassed": {
        "i feel disgusting": "You’re not disgusting. The shame belongs to the person who hurt you, not you.",
        "maybe it’s my fault": "No. Harassment is never your fault. Ever."
    },
    "notwilling": {
        "i don’t want to talk": "That’s okay. I’ll just be here with you.",
        "please leave me alone": "I’ll respect your space — I’ll be here if you change your mind."
    },
    "traumatized": {
        "i can’t stop thinking about what happened": "That’s trauma replaying itself. You didn't deserve this.",
        "i feel broken": "You are not broken. You’re hurt, and healing takes time."
    },
    "funny": {
        "my brain won’t shut up": "Same — it's like having 57 tabs open and one is playing music."
    },
    "okay": {
        "i feel fine": "Fine is enough. No need to force amazing every day."
    }
}

MOOD_MENU = {
    "1": ("harassed", "Harassed / Triggered"),
    "2": ("notwilling", "Not Willing to Talk"),
    "3": ("traumatized", "Traumatized / Highly Distressed"),
    "4": ("funny", "Light / Funny / Stigma-breaking"),
    "5": ("okay", "Okay / Neutral")
}

# Meme API
MEME_API = "https://meme-api.com/gimme"

# ====== SESSION STATE INIT ======
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of dicts: {"from":"user"/"bot","text":...}
if "mood_log" not in st.session_state:
    st.session_state.mood_log = []
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {"name": "", "age": None, "gender": ""}
if "canned_df" not in st.session_state:
    st.session_state.canned_df = None
if "responses_file_loaded" not in st.session_state:
    st.session_state.responses_file_loaded = False
if "active_mood_category" not in st.session_state:
    st.session_state.active_mood_category = "okay"

# ====== HELPERS ======
def load_canned_from_file(uploaded_file):
    """Load CSV or JSON of canned responses. Expected CSV columns: user_phrase, bot_reply[, category]"""
    try:
        if uploaded_file is None:
            return None
        name = uploaded_file.name.lower()
        if name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif name.endswith(".json"):
            df = pd.read_json(uploaded_file)
        else:
            st.error("Upload a .csv or .json file (columns: user_phrase, bot_reply, optional category).")
            return None
        # normalize lower
        if "user_phrase" in df.columns and "bot_reply" in df.columns:
            df["user_phrase_norm"] = df["user_phrase"].astype(str).str.lower()
            return df
        else:
            st.error("File must contain columns: user_phrase, bot_reply")
            return None
    except Exception as e:
        st.error("Failed to load canned responses file: " + str(e))
        return None

def find_canned_reply(user_text, threshold=0.65):
    """Fuzzy-match user_text to canned responses (if loaded). Returns reply or None."""
    df = st.session_state.canned_df
    if df is None:
        return None
    user_text_norm = user_text.strip().lower()
    # exact match
    exact = df[df["user_phrase_norm"] == user_text_norm]
    if not exact.empty:
        return exact.iloc[0]["bot_reply"]
    # fuzzy match using difflib ratio
    choices = df["user_phrase_norm"].tolist()
    # find top close match
    matches = difflib.get_close_matches(user_text_norm, choices, n=3, cutoff=threshold)
    if matches:
        best = matches[0]
        row = df[df["user_phrase_norm"] == best].iloc[0]
        return row["bot_reply"]
    # fallback: token containment / phrase-in-input
    for idx, phrase in enumerate(choices):
        if phrase in user_text_norm:
            return df.iloc[idx]["bot_reply"]
    return None

def find_mood_dict_reply(user_text, mood_key):
    # Exact then partial matching within mood dict
    dict_for_mood = MOOD_DICT.get(mood_key, {})
    txt = user_text.strip().lower()
    # exact phrase
    for phrase, response in dict_for_mood.items():
        if phrase == txt:
            return response
    # partial word match
    for phrase, response in dict_for_mood.items():
        if any(word in txt for word in phrase.split()):
            return response
    return None

def baseline_keyword_reply(user_text):
    text = user_text.lower()
    for key, replies in PREDEFINED_REPLIES.items():
        if key in text:
            return random.choice(replies)
    return random.choice(PREDEFINED_REPLIES["default"])

def get_reply(user_text):
    # 1) canned dataset (upload your 500-1000 responses CSV and this will be used)
    canned = find_canned_reply(user_text)
    if canned:
        return canned
    # 2) mood-specific dictionary (from Nanda)
    mood_reply = find_mood_dict_reply(user_text, st.session_state.active_mood_category)
    if mood_reply:
        return mood_reply
    # 3) keyword-based defaults
    return baseline_keyword_reply(user_text)

# ====== SIDEBAR: Onboarding + uploads ======
with st.sidebar:
    st.header("👋 Onboard")
    name = st.text_input("Name", value=st.session_state.user_profile.get("name",""))
    age = st.number_input("Age", min_value=10, max_value=120, value=st.session_state.user_profile.get("age") or 18)
    gender = st.selectbox("Gender", ["Prefer not to say", "Male", "Female", "Other"], index=0)
    if st.button("Save profile"):
        st.session_state.user_profile.update({"name": name, "age": age, "gender": gender})
        st.success("Profile saved ✅")

    st.markdown("---")
    st.subheader("Upload canned responses (optional)")
    st.markdown("Format: CSV with columns `user_phrase,bot_reply,category(optional)` — upload 500–1000 rows to improve answers.")
    uploaded = st.file_uploader("Upload CSV/JSON of canned Q→A", type=["csv","json"])
    if uploaded:
        df = load_canned_from_file(uploaded)
        if df is not None:
            st.session_state.canned_df = df
            st.session_state.responses_file_loaded = True
            st.success(f"Loaded {len(df)} canned pairs.")
    if st.session_state.responses_file_loaded:
        if st.button("Clear uploaded responses"):
            st.session_state.canned_df = None
            st.session_state.responses_file_loaded = False
            st.info("Cleared uploaded canned responses.")

# ====== MAIN PAGE ======
st.markdown('<div class="main">', unsafe_allow_html=True)
st.title("🌱 Zypher — Youth Mental Wellness")
st.caption("Chat • Mood Analyzer • Memes — Prototype")

tabs = st.tabs(["Chat", "Mood Analyzer", "Memes", "Mood Log", "Settings"])

# -----------------
# TAB: Chat
# -----------------
with tabs[0]:
    st.subheader("💬 Talk to ZypherBot (Prototype)")
    col1, col2 = st.columns([3,1])
    with col1:
        # mood category selector (choose or apply analyzer result later)
        mood_label = st.selectbox("Bot tone / mood", 
                                  ["harassed","notwilling","traumatized","funny","okay"],
                                  index=["harassed","notwilling","traumatized","funny","okay"].index(st.session_state.active_mood_category))
    with col2:
        if st.button("Apply selected mood"):
            st.session_state.active_mood_category = mood_label
            st.success(f"Active mood set to: {mood_label}")

    user_input = st.text_input("Type something (try: 'i feel disgusting' or 'i’m too tired')", key="chat_input")
    if st.button("Send"):
        if not user_input or user_input.strip() == "":
            st.warning("Type something first!")
        else:
            st.session_state.chat_history.append({"from":"user","text":user_input})
            reply = get_reply(user_input)
            st.session_state.chat_history.append({"from":"bot","text":reply})
    # Show chat history
    st.markdown("**Conversation**")
    for item in st.session_state.chat_history[::-1]:  # show latest first
        if item["from"] == "user":
            st.markdown(f"**You:** {item['text']}")
        else:
            st.markdown(f"**ZypherBot:** {item['text']}")

# -----------------
# TAB: Mood Analyzer (questionnaire)
# -----------------
with tabs[1]:
    st.subheader("📋 Mood Analyzer")
    st.markdown("Answer quickly — this creates a mood score and suggests a tone for the bot.")
    questions = [
        {"q":"How have you been feeling generally today?","opts":["Very good","Good","Neutral","Bad","Very bad"]},
        {"q":"How motivated do you feel right now?","opts":["Very motivated","Somewhat motivated","Neutral","Little motivated","Not motivated at all"]},
        {"q":"How well did you sleep last night?","opts":["Very well","Well","Average","Poorly","Very poorly"]},
        {"q":"How would you rate your stress level currently?","opts":["Very low","Low","Moderate","High","Very high"]},
        {"q":"How connected have you felt with others recently?","opts":["Very connected","Somewhat connected","Neutral","Somewhat disconnected","Very disconnected"]}
    ]

    with st.form("mood_form"):
        answers = []
        for i, qq in enumerate(questions):
            ans = st.radio(qq["q"], qq["opts"], index=2, key=f"q{i}")
            answers.append(ans)
        submit = st.form_submit_button("Analyze Mood")
    if submit:
        # Map answers to scores 5..1 (positive->higher)
        score_map = {"Very good":5,"Good":4,"Neutral":3,"Average":3,"Bad":2,"Very bad":1,
                     "Very motivated":5,"Somewhat motivated":4,"Little motivated":2,"Not motivated at all":1,
                     "Very well":5,"Well":4,"Poorly":2,"Very poorly":1,
                     "Very low":5,"Low":4,"Moderate":3,"High":2,"Very high":1,
                     "Very connected":5,"Somewhat connected":4,"Somewhat disconnected":2,"Very disconnected":1}
        total = 0
        for a in answers:
            total += score_map.get(a,3)
        avg = total / len(questions)
        # Interpret
        if avg >= 4.5:
            analysis = "Very Positive and Happy"
            suggested_mood = "funny"
        elif avg >= 3.5:
            analysis = "Generally Positive"
            suggested_mood = "okay"
        elif avg >= 2.5:
            analysis = "Neutral"
            suggested_mood = "okay"
        elif avg >= 1.5:
            analysis = "Stressed or Negative"
            suggested_mood = "traumatized"
        else:
            analysis = "Very Negative or Upset"
            suggested_mood = "harassed"

        st.markdown(f"**Average mood score:** {avg:.2f}")
        st.info(f"Analysis: {analysis}")
        st.markdown(f"**Suggested chat tone:** `{suggested_mood}`")
        if st.button("Use suggested tone for chat"):
            st.session_state.active_mood_category = suggested_mood
            st.success(f"Applied mood `{suggested_mood}` to chat.")

# -----------------
# TAB: Memes
# -----------------
with tabs[2]:
    st.subheader("😂 Meme Generator")
    if st.button("Generate Meme"):
        try:
            meme = requests.get(MEME_API, timeout=6).json()
            img_url = meme.get("url")
            title = meme.get("title")
            if img_url:
                resp = requests.get(img_url, timeout=8)
                img = Image.open(BytesIO(resp.content))
                st.image(img, caption=title)
            else:
                st.warning("Could not fetch meme right now.")
        except Exception as e:
            st.warning("Meme fetch failed: " + str(e))

# -----------------
# TAB: Mood Log (no chart)
# -----------------
with tabs[3]:
    st.subheader("📓 Mood Log (history)")
    colA, colB = st.columns([2,1])
    with colA:
        mood = st.selectbox("Log current mood", ["😊 Happy","😔 Sad","😡 Angry","😴 Tired","😎 Chill"])
    with colB:
        if st.button("Log Mood"):
            st.session_state.mood_log.append({"mood": mood})
            st.success("Mood logged.")
    if st.session_state.mood_log:
        st.write(pd.DataFrame(st.session_state.mood_log))

# -----------------
# TAB: Settings / Data upload instructions
# -----------------
with tabs[4]:
    st.subheader("⚙️ Settings & Data")
    st.markdown("""
    **How to improve bot responses quickly (recommended for 1–2 hour hackathon):**
    1. Prepare a CSV with columns: `user_phrase,bot_reply,category(optional)` — 200–1000 rows of typical user utterances and good bot replies.
    2. Upload it in the sidebar (or commit to repo as `responses.csv` and the app can be updated).
    3. The app will try exact match → fuzzy match → mood-dict → default replies.
    """)
    st.markdown("**Sample CSV rows (example):**")
    st.code('''user_phrase,bot_reply,category
"i feel disgusting","You’re not disgusting. The shame belongs to the person who hurt you.",harassed
"i'm so tired of everything","That sounds heavy — do you want to tell me more?",traumatized
"i need a laugh","Here, this meme might help! 😂",funny
''')
    st.markdown("---")
    st.markdown("**Development notes**")
    st.write("- To edit large mood dictionaries, add `responses.json` to repo with mood keys and phrase→reply mapping.")
    st.write("- For later improvement: use semantic embeddings + vector search (needs extra packages / API). For now, CSV + fuzzy-match works well offline.")

# ====== FOOTER ======
st.markdown("</div>", unsafe_allow_html=True)
st.markdown(
    """<div class="footer">✨ Built by <b>Team Zypher</b> | Youth Hackathon Prototype 2025 — Streamlit prototype</div>""",
    unsafe_allow_html=True
)

