#  Hello! Thanks for checking out my program!  #

import streamlit as st
from groq import Groq
import time
import base64

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

# 4. Initialize session state tracking variables
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = "Session 1"
if "session_counter" not in st.session_state:
    st.session_state.session_counter = 1
if "total_words_processed" not in st.session_state:
    st.session_state.total_words_processed = 0

# Initialize active session list if empty
if st.session_state.current_session_id not in st.session_state.sessions:
    st.session_state.sessions[st.session_state.current_session_id] = {
        "messages": [{"role": "system", "content": GENERAL_SYSTEM_PROMPT}],
        "logs": []
    }

# Fetch pointers for active session
active_session = st.session_state.sessions[st.session_state.current_session_id]

# HELPER: Define tracking logic BEFORE any button runs it
def track_usage(text_input):
    words = len(str(text_input).split())
    st.session_state.total_words_processed += words

# 5. SIDEBAR: Dashboard Configuration
st.sidebar.title("🛡️ CP-OPS Dashboard")
st.sidebar.markdown("---")

# Target Platform Selection
system_choice = st.sidebar.selectbox(
    "Choose target environment:",
    ["General / Mixed", "Windows Server / Desktop", "Linux (Ubuntu/Debian)", "Cisco Packet Tracer"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ Study Tools")

# TOOL 1: Generate Security Checklist
if st.sidebar.button("📋 Generate Security Checklist", use_container_width=True):
    checklist_trigger = f"Act as an automated security scanner. Generate a short, highly technical, point-by-point security hardening checklist for {system_choice}. Format each item starting strictly with '- [ ] ' so it can be parsed. Group them clearly."
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
        
        # Parse checklist items out of the response text and store them
        checklist_items = []
        for line in output_text.split("\n"):
            if line.strip().startswith("- [ ]") or line.strip().startswith("- [x]"):
                clean_item = line.replace("- [ ]", "").replace("- [x]", "").strip()
                if clean_item:
                    checklist_items.append(clean_item)
        
        # Save into session state with unique keys
        active_session["checklist"] = {item: False for item in checklist_items}
    st.rerun()

# TOOL 2: Generate Short Quiz
if st.sidebar.button("🚀 Generate Quick Quiz", use_container_width=True):
    quiz_payload = [{"role": "system", "content": QUIZ_SYSTEM_PROMPT}, {"role": "user", "content": f"Create a short 3-MCQ and 1-Free Response quiz tracking core security metrics on {system_choice}."}]
    active_session["logs"].append("📝 Generated Quick Quiz")
    track_usage(f"Quiz on {system_choice}")
    
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
    track_usage(reveal_trigger)
    
    with st.spinner("Retrieving quiz answer key..."):
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

# TOOL 4: Competition Round Reviewer
if st.sidebar.button("📊 Review Last Competition Round", use_container_width=True):
    review_trigger = f"Provide a comprehensive technical audit reviewing typical core scoring components found specifically in CyberPatriot Training Rounds and Round 1 for {system_choice}. Breakdown specific point-earning actions and detail the exact remediation verification commands."
    active_session["messages"].append({"role": "user", "content": review_trigger})
    active_session["logs"].append("📊 Requested Round Review")
    track_usage(review_trigger)
    
    with st.spinner("Analyzing competitive metrics..."):
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

st.sidebar.markdown("---")
st.sidebar.markdown("### 💬 Session Manager")

if st.sidebar.button("➕ Start New Chat Session", use_container_width=True):
    st.session_state.session_counter += 1
    new_id = f"Session {st.session_state.session_counter}"
    st.session_state.sessions[new_id] = {
        "messages": [{"role": "system", "content": GENERAL_SYSTEM_PROMPT}],
        "logs": []
    }
    st.session_state.current_session_id = new_id
    st.rerun()

if st.sidebar.button("🗑️ Clear Current Logs", use_container_width=True):
    st.session_state.sessions[st.session_state.current_session_id] = {
        "messages": [{"role": "system", "content": GENERAL_SYSTEM_PROMPT}],
        "logs": []
    }
    st.rerun()

st.sidebar.markdown("#### 🕒 Session Logs History")
for sid in list(st.session_state.sessions.keys()):
    button_label = f"📁 {sid} (Active)" if sid == st.session_state.current_session_id else f"📄 {sid}"
    if st.sidebar.button(button_label, key=f"nav_{sid}", use_container_width=True):
        st.session_state.current_session_id = sid
        st.rerun()

# TOOL: Quick-Copy Command Toolbox
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ Quick-Copy Toolbox")

os_tool_tab = st.sidebar.selectbox(
    "Select OS Commands:", 
    ["Windows PowerShell", "Linux (Ubuntu/Debian)", "Cisco IOS"]
)

if os_tool_tab == "Windows PowerShell":
    st.sidebar.code("""# Audit accounts & passwords
Get-LocalUser
Get-CimInstance Win32_UserAccount

# Disable guest account
Disable-LocalUser -Name "Guest"

# Enforce password complexity via SecPol
secedit /export /cfg C:\\secpol.cfg""", language="powershell")

elif os_tool_tab == "Linux (Ubuntu/Debian)":
    st.sidebar.code("""# Check active listening ports
sudo ss -tulpn

# Update package manager & secure ssh
sudo apt update && sudo apt upgrade
sudo nano /etc/ssh/sshd_config  # PermitRootLogin no

# Find unauthorized media files
sudo find / -name '*.mp3' -o -name '*.avi' -o -name '*.mov'""", language="bash")

elif os_tool_tab == "Cisco IOS":
    st.sidebar.code("""# Enable config mode & set password encryption
en
conf t
service password-encryption

# Secure console & vty lines
line con 0
password SECURE_PASS
login
exit""", language="text")

# TOOL 5: Export Transcript Feature (MOVED ABOVE ANALYTICS)
st.sidebar.markdown("---")
st.sidebar.markdown("### 💾 Export Data")

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

# LIVE ANALYTICS COMPONENT (MOVED TO ABSOLUTE BOTTOM)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Live Analytics Monitor")
st.sidebar.metric(label="Data Volume Processed", value=f"{st.session_state.total_words_processed} words")
st.sidebar.caption("Infrastructure Billing Estimate: **$0.00 (Free Tier)**")

    
# 6. MAIN PANEL UI & IMAGE STATE CAPTURE
st.title("🛡️ CYBERPATRIOT OPS MENTOR")
st.caption("24/7 Practice assistant. Select an environment scope, launch study modules, or attach diagnostics files below.")
st.markdown(f"**Active Workspace Context:** `{system_choice}` | **Session:** `{st.session_state.current_session_id}`")
st.markdown("---")

if "Windows" in system_choice:
    st.info("🌐 **SYSTEM WORKING CONTEXT: WINDOWS PLATFORM LAB**\n\nActive Direct Access Hardening Policies Enforced — Auditing user accounts, registry baselines, and local groups.")
elif "Linux" in system_choice:
    st.warning("🐧 **SYSTEM WORKING CONTEXT: LINUX ENVIRONMENT CORE**\n\nActive Systemd and Security Daemon Monitoring Active — Prioritizing service lockdowns, login profiles, and file configurations.")
elif "Cisco" in system_choice:
    st.success("📡 **SYSTEM WORKING CONTEXT: CISCO IOS APPLIANCE LAB**\n\nActive Infrastructure Access Control baselines active — Tracking network switches, vlan permissions, and router logs.")
else:
    st.info("⚙️ **GENERAL SECURITY METRICS** — Mixed-environment architecture overview active.")
st.markdown("---")

# INTERACTIVE CHECKLIST TRACKER WIDGET
if "checklist" in active_session and active_session["checklist"]:
    st.markdown("### 🎯 Live Hardening Checklist Tracker")
    st.caption("Check off items as you complete them in your virtual machine lab to track your hardening progress!")
    
    checklist_dict = active_session["checklist"]
    total_tasks = len(checklist_dict)
    
    # Render checkboxes
    completed_count = 0
    for task, is_checked in checklist_dict.items():
        # st.checkbox returns True if checked
        status = st.checkbox(task, value=is_checked, key=f"check_{task}")
        active_session["checklist"][task] = status
        if status:
            completed_count += 1
            
    # Progress Bar Calculation
    progress_percentage = completed_count / total_tasks if total_tasks > 0 else 0
    st.progress(progress_percentage, text=f"Hardening Progress: {completed_count}/{total_tasks} Tasks Completed ({int(progress_percentage * 100)}%)")
    
    if completed_count == total_tasks and total_tasks > 0:
        st.balloons()
        st.success("🎉 Incredible job! All hardening tasks for this checklist are complete!")
    
    st.markdown("---")

for msg in active_session["messages"]:
    if msg["role"] != "system":
        if msg["content"] != "Give me a brand new, random CyberPatriot practice quiz challenge right now!":
            # Handle text vs multimodal list content display safely
            if isinstance(msg["content"], list):
                text_content = next((item["text"] for item in msg["content"] if item["type"] == "text"), "")
                st.chat_message(msg["role"]).write(text_content)
            else:
                st.chat_message(msg["role"]).write(msg["content"])

if len(active_session["messages"]) <= 1:
    st.markdown("#### 💡 Quick Prompt Starters")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 Explain Account Lockout Policies", use_container_width=True):
            st.session_state["shortcut_input"] = "Explain how to audit and configure Account Lockout Policies to prevent brute-force attacks."
    with col2:
        if st.button("🚫 Show Common Forbidden Software", use_container_width=True):
            st.session_state["shortcut_input"] = "List the most common forbidden software and media file extensions that cause penalties in competition images."

# PERSISTENT UPLOADER: Save file to session state so it survives re-runs
uploaded_file = st.file_uploader("🖼️ Upload system error screenshots or policy diagnostics pictures for analysis:", type=["png", "jpg", "jpeg"], key="image_uploader_widget")

if uploaded_file is not None:
    st.session_state["persisted_image"] = uploaded_file
    st.success(f"Successfully attached: '{uploaded_file.name}'! Ready to send with your message.")

# 7. Live Input Loop & Multimodal Handler
default_input_val = st.session_state.pop("shortcut_input") if "shortcut_input" in st.session_state else ""
user_entry = st.chat_input("Ask a tracking question, check configurations, or paste script strings...", key="chat_field")

user_input = default_input_val if default_input_val else user_entry

if user_input:
    context_text = f"[{system_choice} Context] {user_input}. Note: If this is an answer submission for a quiz, evaluate it and show the solution breakdown."
    
    # Check if a persisted image exists in session state
    active_image = st.session_state.get("persisted_image", None)
    
    if active_image is not None:
        # Encode image to base64
        bytes_data = active_image.getvalue()
        base64_encoded_image = base64.b64encode(bytes_data).decode("utf-8")
        
        # Build Groq multimodal message block
        message_content = [
            {"type": "text", "text": context_text},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{active_image.type.split('/')[-1]};base64,{base64_encoded_image}"
                }
            }
        ]
        active_session["logs"].append(f"🖼️ Analyzed image: {active_image.name}")
    else:
        message_content = context_text
        active_session["logs"].append(user_input)

    st.chat_message("user").write(user_input)
    if active_image is not None:
        st.image(active_image, caption="Attached Diagnostic Screenshot", width=300)

    active_session["messages"].append({"role": "user", "content": message_content})
    track_usage(context_text)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        with st.spinner("Analyzing environment diagnostics..."):
            try:
                # Switch to Groq's vision model if an image is present, otherwise keep standard model
                active_model = "qwen/qwen3.8-27b" if active_image is not None else "openai/gpt-oss-20b"
                
                completion = client.chat.completions.create(
                    model=active_model,
                    messages=active_session["messages"],
                    stream=False
                )
                output_text = completion.choices[0].message.content
            except Exception as e:
                output_text = f"⚠️ Error communicating with Groq API: {e}"

        track_usage(output_text)
        response_placeholder.write(output_text)
        active_session["messages"].append({"role": "assistant", "content": output_text})
        
        # Clear the image from session state after it's processed so it doesn't attach to future messages
        if "persisted_image" in st.session_state:
            del st.session_state["persisted_image"]
            
        st.rerun()
