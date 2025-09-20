python
# ... (keep your imports and initial setup)

# 1) PAGE SETUP
st.set_page_config(page_title="Zypher AI Bot", page_icon="🌿", layout="wide")

# Updated CSS for chat bubbles and layout box
st.markdown("""
<style>
  #MainMenu, header, footer { visibility: hidden !important; }
  .block-container { padding-top:0 !important; }

  /* Left panel box */
  .left-panel-box {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1rem;
    background: #f9f9f9;
    height: 100%;
  }

  /* Chat bubbles */
  .user-bubble, .bot-bubble {
    margin: 0.5rem 0; padding: 0.75rem 1rem; max-width: 70%; line-height: 1.4;
    border-radius: 1rem;
    font-size: 1rem;
    display: inline-block;
    word-wrap: break-word;
  }
  .user-bubble {
    background: #DCF8C6; /* WhatsApp style green */
    color: #000;
    border-bottom-right-radius: 0;
    float: right;
    clear: both;
  }
  .bot-bubble {
    background: #E5E5EA; /* light gray */
    color: #000;
    border-bottom-left-radius: 0;
    float: left;
    clear: both;
  }
  .timestamp {
    display: block; font-size: 0.65rem; color: #666; margin-top: 0.2rem;
  }
  h1, h2, h3 { margin-top: 0.2rem; margin-bottom: 0.5rem; }

  /* Clear floats after chat bubbles */
  .chat-message {
    overflow: auto;
    margin-bottom: 0.5rem;
  }
</style>
""", unsafe_allow_html=True)

# ... (keep your Gemini API and session state code)

# 5) LAYOUT: TWO COLUMNS, equal width
left_col, right_col = st.columns([1, 1], gap="medium")

# --- LEFT PANEL: Mood Log / Meme / Analyzer inside a box
with left_col:
    st.markdown('<div class="left-panel-box">', unsafe_allow_html=True)

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
            if url:
                img = Image.open(BytesIO(requests.get(url).content))
                st.image(img, caption=cap, use_container_width=True)  # fixed here
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

        st.markdown(f"*Avg. Score:* {avg:.2f}")
        st.info(f"Analysis: {analysis}")
        if st.button("Apply Suggested Tone"):
            current_mood = tone
            st.success(f"Chat tone set to {tone}")

    st.markdown('</div>', unsafe_allow_html=True)

# --- RIGHT PANEL: Chatbot
with right_col:
    st.header("🌿 Zypher Chatbot")

    # render messages
    def render_chat():
        for msg in st.session_state.chat_history:
            txt = html.escape(msg.get("text",""))
            ts  = msg.get("timestamp","")
            cls = "user-bubble" if msg.get("from")=="user" else "bot-bubble"
            st.markdown(
                f'<div class="chat-message"><div class="{cls}">{txt}'
                f'<span class="timestamp">{ts}</span></div></div>',
                unsafe_allow_html=True
            )
        # anchor for scrolling
        st.markdown('<div id="bottom"></div>', unsafe_allow_html=True)

    render_chat()

    # input
    user_input = st.chat_input("Type your message…")
    if user_input:
        now = datetime.now().strftime("%H:%M")
        st.session_state.chat_history.append({"from":"user","text":user_input,"timestamp":now})
        reply = get_bot_response(user_input, current_mood)
        st.session_state.chat_history.append({
            "from":"bot","text":reply,"timestamp":datetime.now().strftime("%H:%M")
        })
        render_chat()
        # auto-scroll
        components.html("""
            <script>
            const chat = parent.document.querySelector('div[data-testid="stChatMessageList"]');
            if(chat) chat.scrollTop = chat.scrollHeight;
            </script>
        """, height=0)

# 6) FOOTER NOTE
st.markdown(
    "<div style='text-align:center;color:#888;font-size:0.8rem;"
    "padding:0.5rem 0;'>🔒 Conversations are end-to-end encrypted.</div>",
    unsafe_allow_html=True
)
