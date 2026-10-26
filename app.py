import streamlit as st
from groq import Groq

# Page Configuration & Title
st.set_page_config(page_title="CyberPatriot AI Coach", page_icon="🛡️")
st.title("🛡️ CYBERPATRIOT O.P.S. MENTOR")
st.markdown("---")
st.sidebar.markdown("### 🛠️ Training Modules")
st.sidebar.info("Select or type drills for Windows Hardening, Linux Forensics, or Packet Tracer Auditing.")


# Initialize AI
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Inject the hardcoded "System Prompt" into the AI
SYSTEM_PROMPT = """
You are an educational CyberPatriot mentor. Your goal is to help students learn Windows and Linux hardening by guiding them to answers, not just handing them over.

Follow this response structure to help them learn effectively:
1. THE SOLUTION CONCEPT: Explain the security theory first (e.g., why a certain registry key or user group matters).
2. THE ACTIONABLE STEP: Provide the specific command, policy path, or solution. Keep code snippets short and focused.
3. THE LEARNING TEST: End your response with exactly ONE short follow-up question or practice drill to see if they understand how to apply the fix.

Keep your entire response brief, punchy, and structured with clean markdown bolding. Do not write long paragraphs.
"""

# Initialize chat history in the web session
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Display past messages to the user
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

# Handle new user input
if user_input := st.chat_input("Ask a question or type 'Give me a Linux scenario'"):
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Stream the AI response live to the screen
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        # Call ai model via Groq
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=st.session_state.messages,
            stream=False
        )
        
        output_text = completion.choices[0].message.content
        response_placeholder.write(output_text)
        st.session_state.messages.append({"role": "assistant", "content": output_text})
