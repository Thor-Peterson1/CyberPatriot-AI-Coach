import streamlit as st
from groq import Groq

# Page Configuration & Layout
st.set_page_config(page_title="CyberPatriot AI Coach", page_icon="🛡️", layout="wide")

# Initialize the ai client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Upgraded Educational System Prompt
SYSTEM_PROMPT = """
You are an educational CyberPatriot mentor. Your goal is to help students learn Windows and Linux hardening by providing thorough, detailed breakdowns of security concepts.

Follow this response structure to help them learn effectively:
1. THE SOLUTION CONCEPT: Provide a comprehensive, detailed explanation of the underlying security theory (e.g., exactly how an exploit works, what a registry key controls, or the specific security risks involved). Feel free to explain the mechanics thoroughly.
2. THE ACTIONABLE STEP: Provide the specific command, policy path, or solution step. Include necessary context or common parameters so the student learns how to use them.
3. THE LEARNING TEST: End your response with exactly ONE short follow-up question or practice drill to verify their understanding.

Structure your response clearly with clean markdown bolding and bullet points so it remains easy to read.
"""


# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
if "user_prompts" not in st.session_state:
    st.session_state.user_prompts = []

# SIDEBAR: Sidebar Configuration & History Tracker
st.sidebar.title("🛡️ CP-OPS Dashboard")
st.sidebar.markdown("---")

# Quick Study Quiz Button
st.sidebar.markdown("### 📝 Study Tools")
if st.sidebar.button("🚀 Generate Quick Quiz", use_container_width=True):
    # Inject an automated instruction to the AI to start a quiz immediately
    quiz_trigger = "Give me a brand new, random CyberPatriot practice quiz challenge right now!"
    st.session_state.messages.append({"role": "user", "content": quiz_trigger})
    
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=st.session_state.messages,
        stream=False
    )
    output_text = completion.choices.message.content
    st.session_state.messages.append({"role": "assistant", "content": output_text})
    st.session_state.user_prompts.append("📝 Triggered Quick Quiz")

# Visual list of what the user has asked during this session
st.sidebar.markdown("---")
st.sidebar.markdown("### 🕒 Session History Logs")
if st.session_state.user_prompts:
    for idx, prompt in enumerate(reversed(st.session_state.user_prompts)):
        st.sidebar.caption(f"{idx+1}. {prompt[:28]}...")
else:
    st.sidebar.info("Your prompt history logs will compile here as you chat.")

# MAIN PANEL: Headers and Instructions
st.title("🛡️ CYBERPATRIOT OPS MENTOR")
st.caption("24/7 Practice assistant. Enter your query or request a practice drill below.")
st.markdown("---")

# Render Chat History on Main Screen
for msg in st.session_state.messages:
    if msg["role"] != "system":
        # Check if it was an automated quiz button trigger to keep the UI clean
        if msg["content"] != "Give me a brand new, random CyberPatriot practice quiz challenge right now!":
            st.chat_message(msg["role"]).write(msg["content"])

# Handle Live User Input
if user_input := st.chat_input("Ask a question, or type 'Give me a Linux drill'..."):
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.user_prompts.append(user_input) # Log to sidebar history

    # Generate response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=st.session_state.messages,
            stream=False
        )
        
        output_text = completion.choices.message.content
        response_placeholder.write(output_text)
        st.session_state.messages.append({"role": "assistant", "content": output_text})
        
        # Rerun to refresh the sidebar logs view instantly
        st.rerun()
