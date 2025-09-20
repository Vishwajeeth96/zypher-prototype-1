import streamlit as st
import random, requests, datetime, html
from textblob import TextBlob
from io import BytesIO
from PIL import Image
import streamlit.components.v1 as components

# ----- CSS (Dark mode + Chat bubbles) -----
st.markdown("""
<style>
body, .stApp {
    background-color: #121212;
    color: #e0e0e0;
}
.stButton>button {
    background-color: #333;
    color: white;
    border-radius: 8px;
    border: 1px solid #555;
}
.user-bubble {
    background: #2e7d32;
    color: white;
    padding: 10px;
    border-radius: 12px;
    margin: 5px;
    max-width: 75%;
}
.bot-bubble {
    background: #1e88e5;
    color: white;
    padding: 10px;
    border-radius: 12px;
    margin: 5px;
    max-width: 75%;
}
.timestamp {
    font-size: 0.7em;
    color: #bbb;
    float: right;
    margin-left: 10px;
}
</style>
""", unsafe_allow_html=True)

# ----- Session state -----
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "mood_log" not in st.session_state:
    st.session_state.mood_log = []

# ----- Mood Analyzer -----
def analyze_mood(text):
    blob = TextBlob(text)
    score = blob.sentiment.polarity
    if score > 0.2: mood = "😊 Positive"
    elif score < -0.2: mood = "😔 Negative"
    else: mood = "😐 Neutral"
    st.session_state.mood_log.append(
        {"text": text, "mood": mood, "time": datetime.datetime.now().strftime("%H:%M:%S")}
    )
    return mood

# ----- Chatbot (Rule-based) -----
def chatbot_response(user_input):
    ui = user_input.lower()
    if "hello" in ui or "hi" in ui:
        return "Hey there! 🤖 Zypher here. How’s your day?"
    if "joke" in ui:
        return random.choice([
            "😂 Why don’t skeletons fight each other? They don’t have the guts!",
            "🤣 Parallel lines have so much in common. It’s a shame they’ll never meet.",
            "😆 Why did the computer go to the doctor? Because it caught a virus!"
        ])
    if "how are you" in ui:
        return "I’m just a bot, but I’m feeling chatty today! ⚡"
    return random.choice([
        "🤔 Interesting… tell me more!",
        "😎 Got it! Wanna hear a joke?",
        "🤖 Processing… Done! But seriously, that’s cool."
    ])

# ----- Render Chat -----
def render_chat():
    for msg in st.session_state.chat_history:
        txt = html.escape(msg.get("text",""))
        ts  = msg.get("timestamp","")
        cls = "user-bubble" if msg.get("from")=="user" else "bot-bubble"
        prefix = "🧑 You: " if msg.get("from")=="user" else "🤖 Zypher: "
        st.markdown(
            f'<div class="{cls}"><b>{prefix}</b>{txt}'
            f'<span class="timestamp">{ts}</span></div>',
            unsafe_allow_html=True
        )
    # auto-scroll to latest (like ChatGPT)
    components.html("""
        <script>
        var chat = parent.document.querySelector('section.main');
        if(chat) chat.scrollTop = chat.scrollHeight;
        </script>
    """, height=0)

# ----- UI Layout -----
st.title("🤖 Zypher: Mood-Aware Chatbot with Humor")

left_col, right_col = st.columns([2,1])

with left_col:
    st.header("💬 Chat with Zypher")
    render_chat()

    user_input = st.text_input("Type your message:")
    if st.button("Send"):
        if user_input.strip():
            mood = analyze_mood(user_input)
            st.session_state.chat_history.append({
                "from": "user",
                "text": user_input,
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
            })
            bot_reply = chatbot_response(user_input)
            st.session_state.chat_history.append({
                "from": "bot",
                "text": f"{bot_reply} \n\n*(Mood detected: {mood})*",
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
            })
            st.rerun()

    # Meme Generator
    st.header("😂 Meme Generator")
    if st.button("Fetch Meme"):
        try:
            m = requests.get("https://meme-api.com/gimme", timeout=5).json()
            url, cap = m.get("url"), m.get("title","")

            # check if it's an image
            if url and url.lower().endswith((".jpg", ".jpeg", ".png")):
                try:
                    img_data = requests.get(url, timeout=5).content
                    img = Image.open(BytesIO(img_data))
                    st.image(img, caption=cap, use_container_width=True)
                except Exception:
                    st.warning("⚠️ Meme image could not be loaded, showing text instead:")
                    st.info(cap or "😂 Keep smiling!")
            else:
                # fallback to Imgflip static meme if not valid image
                backup = requests.get("https://api.imgflip.com/get_memes", timeout=5).json()
                memes = backup.get("data", {}).get("memes", [])
                if memes:
                    pick = random.choice(memes)
                    st.image(pick["url"], caption=pick["name"], use_container_width=True)
                else:
                    st.warning("⚠️ No meme available, here’s a text joke:")
                    st.info(cap or "😂 Keep smiling!")

        except Exception as e:
            st.error(f"Failed to fetch meme. ({e})")

with right_col:
    st.header("📊 Mood Analyzer Log")
    for entry in st.session_state.mood_log:
        st.write(f"📝 '{entry['text']}' → {entry['mood']} ({entry['time']})")
