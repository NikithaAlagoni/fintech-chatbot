import streamlit as st
import anthropic

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinBot – AI Financial Assistant",
    page_icon="💳",
    layout="centered"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Background */
    .stApp { background-color: #f0f4ff; }

    /* Header bar */
    .header-box {
        background: linear-gradient(135deg, #1a3c6e 0%, #2563eb 100%);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        color: white;
    }
    .header-box h1 { margin: 0; font-size: 2rem; font-weight: 800; color: white; }
    .header-box p  { margin: 6px 0 0; font-size: 0.95rem; opacity: 0.85; color: white; }

    /* Chat bubbles */
    .user-bubble {
        background: #2563eb;
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0 8px 60px;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .assistant-bubble {
        background: white;
        color: #1e293b;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 60px 8px 0;
        font-size: 0.95rem;
        line-height: 1.5;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .label { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.05em;
             text-transform: uppercase; color: #94a3b8; margin-bottom: 2px; }

    /* Suggestion chips */
    .chips-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
    .chip {
        background: white;
        border: 1.5px solid #2563eb;
        color: #2563eb;
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 0.82rem;
        font-weight: 500;
        cursor: pointer;
    }

    /* Input area */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 1.5px solid #cbd5e1;
        padding: 12px 16px;
        font-size: 0.95rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #1a3c6e, #2563eb);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        width: 100%;
    }
    .stButton > button:hover { opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are FinBot, a friendly and knowledgeable AI financial assistant 
for OnePay — an all-in-one fintech platform offering banking, high-yield savings, 
credit cards, investing, and crypto.

Your role is to help users with:
- Understanding their account features (savings rates, credit limits, crypto options)
- Explaining financial concepts clearly and simply
- Helping users make smart money decisions
- Answering questions about transfers, payments, and transactions
- Providing guidance on budgeting and saving strategies

Tone: Warm, clear, and professional. Avoid jargon. Always encourage good financial habits.
If asked something outside finance, politely redirect to financial topics.
Keep responses concise — 2 to 4 sentences unless more detail is truly needed."""

# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-box">
    <h1>💳 FinBot</h1>
    <p>Your AI-powered financial assistant — ask me anything about your money.</p>
</div>
""", unsafe_allow_html=True)

# ── API key input ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    api_key_input = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        value=st.session_state.api_key
    )
    if api_key_input:
        st.session_state.api_key = api_key_input

    st.markdown("---")
    st.markdown("### 💡 About FinBot")
    st.markdown("""
FinBot is a customer-facing AI assistant prototype built with:
- 🤖 **Claude 3 Haiku** (Anthropic)
- 🧠 **Agentic prompt design**
- 🔁 **Multi-turn conversation memory**
- 🖥️ **Streamlit UI**

*Built as a research prototype exploring agentic AI for fintech customer experience.*
    """)

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ── Suggestion chips ───────────────────────────────────────────────────────────
suggestions = [
    "What's my savings rate?",
    "How do I transfer money?",
    "Explain high-yield savings",
    "How does crypto work here?",
    "Tips to save more money",
]

st.markdown('<div class="chips-row">' +
    "".join(f'<span class="chip">💬 {s}</span>' for s in suggestions) +
    '</div>', unsafe_allow_html=True)

# ── Chat history ───────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="label">You</div><div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="label">FinBot</div><div class="assistant-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────
st.markdown("---")
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input(
        "Message",
        placeholder="Ask me about savings, transfers, credit cards...",
        label_visibility="collapsed",
        key="user_input"
    )
with col2:
    send = st.button("Send ➤")

# ── Response logic ─────────────────────────────────────────────────────────────
if send and user_input.strip():
    if not st.session_state.api_key:
        st.error("Please enter your Anthropic API key in the sidebar.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})

        with st.spinner("FinBot is thinking..."):
            try:
                client = anthropic.Anthropic(api_key=st.session_state.api_key)
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=512,
                    system=SYSTEM_PROMPT,
                    messages=st.session_state.messages
                )
                reply = response.content[0].text
            except Exception as e:
                reply = f"⚠️ Error: {str(e)}"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
