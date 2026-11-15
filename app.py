#  Hello! Thanks for checking out my program!  #

import streamlit as st
from groq import Groq
import time
import base64
import sqlite3
import json

# Initialize SQLite Database for Persistent Storage
def init_db():
    conn = sqlite3.connect("cyberpatriot_coach.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            data TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Load/Save Helpers
def load_session_from_db(session_id):
    conn = sqlite3.connect("cyberpatriot_coach.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None

def save_session_to_db(session_id, session_data):
    conn = sqlite3.connect("cyberpatriot_coach.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO sessions (session_id, data) VALUES (?, ?)
    """, (session_id, json.dumps(session_data)))
    conn.commit()
    conn.close()

# 1. Page Configuration & Layout
st.set_page_config(page_title="CyberPatriot AI Coach", page_icon="🛡️", layout="wide")

# 🌙 Theme Toggle & Custom CSS Styling
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎨 Theme & Appearance")
is_dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=True, key="dark_mode_toggle_switch")

# Define dynamic color variables based on the toggle switch
if is_dark_mode:
    bg_color = "#0e1117"
    text_color = "#fafafa"
    card_bg = "#1e1e2f"
    border_color = "#3f3f5f"
else:
    bg_color = "#ffffff"
    text_color = "#31333F"
    card_bg = "#f8f9fa"
    border_color = "#d1d5db"

# Inject Custom Dynamic CSS
st.markdown(f"""
<style>
    /* Main App Background & Text */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    
    /* Custom Dashboard Card Container */
    .cyber-card {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 12px;
    }}
    
    /* Metric Card Polish */
    [data-testid="stMetric"] {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        padding: 10px 15px;
        border-radius: 8px;
    }}
</style>
""", unsafe_allow_html=True)

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
Generate exactly 3 multiple choice questions (with options A, B, C, D) and 1 free response question based on the selected operating system scope.
Make sure the questions are clearly numbered (Question 1, Question 2, Question 3, Question 4).
"""

# 4. Initialize session state tracking variables & helpers
def track_usage(text_input):
    words = len(str(text_input).split())
    st.session_state.total_words_processed += words

if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = "Session 1"
if "session_counter" not in st.session_state:
    st.session_state.session_counter = 1
if "total_words_processed" not in st.session_state:
    st.session_state.total_words_processed = 0

# Initialize active session (checks SQLite DB first, otherwise creates a fresh one)
if st.session_state.current_session_id not in st.session_state.sessions:
    saved_data = load_session_from_db(st.session_state.current_session_id)
    if saved_data:
        st.session_state.sessions[st.session_state.current_session_id] = saved_data
    else:
        st.session_state.sessions[st.session_state.current_session_id] = {
            "messages": [{"role": "system", "content": GENERAL_SYSTEM_PROMPT}],
            "logs": [],
            "last_score": None,
            "quiz_difficulty": "Intermediate"
        }

# Fetch pointers for active session
active_session = st.session_state.sessions[st.session_state.current_session_id]


# 5. SIDEBAR: Dashboard Configuration & Navigation
st.sidebar.title("🛡️ CP-OPS Dashboard")
st.sidebar.markdown("---")

# Target Platform Selection
system_choice = st.sidebar.selectbox(
    "Choose target environment:",
    ["General / Mixed", "Windows Server / Desktop", "Linux (Ubuntu/Debian)", "Cisco Packet Tracer"],
    index=0,
    key="target_env_selectbox"
)

st.sidebar.markdown("---")

# EXPANDER 1: Study & Training Tools
with st.sidebar.expander("🛠️ Study & Training Tools", expanded=True):
    if st.button("📋 Generate Security Checklist", key="sidebar_btn_gen_checklist", use_container_width=True):
        checklist_prompt = (
            f"Generate a focused, high-priority CyberPatriot hardening checklist for {system_choice}. "
            "Group items under 3-4 short category headers formatted as '### Category Name'. "
            "Format every actionable task strictly starting with '- [ ] ' followed by a concise command or setting (under 15 words). "
            "Do not include introductory or concluding paragraphs."
        )
        active_session["logs"].append(f"📋 Generated {system_choice} Checklist")
        track_usage(checklist_prompt)
        
        with st.spinner(f"Compiling {system_choice} hardening checklist..."):
            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": "You are an automated CyberPatriot scoring engine. Output only categorized markdown checklists."},
                    {"role": "user", "content": checklist_prompt}
                ],
                stream=False
            )
            output_text = completion.choices[0].message.content
            track_usage(output_text)
            
            structured_checklist = {}
            current_category = "General Hardening"
            
            for line in output_text.split("\n"):
                clean_line = line.strip()
                if clean_line.startswith("### "):
                    current_category = clean_line.replace("### ", "").strip()
                    if current_category not in structured_checklist:
                        structured_checklist[current_category] = {}
                elif clean_line.startswith("- [ ]") or clean_line.startswith("- [x]"):
                    task_text = clean_line.replace("- [ ]", "").replace("- [x]", "").strip()
                    if task_text:
                        if current_category not in structured_checklist:
                            structured_checklist[current_category] = {}
                        structured_checklist[current_category][task_text] = False
            
            active_session["checklist"] = structured_checklist
            active_session["checklist_platform"] = system_choice
        st.rerun()

    if st.button("🚀 Generate Quick Quiz", key="sidebar_btn_gen_quiz", use_container_width=True):
        current_diff = active_session.get("quiz_difficulty", "Intermediate")
        last_score = active_session.get("last_score")
        
        if last_score is not None:
            if last_score == 4:
                current_diff = "Advanced / Hardened Expert"
            elif last_score <= 2:
                current_diff = "Beginner / Foundational"
            else:
                current_diff = "Intermediate"
        
        active_session["quiz_difficulty"] = current_diff
        quiz_prompt = (
            f"Generate a short quiz tracking core security metrics on {system_choice} "
            f"at a **{current_diff}** difficulty level. "
            "Generate exactly 3 multiple choice questions (with options A, B, C, D) "
            "and 1 free response question. Number them clearly (Question 1 to 4)."
        )
        quiz_payload = [
            {"role": "system", "content": QUIZ_SYSTEM_PROMPT}, 
            {"role": "user", "content": quiz_prompt}
        ]
        active_session["logs"].append(f"📝 Generated {current_diff} Quiz")
        track_usage(quiz_prompt)
        
        with st.spinner(f"Generating {current_diff} quiz..."):
            time.sleep(0.5)
            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=quiz_payload,
                stream=False
            )
            output_text = completion.choices[0].message.content
            track_usage(output_text)
            
            active_session["messages"].append({"role": "assistant", "content": output_text})
            active_session["quiz_active"] = True
        st.rerun()

    if st.button("🔓 Reveal Quiz Answers", key="sidebar_btn_reveal_answers", use_container_width=True):
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

    if st.button("🕵️ Forensics Question Helper", key="sidebar_btn_forensics_helper", use_container_width=True):
        forensics_prompt = (
            f"I need help solving a CyberPatriot Forensics Question on {system_choice}. "
            "Ask me to paste the exact forensics question text from my Desktop. "
            "Once I paste it, guide me step-by-step on where to look (specific log paths, registry hives, "
            "file metadata, or decoding commands) without giving away a fake answer."
        )
        active_session["messages"].append({"role": "user", "content": forensics_prompt})
        active_session["logs"].append("🕵️ Activated Forensics Helper")
        track_usage(forensics_prompt)
        
        with st.spinner("Initializing Forensics Investigation Mode..."):
            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=active_session["messages"],
                stream=False
            )
            output_text = completion.choices[0].message.content
            track_usage(output_text)
            active_session["messages"].append({"role": "assistant", "content": output_text})
            save_session_to_db(st.session_state.current_session_id, active_session)
        st.rerun()

# EXPANDER 2: Quick-Copy Command Toolbox
with st.sidebar.expander("⚡ Quick-Copy Toolbox", expanded=False):
    os_tool_tab = st.selectbox(
        "Select OS Commands:", 
        ["Windows PowerShell", "Linux (Ubuntu/Debian)", "Cisco IOS"],
        key="quick_copy_os_selectbox"
    )

    if os_tool_tab == "Windows PowerShell":
        st.code("""# Audit accounts & passwords
Get-LocalUser
Get-CimInstance Win32_UserAccount

# Disable guest account
Disable-LocalUser -Name "Guest"

# Enforce password complexity via SecPol
secedit /export /cfg C:\\secpol.cfg""", language="powershell")

    elif os_tool_tab == "Linux (Ubuntu/Debian)":
        st.code("""# 1. Audit Users & Sudoers
cut -d: -f1,3 /etc/passwd | grep -E ':[0-9]{4}$'
getent group sudo

# 2. Firewall & Network Hardening
sudo ufw enable
sudo ufw default deny incoming
sudo ss -tulpn

# 3. SSH & Kernel Security
sudo sed -i 's/#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh
sudo sysctl -w net.ipv4.tcp_syncookies=1

# 4. Password Policy & Updates
sudo apt update && sudo apt upgrade -y
sudo nano /etc/login.defs  # PASS_MAX_DAYS 90

# 5. Hunt Prohibited Media
sudo find /home -type f \\( -name "*.mp3" -o -name "*.mp4" \\)""", language="bash")

    elif os_tool_tab == "Cisco IOS":
        st.code("""# Enable config mode & set password encryption
en
conf t
service password-encryption

# Secure console & vty lines
line con 0
password SECURE_PASS
login
exit""", language="text")

# EXPANDER 3: Session Management & Export
with st.sidebar.expander("💬 Session & Data Export", expanded=False):
    if st.button("➕ Start New Chat Session", key="sidebar_btn_new_session", use_container_width=True):
        st.session_state.session_counter += 1
        new_id = f"Session {st.session_state.session_counter}"
        st.session_state.sessions[new_id] = {
            "messages": [{"role": "system", "content": GENERAL_SYSTEM_PROMPT}],
            "logs": [],
            "last_score": None,
            "quiz_difficulty": "Intermediate"
        }
        st.session_state.current_session_id = new_id
        st.rerun()

    if st.button("🗑️ Clear Current Logs", key="sidebar_btn_clear_logs", use_container_width=True):
        st.session_state.sessions[st.session_state.current_session_id] = {
            "messages": [{"role": "system", "content": GENERAL_SYSTEM_PROMPT}],
            "logs": [],
            "last_score": None,
            "quiz_difficulty": "Intermediate"
        }
        st.rerun()

    full_transcript = ""
    for msg in active_session["messages"]:
        if msg["role"] != "system" and msg["content"] != "Give me a brand new, random CyberPatriot practice quiz challenge right now!":
            speaker = "STUDENT" if msg["role"] == "user" else "MENTOR"
            full_transcript += f"[{speaker}]:\n{msg['content']}\n\n{'='*40}\n\n"

    if full_transcript:
        st.download_button(
            label="📥 Download Study Notes (.txt)",
            data=full_transcript,
            file_name=f"cyberpatriot_study_notes_{st.session_state.current_session_id.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
            key="sidebar_download_notes_btn"
        )
    else:
        st.caption("Chat with the mentor or generate a checklist to unlock download export options.")

st.sidebar.markdown("#### 🕒 Session History")
for sid in list(st.session_state.sessions.keys()):
    button_label = f"📁 {sid} (Active)" if sid == st.session_state.current_session_id else f"📄 {sid}"
    if st.sidebar.button(button_label, key=f"nav_session_{sid}", use_container_width=True):
        st.session_state.current_session_id = sid
        if "persisted_image" in st.session_state:
            del st.session_state["persisted_image"]
        st.rerun()

# LIVE ANALYTICS MONITOR (Bottom of Sidebar)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Live Analytics Monitor")
st.sidebar.metric(label="Data Volume Processed", value=f"{st.session_state.total_words_processed} words")
estimated_tokens = int(st.session_state.total_words_processed * 1.3)
st.sidebar.metric(label="Estimated API Tokens", value=f"{estimated_tokens:,} tokens")
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

# INTERACTIVE QUIZ SUBMISSION DASHBOARD
if active_session.get("quiz_active", False):
    st.markdown("---")
    st.markdown("### 📝 Active Quiz Assessment Engine")
    st.info("Review the quiz questions below in the chat feed, then submit your answers below to get your score and detailed corrections!")
    
    with st.form("quiz_submission_form"):
        col1, col2 = st.columns(2)
        with col1:
            q1_ans = st.selectbox("Question 1 Answer:", ["Select...", "A", "B", "C", "D"])
            q2_ans = st.selectbox("Question 2 Answer:", ["Select...", "A", "B", "C", "D"])
        with col2:
            q3_ans = st.selectbox("Question 3 Answer:", ["Select...", "A", "B", "C", "D"])
            q4_ans = st.text_input("Question 4 (Free Response Answer):", placeholder="Type your short answer here...")
            
        submitted_quiz = st.form_submit_button("🎓 Submit Answers for Grading", use_container_width=True)
        
        if submitted_quiz:
            if q1_ans == "Select..." or q2_ans == "Select..." or q3_ans == "Select..." or not q4_ans.strip():
                st.warning("Please answer all 4 questions before submitting!")
            else:
                grading_prompt = f"""
                The student has submitted their answers for the quiz:
                - Question 1: {q1_ans}
                - Question 2: {q2_ans}
                - Question 3: {q3_ans}
                - Question 4 (Free Response): {q4_ans}

                Please grade these answers against the quiz you generated. 
                You MUST start your response with a clear score line formatted exactly like this: `SCORE: X/4` (where X is the number of correct answers, 0 to 4).
                Follow the score with detailed explanations and corrections for each question.
                """
                
                active_session["messages"].append({"role": "user", "content": grading_prompt})
                
                with st.spinner("Grading your submission..."):
                    completion = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=active_session["messages"],
                        stream=False
                    )
                    grading_result = completion.choices[0].message.content
                    active_session["messages"].append({"role": "assistant", "content": grading_result})
                    
                    # Attempt to extract score for badge display
                    import re
                    score_match = re.search(r"SCORE:\s*(\d+)/4", grading_result, re.IGNORECASE)
                    if score_match:
                        earned_score = int(score_match.group(1))
                        active_session["last_score"] = earned_score
                    else:
                        active_session["last_score"] = None
                        
                    active_session["quiz_active"] = False # Reset quiz active state
                st.rerun()

# Display Last Score Badge if available
if "last_score" in active_session and active_session["last_score"] is not None:
    score = active_session["last_score"]
    st.markdown("---")
    col_a, col_b = st.columns([1, 3])
    with col_a:
        st.metric(label="Latest Quiz Score", value=f"{score}/4", delta=f"{int((score/4)*100)}%")
    with col_b:
        if score == 4:
        #   st.success("🏆 Flawless victory! Perfect score on this challenge.") # handled below
            pass
        elif score >= 3:
            st.success("Great job! You have a solid grasp of these concepts.")
        else:
            st.warning("Keep practicing! Review the feedback breakdown above to strengthen your hardening skills.")

# INTERACTIVE CHECKLIST TRACKER WIDGET
if "checklist" in active_session and active_session["checklist"]:
    platform_label = active_session.get("checklist_platform", system_choice)
    
    header_col1, header_col2 = st.columns([4, 1])
    with header_col1:
        st.markdown(f"### 🎯 Live Hardening Checklist ({platform_label})")
    with header_col2:
        if st.button("🗑️ Clear Checklist", use_container_width=True):
            del active_session["checklist"]
            st.rerun()

    st.caption("Check off items as you complete them in your VM lab.")
    
    checklist_data = active_session["checklist"]
    total_tasks = 0
    completed_count = 0
    
    for cat_idx, (category, tasks) in enumerate(checklist_data.items()):
        if tasks:
            st.markdown(f"**{category}**")
            for task_idx, (task, is_checked) in enumerate(tasks.items()):
                total_tasks += 1
                unique_key = f"chk_{st.session_state.current_session_id}_{cat_idx}_{task_idx}"
                status = st.checkbox(task, value=is_checked, key=unique_key)
                active_session["checklist"][category][task] = status
                if status:
                    completed_count += 1

    progress_percentage = completed_count / total_tasks if total_tasks > 0 else 0
    st.progress(
        progress_percentage,
        text=f"Hardening Progress: {completed_count}/{total_tasks} Tasks Completed ({int(progress_percentage * 100)}%)"
    )
    
    if completed_count == total_tasks and total_tasks > 0:
        st.balloons()
        st.success("🎉 All hardening tasks for this checklist are complete!")
    
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

# Quick Prompt Start Buttons
if len(active_session["messages"]) <= 1:
    st.markdown("#### 💡 Quick Prompt Starters")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 Explain Account Lockout Policies", use_container_width=True):
            st.session_state["shortcut_input"] = "Explain how to audit and configure Account Lockout Policies to prevent brute-force attacks."
    with col2:
        if st.button("🚫 Show Common Forbidden Software", use_container_width=True):
            st.session_state["shortcut_input"] = "List the most common forbidden software and media file extensions that cause penalties in competition images."

# README SCENARIO CONTEXT PARSER
with st.expander("📄 Paste Competition README (Prevents Accidental Point Penalties)", expanded=False):
    readme_text = st.text_area(
        "Paste Authorized Users, Admins, and Critical Services from the VM README:",
        value=active_session.get("readme_context", ""),
        height=120,
        placeholder="e.g., Authorized Admins: jdoe, msmith | Critical Services: SSH, Apache2 | Do NOT remove..."
    )
    if st.button("🔒 Lock README Rules into Session", key="lock_readme_btn"):
        active_session["readme_context"] = readme_text
        # Update the system prompt so the AI respects the README rules on every reply
        active_session["messages"][0]["content"] = (
            GENERAL_SYSTEM_PROMPT + 
            f"\n\nCRITICAL COMPETITION README RULES (NEVER VIOLATE THESE):\n{readme_text}"
        )
        save_session_to_db(st.session_state.current_session_id, active_session)
        st.success("✅ README rules locked! The AI will now protect your authorized users and critical services.")

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
