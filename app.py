import streamlit as st
from groq import Groq
import time

# 1. Page Configuration & Layout
st.set_page_config(page_title="CyberPatriot AI Coach", page_icon="🛡️", layout="wide")

# 2. Initialize the ai client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. Dynamic Educational System Prompts
GENERAL_SYSTEM_PROMPT = """
You are an educational CyberPatriot mentor. Your goal is to help students learn Windows and Linux hardening by providing thorough, detailed breakdowns of security concepts.

Follow this response structure to help them learn effectively:
1. THE SOLUTION CONCEPT: Provide a comprehensive, detailed explanation of the underlying security theory (e.g., exactly how an exploit works, what a registry key controls, or the specific security risks involved). Feel free to explain the mechanics thoroughly.
2. THE ACTIONABLE STEP: Provide the specific command, policy path, or solution step. Include necessary context or common parameters so the student learns how to use them.
3. THE LEARNING TEST: End your response with exactly ONE short follow-up question or practice drill to verify their understanding.

Structure your response clearly with clean markdown bolding and bullet points so it remains easy to read.
"""

QUIZ_SYSTEM_PROMPT = """
You are an objective CyberPatriot testing engine. 
Generate exactly 3 multiple choice questions and 1 free response question based on the selected operating system scope.
DO NOT include any answers, explanations, solution concepts, or actionable steps in your initial response. Only provide the questions and choice options (A, B, C, D).
When the user submits their answers, grade them accurately and provide the corrections.
"""

# 4. Initialize session state tracking for message history and multi-chat sessions
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = "Session 1"
if "session_counter" not in st.session_state:
    st.session_state.session_counter = 1

# Initialize active session list if empty
if st.session_state.current_session_id not in st.session_state.sessions:
    st.session_state.sessions[st.session_state.current_session_id] = {
        "messages": [{"role": "system", "content": GENERAL_SYSTEM_PROMPT}],
        "logs": []
    }

# Fetch pointers for active session
active_session = st.session_state.sessions[st.session_state.current_session_id]

if "session_counter" not in st.session_state:
    st.session_state.session_counter = 1
# ADD THIS LINE RIGHT HERE:
if "total_words_processed" not in st.session_state:
    st.session_state.total_words_processed = 0


# Helper function to track data volume sizes
def track_usage(text_input):
    words = len(str(text_input).split())
    st.session_state.total_words_processed += words


# 5. SIDEBAR: Dashboard Configuration
st.sidebar.title("🛡️ CP-OPS Dashboard")
st.sidebar.markdown("---")

# Target Platform Selection
st.sidebar.markdown("### 🎯 Training Target Scope")
system_choice = st.sidebar.selectbox(
    "Choose target environment:",
    ["General / Mixed", "Windows Server / Desktop", "Linux (Ubuntu/Debian)", "Cisco Packet Tracer"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ Study Tools")

# TOOL 1: Generate Security Checklist
if st.sidebar.button("📋 Generate Security Checklist", use_container_width=True):
    checklist_trigger = f"Act as an automated security scanner. Generate a highly technical, point-by-point security hardening checklist for {system_choice}. Do not write a conversational introduction or conclusion. Format it completely as checkboxes (- [ ]) grouped by categories like User Management, Software/Services, Firewalls, and Audit Policies."
    active_session["messages"].append({"role": "user", "content": checklist_trigger})
    active_session["logs"].append(f"📋 Generated {system_choice} Checklist")
    track_usage(checklist_trigger)
    
    with st.spinner("Compiling security checklist..."):
        time.sleep(0.5)
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=active_session["messages"],
            stream=False
        )
        output_text = completion.choices[0].message.content
        track_usage(output_text)
        active_session["messages"].append({"role": "assistant", "content": output_text})
    st.rerun()


# TOOL 2: Generate Short Quiz
if st.sidebar.button("🚀 Generate Quick Quiz", use_container_width=True):
    quiz_payload = [{"role": "system", "content": QUIZ_SYSTEM_PROMPT}, {"role": "user", "content": f"Create a short 3-MCQ and 1-Free Response quiz tracking core security metrics on {system_choice}."}]
    active_session["logs"].append("📝 Generated Quick Quiz")
    track_usage(checklist_trigger)
    
    with st.spinner("Generating clean quiz..."):
        time.sleep(0.5)
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=quiz_payload,
            stream=False
        )
        output_text = completion.choices[0].message.content
        track_usage(output_text)
        active_session["messages"].append({"role": "assistant", "content": output_text})
    st.rerun()

# TOOL 3: Reveal Quiz Answers Shortcut
if st.sidebar.button("🔓 Reveal Quiz Answers", use_container_width=True):
    reveal_trigger = "Explain the step-by-step corrections for this exercise and break down the solution mechanics and command examples for each question to help me study."

    active_session["messages"].append({"role": "user", "content": reveal_trigger})
    active_session["logs"].append("🔓 Revealed Quiz Answers")
    
    with st.spinner("Retrieving quiz answer key..."):
        time.sleep(0.5)
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=active_session["messages"],
            stream=False
        )
        # FIXED: Added [0] here to prevent the AttributeError
        output_text = completion.choices[0].message.content
        active_session["messages"].append({"role": "assistant", "content": output_text})
    st.rerun()


# TOOL 4: Competition Round Reviewer
if st.sidebar.button("📊 Review Last Competition Round", use_container_width=True):
    review_trigger = f"Provide a comprehensive technical audit reviewing typical core scoring components found specifically in CyberPatriot Training Rounds and Round 1 for {system_choice}. Breakdown specific point-earning actions (e.g. initial media file removal, default password updates, standard unauthorized user auditing, disabling forbidden features like guest logs/Telnet) and detail the exact remediation verification commands."
    active_session["messages"].append({"role": "user", "content": review_trigger})
    active_session["logs"].append("📊 Requested Round Review")
    
    with st.spinner("Analyzing competitive metrics..."):
        time.sleep(0.5)
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=active_session["messages"],
            stream=False
        )
        output_text = completion.choices[0].message.content
        active_session["messages"].append({"role": "assistant", "content": output_text})
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 💬 Session Manager")

# Fresh Chat Creation Button
if st.sidebar.button("➕ Start New Chat Session", use_container_width=True):
    st.session_state.session_counter += 1
    new_id = f"Session {st.session_state.session_counter}"
    st.session_state.sessions[new_id] = {
        "messages": [{"role": "system", "content": GENERAL_SYSTEM_PROMPT}],
        "logs": []
    }
    st.session_state.current_session_id = new_id
    st.rerun()

# Clear Logs Tool (NEW QOL BUTTON)
if st.sidebar.button("🗑️ Clear Current Logs", use_container_width=True):
    st.session_state.sessions[st.session_state.current_session_id] = {
        "messages": [{"role": "system", "content": GENERAL_SYSTEM_PROMPT}],
        "logs": []
    }
    st.rerun()

# TOOL 5: Export Session to Text File (NEW QOL FEATURE)
st.sidebar.markdown("---")
st.sidebar.markdown("### 💾 Export Data")

# NEW VISUAL MONITOR COMPONENT
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Live Analytics Monitor")
st.sidebar.metric(label="Data Volume Processed", value=f"{st.session_state.total_words_processed} words")
st.sidebar.caption("Infrastructure Billing Estimate: **$0.00 (Free Tier)**")


# Compile all conversation history into a single string
full_transcript = ""
for msg in active_session["messages"]:
    if msg["role"] != "system" and msg["content"] != "Give me a brand new, random CyberPatriot practice quiz challenge right now!":
        speaker = "STUDENT" if msg["role"] == "user" else "MENTOR"
        full_transcript += f"[{speaker}]:\n{msg['content']}\n\n{'='*40}\n\n"

if full_transcript:
    st.sidebar.download_button(
        label="📥 Download Study Notes (.txt)",
        data=full_transcript,
        file_name=f"cyberpatriot_study_notes_{st.session_state.current_session_id.lower().replace(' ', '_')}.txt",
        mime="text/plain",
        use_container_width=True
    )
else:
    st.sidebar.caption("Chat with the mentor or generate a checklist to unlock download export options.")


# Interactive Historical Navigation List
st.sidebar.markdown("#### 🕒 Historic Session Logs")
for sid in list(st.session_state.sessions.keys()):
    button_label = f"📁 {sid} (Active)" if sid == st.session_state.current_session_id else f"📄 {sid}"
    if st.sidebar.button(button_label, key=f"nav_{sid}", use_container_width=True):
        st.session_state.current_session_id = sid
        st.rerun()

# 6. MAIN PANEL: Primary App View
st.title("🛡️ CYBERPATRIOT OPS MENTOR")
st.caption("24/7 Practice assistant. Select an environment scope, launch study modules, or attach diagnostics files below.")
st.markdown(f"**Active Workspace Context:** `{system_choice}` | **Session:** `{st.session_state.current_session_id}`")
st.markdown("---")

# Render Past Chat Messages
for msg in active_session["messages"]:
    if msg["role"] != "system":
        if msg["content"] != "Give me a brand new, random CyberPatriot practice quiz challenge right now!":
            st.chat_message(msg["role"]).write(msg["content"])

# Interactive Quick Prompt Starters (NEW QOL LAYOUT)
if len(active_session["messages"]) <= 1:
    st.markdown("#### 💡 Quick Prompt Starters")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 Explain Account Lockout Policies", use_container_width=True):
            st.session_state["shortcut_input"] = "Explain how to audit and configure Account Lockout Policies to prevent brute-force attacks."
    with col2:
        if st.button("🚫 Show Common Forbidden Software", use_container_width=True):
            st.session_state["shortcut_input"] = "List the most common forbidden software and media file extensions that cause penalties in competition images."

# Image Artifact Upload Integration
uploaded_image = st.file_uploader("🖼️ Upload system error screenshots or policy diagnostics pictures for analysis:", type=["png", "jpg", "jpeg"])
if uploaded_image is not None:
    st.success(f"Successfully processed image file: '{uploaded_image.name}'! Reference this upload in the prompt window below to run forensics validations.")

# 7. Handle Live Dialogue Input Loops
# Safely pull a value if clicked from the shortcut boxes
default_input_val = st.session_state.pop("shortcut_input") if "shortcut_input" in st.session_state else ""

# Handle user input via chat box entry
user_entry = st.chat_input("Ask a tracking question, check configurations, or paste script strings...", key="chat_field")

# Workaround to handle both typing and button triggers cleanly
if default_input_val:
    user_input = default_input_val
else:
    user_input = user_entry

if user_input:
    contextualized_prompt = f"[{system_choice} Context] {user_input}. Note: If this is an answer submission for a quiz, evaluate it and show the solution breakdown."
    
    st.chat_message("user").write(user_input)
    active_session["messages"].append({"role": "user", "content": contextualized_prompt})
    active_session["logs"].append(user_input)
    track_usage(contextualized_prompt) # <--- ADD THIS

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        with st.spinner("Calculating educational layout..."):
            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=active_session["messages"],
                stream=False
            )
        
        output_text = completion.choices[0].message.content
        track_usage(output_text) # <--- ADD THIS
        response_placeholder.write(output_text)
        active_session["messages"].append({"role": "assistant", "content": output_text})
        
        st.rerun()

