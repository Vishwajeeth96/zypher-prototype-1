# app.py — Zypher • Youth Mental Wellness (Polished + GenAI-safe)
# Put your transparent logo into: assets/team_zypher_logo_transparent.png
# Run locally: pip install -r requirements.txt
# Then: streamlit run app.py

import os
import random
import requests
import pandas as pd
import difflib
import streamlit as st
from io import BytesIO
from PIL import Image

# ========== PAGE CONFIG ==========
# Use your repo path (assets/team_zypher_logo_transparent.png) as page_icon after you push the file to GitHub
ICON_PATH = "assets/team_zypher_logo_transparent.png"
if os.path.exists(ICON_PATH):
    st.set_page_config(page_title="Zypher • Youth Mental Wellness", page_icon=ICON_PATH, layout="centered")
else:
    # fallback emoji icon while testing before pushing assets
    st.set_page_config(page_title="Zypher • Youth Mental Wellness", page_icon="🌱", layout="centered")

# ========== CSS / THEME ==========
st.markdown(
    """
    <style>
      :root {
        --bg1: #071123;
        --bg2: #0b3954;
        --accent1: #00C9A7;
        --accent2: #8A2BE2;
      }
      body {
        background: linear-gradient(135deg, var(--bg1), var(--bg2));
        color: #EAFDFC;
      }
      .container {
        background: rgba(255,255,255,0.03);
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.45);
      }
      .user-bubble {
        background: linear-gradient(90deg, var(--accent2), #5b2ee0);
        color: white;
        padding: 10px 14px;
        border-radius: 14px 14px 4px 14px;
        margin: 6px 0;
        max-width: 78%;
        float: right;
        clear: both;
      }
      .bot-bubble {
        background: rgba(255,255,255,0.08);
        color: #EAFDFC;
        padding: 10px 14px;
        border-radius: 14px 14px 14px 4px;
        margin: 6px 0;
        max-width: 78%;
        float: left;
        clear: both;
      }
      .stButton>button {
        background: linear-gradient(90deg, var(--accent1), var(--accent2));
        color: #042027;
        font-weight: 700;
        border-radius: 12px;
        padding: 8px 12px;
      }
      .footer { color: #CFEFE6; text-align:center; padding:8px; font-size:13px; }
      .chat-container::after { content: ""; display: table; clear: both; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ========== DATA / DEFAULTS ==========
PREDEFINED_REPLIES = {
    "happy": ["That's great! Keep smiling 😄", "Yay! Stay happy 🌟"],
    "sad": ["I’m sorry you’re feeling sad. Take a deep breath 🌱", "It's okay to feel down sometimes 💙"],
    "stressed": ["Try to relax and take a short break 🧘‍♂️", "Stress is temporary. You got this 💪"],
    "anxious": ["It’s okay to feel anxious. You’re not alone 💙", "Focus on breathing — small steps."],
    "default": ["I hear you. Keep sharing if you want 💬", "I’m here to listen 🌱"]
}

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

MEME_API = "https://meme-api.com/gimme"

# ========== SESSION STATE ==========
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "canned_df" not in st.session_state:
    st.session_state.canned_df = None
if "active_mood_category" not in st.session_state:
    st.session_state.active_mood_category = "okay"
if "use_ai" not in st.session_state:
    st.session_state.use_ai = True

# ========== HELPERS ==========
def load_canned_from_file(uploaded_file):
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
    df = st.session_state.canned_df
    if df is None:
        return None
    user_text_norm = user_text.strip().lower()
    exact = df[df["user_phrase_norm"] == user_text_norm]
    if not exact.empty:
        return exact.iloc[0]["bot_reply"]
    choices = df["user_phrase_norm"].tolist()
    matches = difflib.get_close_matches(user_text_norm, choices, n=3, cutoff=threshold)
    if matches:
        row = df[df["user_phrase_norm"] == matches[0]].iloc[0]
        return row["bot_reply"]
    for idx, phrase in enumerate(choices):
        if phrase in user_text_norm:
            return df.iloc[idx]["bot_reply"]
    return None

def find_mood_dict_reply(user_text, mood_key):
    dict_for_mood = MOOD_DICT.get(mood_key, {})
    txt = user_text.strip().lower()
    for phrase, response in dict_for_mood.items():
        if phrase == txt:
            return response
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

# ========== GEN AI LOADER (safe) ==========
def init_genai_model():
    """
    Try to import google.generativeai and configure model.
    Returns (model_object, error_str_or_None).
    """
    try:
        import google.generativeai as genai
    except Exception as e:
        return None, f"genai-not-installed: {e}"

    # prefer Streamlit secrets (deployed on Streamlit Cloud)
    api_key = None
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except Exception:
        api_key = os.getenv("GOOGLE_API_KEY")

    # allow quick local testing by pasting into sidebar (won't be saved to repo)
    if not api_key:
        pasted = st.sidebar.text_input("Paste GenAI key (dev only)", type="password")
        if pasted:
            api_key = pasted

    if not api_key:
        return None, "no-api-key"

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model, None
    except Exception as e:
        return None, str(e)

genai_model, genai_error = init_genai_model()

def call_genai(user_text, tone_hint="empathetic"):
    """Call GenAI model if available, otherwise raise an exception."""
    if genai_model is None:
        raise RuntimeError(f"GenAI not available: {genai_error}")
    # Simple prompt framing
    prompt = f"You are Zypher, a friendly mental wellness assistant. Tone: {tone_hint}. Answer briefly and supportively.\nUser: {user_text}\nAssistant:"
    resp = genai_model.generate_content(prompt)
    # resp may contain .text
    try:
        return resp.text.strip()
    except Exception:
        return str(resp)

def get_reply(user_text):
    # 1) canned dataset
    canned = find_canned_reply(user_text)
    if canned:
        return canned
    # 2) mood dict
    mood_reply = find_mood_dict_reply(user_text, st.session_state.active_mood_category)
    if mood_reply:
        return mood_reply
    # 3) AI if enabled
    if st.session_state.get("use_ai", True):
        try:
            tone = st.session_state.active_mood_category
            ai_resp = call_genai(user_text, tone_hint=tone)
            if ai_resp:
                return ai_resp
        except Exception as e:
            # don't crash; fall through
            print("GenAI call failed:", e)
    # 4) baseline
    return baseline_keyword_reply(user_text)

# ========== SIDEBAR (onboarding + settings) ==========
with st.sidebar:
    st.header("👋 Onboard")
    name = st.text_input("Name", value="")
    age = st.number_input("Age", min_value=10, max_value=120, value=18)
    gender = st.selectbox("Gender", ["Prefer not to say", "Male", "Female", "Other"])
    if st.button("Save profile"):
        st.success("Profile saved ✅")
    st.markdown("---")
    st.subheader("AI settings")
    st.checkbox("Use AI (GenAI)", value=st.session_state.get("use_ai", True), key="use_ai")
    if genai_model is None:
        if genai_error and "genai-not-installed" in genai_error:
            st.warning("Gemini SDK not installed in environment. Add google-generativeai to requirements.txt.")
        elif genai_error == "no-api-key":
            st.info("No GenAI API key found. Add it to Streamlit Secrets as GOOGLE_API_KEY or paste it here.")
    st.markdown("---")
    st.subheader("Upload canned responses (optional)")
    st.markdown("CSV with columns `user_phrase,bot_reply,category(optional)`")
    uploaded = st.file_uploader("Upload CSV/JSON of canned Q→A", type=["csv","json"])
    if uploaded:
        df = load_canned_from_file(uploaded)
        if df is not None:
            st.session_state.canned_df = df
            st.success(f"Loaded {len(df)} canned pairs.")

# ========== MAIN PAGE ==========
st.markdown('<div class="container">', unsafe_allow_html=True)
# show logo if in assets
if os.path.exists(ICON_PATH):
    st.image(ICON_PATH, width=200)
st.title("🌱 Zypher — Youth Mental Wellness")
st.caption("Chat • Mood Analyzer • Memes — Prototype")

tabs = st.tabs(["Chat", "Mood Analyzer", "Memes", "Mood Log", "Settings"])

# ---------- CHAT TAB ----------
with tabs[0]:
    st.subheader("💬 Talk to ZypherBot")
    col1, col2 = st.columns([4,1])
    with col1:
        user_input = st.text_input("Say something...", key="chat_input")
    with col2:
        mood_select = st.selectbox("Bot tone", ["harassed", "notwilling", "traumatized", "funny", "okay"], index= ["harassed","notwilling","traumatized","funny","okay"].index(st.session_state.active_mood_category))
        if st.button("Apply mood"):
            st.session_state.active_mood_category = mood_select
            st.success(f"Active mood set to {mood_select}")

    if st.button("Send"):
        if not user_input or user_input.strip() == "":
            st.warning("Type something first!")
        else:
            st.session_state.chat_history.append({"from":"user","text":user_input})
            reply = get_reply(user_input)
            st.session_state.chat_history.append({"from":"bot","text":reply})

    st.markdown("**Conversation**")
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for item in st.session_state.chat_history[::-1]:
        text = item.get("text","")
        if item.get("from") == "user":
            st.markdown(f"<div class='user-bubble'>{st.session_state.get('user_profile',{}).get('name','You')}: {st.utils.safestring.html.escape(text)}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-bubble'>ZypherBot: {st.utils.safestring.html.escape(text)}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- MOOD ANALYZER ----------
with tabs[1]:
    st.subheader("📋 Mood Analyzer")
    questions = [
        {"q":"How have you been feeling generally today?","opts":["Very good","Good","Neutral","Bad","Very bad"]},
        {"q":"How motivated do you feel right now?","opts":["Very motivated","Somewhat motivated","Neutral","Little motivated","Not motivated at all"]},
        {"q":"How well did you sleep last night?","opts":["Very well","Well","Average","Poorly","Very poorly"]},
        {"q":"How would you rate your stress level currently?","opts":["Very low","Low","Moderate","High","Very high"]},
        {"q":"How connected have you felt with others recently?","opts":["Very connected","Somewhat connected","Neutral","Somewhat disconnected","Very disconnected"]}
    ]
    with st.form("mood_form"):
        answers=[]
        for i,qq in enumerate(questions):
            answers.append(st.radio(qq["q"], qq["opts"], index=2, key=f"q{i}"))
        submit = st.form_submit_button("Analyze Mood")
    if submit:
        score_map = {"Very good":5,"Good":4,"Neutral":3,"Average":3,"Bad":2,"Very bad":1,
                     "Very motivated":5,"Somewhat motivated":4,"Little motivated":2,"Not motivated at all":1,
                     "Very well":5,"Well":4,"Poorly":2,"Very poorly":1,
                     "Very low":5,"Low":4,"Moderate":3,"High":2,"Very high":1,
                     "Very connected":5,"Somewhat connected":4,"Somewhat disconnected":2,"Very disconnected":1}
        total = sum(score_map.get(a,3) for a in answers)
        avg = total / len(questions)
        if avg >= 4.5:
            analysis = "Very Positive and Happy"; suggested = "funny"
        elif avg >= 3.5:
            analysis = "Generally Positive"; suggested = "okay"
        elif avg >= 2.5:
            analysis = "Neutral"; suggested = "okay"
        elif avg >= 1.5:
            analysis = "Stressed or Negative"; suggested = "traumatized"
        else:
            analysis = "Very Negative or Upset"; suggested = "harassed"
        st.markdown(f"**Average mood score:** {avg:.2f}")
        st.info(f"Analysis: {analysis}")
        st.markdown(f"**Suggested chat tone:** `{suggested}`")
        if st.button("Use suggested tone for chat"):
            st.session_state.active_mood_category = suggested
            st.success(f"Applied mood `{suggested}` to chat.")

# ---------- MEMES ----------
with tabs[2]:
    st.subheader("😂 Meme Generator")
    if st.button("Generate Meme"):
        try:
            meme = requests.get(MEME_API, timeout=6).json()
            img_url = meme.get("url"); title = meme.get("title")
            if img_url:
                resp = requests.get(img_url, timeout=8)
                img = Image.open(BytesIO(resp.content))
                st.image(img, caption=title)
            else:
                st.warning("Could not fetch meme right now.")
        except Exception as e:
            st.warning("Meme fetch failed: " + str(e))

# ---------- MOOD LOG ----------
with tabs[3]:
    st.subheader("📓 Mood Log (history)")
    colA, colB = st.columns([2,1])
    with colA:
        mood = st.selectbox("Log current mood", ["😊 Happy","😔 Sad","😡 Angry","😴 Tired","😎 Chill"])
    with colB:
        if st.button("Log Mood"):
            if "mood_log" not in st.session_state:
                st.session_state.mood_log = []
            st.session_state.mood_log.append({"mood": mood})
            st.success("Mood logged.")
    if st.session_state.get("mood_log"):
        st.write(pd.DataFrame(st.session_state.mood_log))

# ---------- SETTINGS ----------
with tabs[4]:
    st.subheader("⚙️ Settings & Data")
    st.markdown("Upload a CSV with columns: `user_phrase,bot_reply,category(optional)` to add canned replies.")
    st.markdown("For GenAI: add your key to Streamlit Secrets as `GOOGLE_API_KEY` (recommended) or paste in the sidebar for local testing.")
    st.markdown("---")
    st.markdown("Development notes: For deployment ensure `requirements.txt` contains: streamlit, pandas, requests, Pillow, google-generativeai")

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<div class='footer'>✨ Built by <b>Team Zypher</b> — Hackathon Prototype</div>", unsafe_allow_html=True)
