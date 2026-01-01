import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from datetime import datetime

# ------------------ LOAD ENV ------------------
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ Gemini API key not found. Check your .env file or Streamlit secrets.")
    st.info("💡 For local: Add GEMINI_API_KEY to .env file\n\n💡 For Streamlit Cloud: Add to Secrets in dashboard")
    st.stop()

# ------------------ CONFIGURE GEMINI ------------------
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="You are a helpful, friendly, and knowledgeable AI assistant. Provide clear, concise, and accurate responses."
)

# ------------------ STREAMLIT PAGE CONFIG ------------------
st.set_page_config(
    page_title="Gemini AI Chatbot",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ------------------ CUSTOM CSS ------------------
st.markdown("""
    <style>
    /* Main chat container */
    .stChatMessage {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    
    /* Sidebar styling */
    .sidebar-content {
        padding: 1rem;
    }
    
    /* Stats card */
    .stat-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    /* Chat input */
    .stChatInputContainer {
        border-top: 2px solid #667eea;
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown("""
    <div class="main-header">
        <h1>✨ NK Chatbot</h1>
        <p>Powered by Google's Gemini 2.5 Flash</p>
    </div>
""", unsafe_allow_html=True)

# ------------------ TOOLBAR ------------------
if "messages" in st.session_state and st.session_state.messages:
    msg_count = len(st.session_state.messages)
    user_msgs = len([m for m in st.session_state.messages if m["role"] == "user"])
    st.markdown(f"💬 **{msg_count}** messages • 🧑 **{user_msgs}** from you")

st.markdown("---")

# Default settings (since sidebar is removed)
temperature = 0.7
max_tokens = 1024

# ------------------ SESSION STATE ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------ DISPLAY CHAT HISTORY ------------------
if not st.session_state.messages:
    st.markdown("""
        <div style='text-align: center; padding: 3rem; color: #666;'>
            <h3>👋 Welcome! Start a conversation below.</h3>
            <p>Try asking me anything - I'm here to help!</p>
        </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "✨"):
        st.markdown(msg["content"])

# ------------------ USER INPUT ------------------
user_input = st.chat_input("Type your message here...")

if user_input:
    # Show user message
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().isoformat()
    })

    # Show loading spinner
    with st.chat_message("assistant", avatar="✨"):
        with st.spinner("Thinking..."):
            try:
                # Build conversation context
                context = ""
                for msg in st.session_state.messages[-5:]:  # Last 5 messages for context
                    context += f"{msg['role']}: {msg['content']}\n"
                
                # Generate response
                response = model.generate_content(
                    user_input,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    )
                )

                # Safe response extraction
                if response.candidates and response.candidates[0].content.parts:
                    bot_reply = response.candidates[0].content.parts[0].text
                else:
                    bot_reply = "⚠️ I couldn't generate a response. Please try again."

            except Exception as e:
                st.error(f"Error: {str(e)}")
                bot_reply = "⚠️ Something went wrong. Please try again or adjust your message."

        st.markdown(bot_reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply,
        "timestamp": datetime.now().isoformat()
    })