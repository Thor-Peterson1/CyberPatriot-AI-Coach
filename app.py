import streamlit as st
from groq import Groq

# 1. Page Configuration & Title
st.set_page_config(page_title="CyberPatriot AI Coach", page_icon="🛡️")
st.title("🛡️ CyberPatriot Training Mentor")
st.caption("Off-season practice assistant. Enter your query or request a practice drill below.")

# 2. Initialize the free Groq client (uses Streamlit Secrets for the API Key)
# You can get a free key instantly at ://groq.com
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. Inject the hardcoded "System Prompt" so the AI behaves like a CyberPatriot Coach
SYSTEM_PROMPT = """
You are an expert CyberPatriot mentor and Systems Administrator. 
Your goal is to help students learn Windows and Linux hardening.
CRITICAL: Do NOT give them copy-paste scripts, answers, or direct solutions. 
Instead, guide them with concepts, command syntax examples, or quiz them by simulating a broken/unsecure server image. 
Focus on user management, password policies, firewalls, and audit logs.
"""

# 4. Initialize chat history in the web session
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# 5. Display past messages to the user
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

# 6. Handle new user input
if user_input := st.chat_input("Ask a question or type 'Give me a Linux scenario'"):
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 7. Stream the AI response live to the screen
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        # Call free Llama model via Groq
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=st.session_state.messages,
            stream=False
        )
        
        output_text = completion.choices[0].message.content
        response_placeholder.write(output_text)
        st.session_state.messages.append({"role": "assistant", "content": output_text})
