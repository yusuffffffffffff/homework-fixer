import streamlit as st
import requests
import json
import uuid
from groq import Groq

# Page configuration - Wide workspace layout
st.set_page_config(
    page_title="EduFix AI | Ultimate CS Studio v4.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Backend URL & Defaults
BACKEND_URL = "http://127.0.0.1:8000/fix-code"
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"

# Initialize Chat History in Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- Custom CSS for Ultra-Premium Cyber-Visuals ----------
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --bg-dark: #020408;
  --glass-bg: rgba(10, 15, 30, 0.75);
  --glass-border: rgba(99, 102, 241, 0.2);
  --primary: #6366f1;
  --accent: #ec4899;
  --cyan: #06b6d4;
  --glow-primary: rgba(99, 102, 241, 0.45);
  --glow-cyan: rgba(6, 182, 212, 0.45);
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
}

/* Global Typography */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    letter-spacing: -0.015em;
}

/* Custom Sleek Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #020408;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(var(--primary), var(--cyan));
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: var(--accent);
}

/* Cyber-Grid Animated Background */
@keyframes cyberGridMove {
    0% { background-position: 0px 0px, 0% 50%; }
    100% { background-position: 40px 40px, 100% 50%; }
}

[data-testid="stAppViewContainer"] {
  background-image: 
    radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
    linear-gradient(-45deg, #02040a, #0b0f19, #130f26, #1e1136, #02040a);
  background-size: 100% 100%, 400% 400%;
  animation: cyberGridMove 20s ease infinite;
  color: var(--text-main);
}

.stApp { background: transparent; }

/* Headings */
h1, h2, h3, h4 { 
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #ffffff !important; 
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
}

/* Glassmorphism Tab Panels */
[data-testid="stTabPanel"] {
  background: var(--glass-bg);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  padding: 28px;
  border-radius: 0px 0px 24px 24px;
  border: 1px solid var(--glass-border);
  border-top: none;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8), inset 0 1px 0 rgba(255, 255, 255, 0.1);
  margin-bottom: 20px;
}

/* Tab Bar Navigation */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: 6px;
  background: rgba(5, 8, 18, 0.85);
  padding: 10px;
  border-radius: 20px 20px 0px 0px;
  border: 1px solid var(--glass-border);
  border-bottom: none;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
  height: 48px;
  border-radius: 12px;
  color: var(--text-muted) !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  border: none !important;
  padding: 0px 28px !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

[data-testid="stTabs"] [aria-selected="true"] {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.4), rgba(6, 182, 212, 0.4)) !important;
  color: #ffffff !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  box-shadow: 0 0 25px var(--glow-primary) !important;
}

/* Header & Status Banner */
.header-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0 25px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  margin-bottom: 30px;
}

.brand-title {
  display: flex;
  align-items: center;
  gap: 18px;
}

.logo-badge {
  background: linear-gradient(135deg, var(--primary), var(--accent));
  width: 64px;
  height: 64px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  box-shadow: 0 0 35px var(--glow-primary);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.status-badge {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #34d399;
  padding: 8px 16px;
  border-radius: 30px;
  font-size: 13px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  backdrop-filter: blur(12px);
  box-shadow: 0 0 20px rgba(52, 211, 153, 0.2);
}

.pulse-dot {
  width: 9px;
  height: 9px;
  background-color: #34d399;
  border-radius: 50%;
  box-shadow: 0 0 12px #34d399;
  animation: pulse 1.8s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.8); }
  70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(52, 211, 153, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
}

/* Floating Glass Chat Bubbles */
[data-testid="stChatMessage"] {
    background: rgba(15, 23, 42, 0.65) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 18px !important;
    padding: 18px !important;
    backdrop-filter: blur(16px) !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
    margin-bottom: 16px !important;
}

/* Hyper-Glowing Action Button */
@keyframes buttonBreath {
    0% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.4), inset 0 0 10px rgba(255, 255, 255, 0.2); }
    50% { box-shadow: 0 0 45px rgba(236, 72, 153, 0.7), inset 0 0 20px rgba(255, 255, 255, 0.4); }
    100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.4), inset 0 0 10px rgba(255, 255, 255, 0.2); }
}

.stButton>button {
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
  color: white !important; 
  border: 1px solid rgba(255, 255, 255, 0.25) !important; 
  padding: 16px 28px !important; 
  font-weight: 800 !important; 
  font-size: 16px !important;
  border-radius: 16px !important;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
  animation: buttonBreath 3.5s infinite alternate !important;
}

.stButton>button:hover {
    transform: translateY(-3px) scale(1.01) !important;
    box-shadow: 0 15px 50px rgba(236, 72, 153, 0.8) !important;
}

/* Deep Form Controls & Code Inputs */
textarea, [data-baseweb="input"], [data-baseweb="select"] { 
    background-color: rgba(2, 4, 10, 0.75) !important; 
    color: var(--text-main) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 0px 0px 14px 14px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 14px !important;
    box-shadow: inset 0 4px 15px rgba(0,0,0,0.6) !important;
}

[data-baseweb="select"] { border-radius: 14px !important; }

textarea:focus {
    border-color: var(--cyan) !important;
    box-shadow: inset 0 4px 15px rgba(0,0,0,0.6), 0 0 20px var(--glow-cyan) !important;
}

/* Chat Input Bar */
[data-testid="stChatInput"] {
    border-radius: 18px !important;
    border: 1.5px solid var(--primary) !important;
    background: rgba(8, 12, 24, 0.95) !important;
    backdrop-filter: blur(15px) !important;
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.5) !important;
}

/* macOS Cyber Terminal Header */
.mac-header {
    background: linear-gradient(180deg, #181b29, #111320);
    padding: 12px 18px;
    border-radius: 14px 14px 0 0;
    border: 1px solid rgba(255,255,255,0.12);
    border-bottom: none;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: -1rem;
    position: relative;
    z-index: 10;
}
.mac-dots { display: flex; align-items: center; gap: 8px; }
.mac-btn { width: 12px; height: 12px; border-radius: 50%; display: inline-block; box-shadow: inset 0 1px 3px rgba(0,0,0,0.4); }
.mac-close { background: #ff5f56; }
.mac-min { background: #ffbd2e; }
.mac-max { background: #27c93f; }
.mac-title { 
    color: #a5b4fc; 
    font-family: 'JetBrains Mono', monospace; 
    font-size: 12.5px;
    font-weight: 600;
}
.mac-status-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #38bdf8;
    background: rgba(56, 189, 248, 0.1);
    padding: 2px 8px;
    border-radius: 6px;
    border: 1px solid rgba(56, 189, 248, 0.3);
}

/* Footer */
.footer { 
  color: #64748b; 
  font-size: 13px; 
  text-align: center; 
  padding: 40px 0 20px 0; 
  font-weight: 600; 
  letter-spacing: 0.05em;
}
"""

st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)

# Connect to Groq API securely for Chat Assistant
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Sample Bug Library
SAMPLE_BUGS = {
    "Select Sample...": ("", ""),
    "🐍 Python: Indentation & Type Error": (
        "def calculate_total(prices):\n    total = 0\n    for p in prices:\n    total += p\n    return total + 'USD'",
        "TypeError: unsupported operand type(s) for +: 'int' and 'str'"
    ),
    "⚛️ React: Hook Dependency Loop": (
        "import { useState, useEffect } from 'react';\n\nfunction Counter() {\n  const [count, setCount] = useState(0);\n  useEffect(() => {\n    setCount(count + 1);\n  });\n  return <div>{count}</div>;\n}",
        "Warning: Maximum update depth exceeded."
    ),
    "🦀 Rust: Borrow Checker Bug": (
        "fn main() {\n    let mut s = String::from(\"hello\");\n    let r1 = &s;\n    let r2 = &s;\n    let r3 = &mut s;\n    println!(\"{}, {}, {}\", r1, r2, r3);\n}",
        "error[E0502]: cannot borrow `s` as mutable because it is also borrowed as immutable"
    ),
    "🗄️ SQL: JOIN Syntax Ambiguity": (
        "SELECT id, name, department_name \nFROM users \nJOIN departments ON users.dept_id = departments.id\nWHERE id = id;",
        "ERROR: column reference \"id\" is ambiguous"
    ),
    "⚡ JS: Scope & Async Error": (
        "async function fetchUserData(userId) {\n  let user = await api.getUser(userId);\n  console.log(user.name);\n}\nconsole.log(user.name);",
        "ReferenceError: user is not defined at line 5"
    ),
    "⚙️ C++: Off-by-One Array Bug": (
        "#include <iostream>\nusing namespace std;\n\nint main() {\n    int arr[5] = {1, 2, 3, 4, 5};\n    for(int i=0; i<=5; i++) {\n        cout << arr[i] << endl;\n    }\n    return 0;\n}",
        "Segmentation fault (core dumped)"
    )
}

# ---------- Top Navigation & Header ----------
st.markdown(
    """
    <div class='header-wrapper'>
        <div class='brand-title'>
            <div class='logo-badge'>⚡</div>
            <div>
                <h1 style='margin:0; font-size:30px;'>EduFix <span style='color: #06b6d4;'>AI</span> <span style='font-size:12px; color:#c7d2fe; font-weight:700; padding: 3px 10px; border: 1px solid rgba(199, 210, 254, 0.4); border-radius: 12px; margin-left: 8px; background: rgba(99, 102, 241, 0.2); box-shadow: 0 0 15px rgba(99, 102, 241, 0.3);'>STUDIO v4.0 PRO</span></h1>
                <div style='color:#94a3b8; font-size:14px; font-weight:500;'>Cybernetic Code Analysis & Autonomous CS Tutor</div>
            </div>
        </div>
        <div class='status-badge'>
            <div class='pulse-dot'></div> FastAPI Backend Connected
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- Widescreen Workspace Columns ----------
left_col, right_col = st.columns([1.1, 1], gap="large")

# ================= LEFT COLUMN: TERMINAL =================
with left_col:
    st.markdown("### 💻 Quantum Code Terminal")
    st.markdown("<div style='color:#94a3b8; font-size:13.5px; margin-bottom:16px;'>Feed your source code and telemetry logs into the neural diagnostic matrix.</div>", unsafe_allow_html=True)

    ctrl_col1, ctrl_col2 = st.columns([1, 1.2])
    with ctrl_col1:
        language = st.selectbox("Language Context", ["Python", "JavaScript / React", "C++", "Java", "Rust", "SQL", "Go"], index=0)
    
    with ctrl_col2:
        sample_choice = st.selectbox("💡 Load Scenario Bug", list(SAMPLE_BUGS.keys()))
        if sample_choice != "Select Sample...":
            sample_code, sample_err = SAMPLE_BUGS[sample_choice]
        else:
            sample_code, sample_err = "", ""

    code_val = sample_code if sample_code else ""
    err_val = sample_err if sample_err else ""

    # Source Terminal Header
    st.markdown(
        f"""
        <div class="mac-header">
            <div class="mac-dots">
                <span class="mac-btn mac-close"></span>
                <span class="mac-btn mac-min"></span>
                <span class="mac-btn mac-max"></span>
                <span class="mac-title">main.source</span>
            </div>
            <div class="mac-status-tag">{language.split()[0].upper()} MODE</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    broken_code_input = st.text_area(
        "Source Code Workspace",
        value=code_val,
        height=240,
        placeholder="Paste your source code here...",
        key="code_input_area",
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Traceback Terminal Header
    st.markdown(
        """
        <div class="mac-header">
            <div class="mac-dots">
                <span class="mac-btn mac-close"></span>
                <span class="mac-btn mac-min"></span>
                <span class="mac-btn mac-max"></span>
                <span class="mac-title">terminal.log</span>
            </div>
            <div class="mac-status-tag" style="color: #f43f5e; background: rgba(244, 63, 94, 0.1); border-color: rgba(244, 63, 94, 0.3);">TELEMETRY</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    error_input = st.text_area(
        "Traceback / Error Output (Optional)",
        value=err_val,
        height=90,
        placeholder="Paste compiler errors or logs here...",
        key="error_input_area",
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # User ID Input for Supabase Integration
    st.markdown(
        """
        <div class="mac-header">
            <div class="mac-dots">
                <span class="mac-btn mac-close"></span>
                <span class="mac-btn mac-min"></span>
                <span class="mac-btn mac-max"></span>
                <span class="mac-title">user_session.config</span>
            </div>
            <div class="mac-status-tag" style="color: #38bdf8; background: rgba(56, 189, 248, 0.1); border-color: rgba(56, 189, 248, 0.3);">SUPABASE USER</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    user_id_input = st.text_input(
        "User UUID (Supabase ID)",
        value=DEFAULT_USER_ID,
        key="user_id_input",
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("⚙️ Neural Hyper-Parameters"):
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            temp = st.slider("Temperature (Creativity)", min_value=0.0, max_value=1.0, value=0.2, step=0.05)
        with p_col2:
            max_tokens = st.slider("Max Token Response Limit", min_value=256, max_value=2048, value=1024, step=64)

    st.markdown("<br>", unsafe_allow_html=True)
    analyze = st.button("🚀 Initialize Neural Diagnostics", use_container_width=True)


# ================= RIGHT COLUMN: DIAGNOSTICS & CHAT =================
with right_col:
    tab_diag, tab_chat = st.tabs(["📊 Diagnostic Hub", "💬 Live AI Assistant"])
    
    # ---------------- TAB 1: DIAGNOSTIC HUB ----------------
    with tab_diag:
        if not analyze:
            st.markdown("### 🧠 Diagnostic Hub Standby")
            st.markdown("<div style='color:#94a3b8; font-size:13.5px; margin-bottom:20px;'>Input code on the left and trigger <b>Initialize Neural Diagnostics</b> to deploy:</div>", unsafe_allow_html=True)

            st.markdown(
                """
                <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.08); padding:20px; border-radius:16px; margin-bottom:14px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);'>
                    <h4 style='margin:0; font-size:15px; color:#c7d2fe; display:flex; align-items:center; gap:10px;'>🎟️ Live Token Deductions</h4>
                    <p style='margin:8px 0 0 0; font-size:13px; color:#94a3b8;'>Verifies and deducts 1 token directly from your Supabase user profile.</p>
                </div>
                <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.08); padding:20px; border-radius:16px; margin-bottom:14px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);'>
                    <h4 style='margin:0; font-size:15px; color:#c7d2fe; display:flex; align-items:center; gap:10px;'>🎯 Root Cause Isolation</h4>
                    <p style='margin:8px 0 0 0; font-size:13px; color:#94a3b8;'>Instantly maps execution bottlenecks and structural logical errors via Groq AI.</p>
                </div>
                <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.08); padding:20px; border-radius:16px; margin-bottom:14px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);'>
                    <h4 style='margin:0; font-size:15px; color:#c7d2fe; display:flex; align-items:center; gap:10px;'>⚡ Refactored Clean Code</h4>
                    <p style='margin:8px 0 0 0; font-size:13px; color:#94a3b8;'>Production-ready code blocks accompanied by 1-click clipboard & export tools.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:
            if not broken_code_input or not broken_code_input.strip():
                st.warning("⚠️ Terminal is empty. Please enter or load code snippets before running diagnostics.")
            else:
                with st.spinner("⚡ Requesting fix from FastAPI backend & deducting token..."):
                    try:
                        # Prepare payload for backend
                        payload = {
                            "user_id": user_id_input.strip(),
                            "code_snippet": broken_code_input
                        }

                        # Call FastAPI Backend
                        response = requests.post(BACKEND_URL, json=payload, timeout=15)

                        if response.status_code == 200:
                            res_data = response.json()
                            response_text = res_data.get("fixed_code", "")
                            tokens_remaining = res_data.get("Tokens_remaining", 0)

                            st.balloons()
                            st.success(f"🎟️ **Token Deducted!** Tokens Remaining: **{tokens_remaining}**")

                            st.markdown("### 📊 Diagnostic Results")
                            st.divider()

                            # Render Response
                            st.markdown(response_text)

                            # Extract Refactored Code Block for Copy/Download buttons
                            fixed_code = None
                            if response_text and "```" in response_text:
                                parts = response_text.split("```")
                                if len(parts) >= 2:
                                    code_block = parts[1]
                                    code_lines = code_block.splitlines()
                                    if code_lines and code_lines[0].strip().isalpha():
                                        fixed_code = "\n".join(code_lines[1:]).strip()
                                    else:
                                        fixed_code = code_block.strip()

                            if fixed_code:
                                st.divider()
                                d_col1, d_col2 = st.columns([1, 1])
                                with d_col1:
                                    st.download_button(
                                        label="📥 Export Fixed Code",
                                        data=fixed_code,
                                        file_name="fixed_code.txt",
                                        mime="text/plain",
                                        use_container_width=True
                                    )
                                with d_col2:
                                    copy_id = "copy-btn-" + uuid.uuid4().hex
                                    copy_html = f"""
                                    <button id='{copy_id}' style='background:linear-gradient(135deg,#6366f1,#06b6d4);color:white;border:1px solid rgba(255,255,255,0.2);border-radius:14px;padding:11px 10px;cursor:pointer;width:100%;font-weight:700;font-family:"Plus Jakarta Sans", sans-serif; box-shadow: 0 4px 20px rgba(6, 182, 212, 0.4); transition: all 0.3s ease;'>📋 Copy Solution</button>
                                    <script>
                                    const btn = document.getElementById('{copy_id}');
                                    if (btn) {{
                                      btn.addEventListener('click', async () => {{
                                        try {{
                                          await navigator.clipboard.writeText({json.dumps(fixed_code)});
                                          btn.innerText = '✅ Copied to Clipboard!';
                                          setTimeout(() => {{ btn.innerText = '📋 Copy Solution'; }}, 2500);
                                        }} catch(e) {{
                                          btn.innerText = '❌ Failed';
                                          setTimeout(() => {{ btn.innerText = '📋 Copy Solution'; }}, 2500);
                                        }}
                                      }});
                                    }}
                                    </script>
                                    """
                                    st.markdown(copy_html, unsafe_allow_html=True)

                        elif response.status_code == 400:
                            st.error("⚠️ Out of tokens! Please top up your token balance in Supabase.")
                        elif response.status_code == 404:
                            st.error(f"❌ User ID (`{user_id_input}`) not found in Supabase `Profiles` table.")
                        else:
                            st.error(f"❌ Backend Error ({response.status_code}): {response.text}")

                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Connection Error: Ensure your FastAPI backend is running locally at `http://127.0.0.1:8000`.")
                    except Exception as e:
                        st.error(f"❌ Neural Processing Error: {e}")

    # ---------------- TAB 2: LIVE AI ASSISTANT ----------------
    with tab_chat:
        st.markdown("### 🤖 Interactive Tutor Chat")
        st.markdown(
            "<div style='color:#94a3b8; font-size:13.5px; margin-bottom:15px;'>"
            "Consult the neural assistant regarding architecture optimization, edge-cases, or theoretical concepts."
            "</div>",
            unsafe_allow_html=True
        )

        chat_container = st.container()

        with chat_container:
            if not st.session_state.messages:
                st.info("👋 Hello! I am your EduFix Neural Assistant. Run diagnostics or ask me any question about your codebase right now!")

            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if prompt := st.chat_input("Ask a follow-up question..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Synthesizing response..."):
                        try:
                            if not groq_client:
                                st.error("🔑 GROQ_API_KEY is missing from Streamlit secrets. Please set it in `.streamlit/secrets.toml` for chat.")
                            else:
                                code_context = broken_code_input.strip() if broken_code_input else "No code loaded."
                                sys_prompt = (
                                    "You are an elite, friendly computer science professor and assistant for EduFix AI Studio. "
                                    f"Language context: {language}.\n\n"
                                    "Current active code in user terminal:\n"
                                    "```\n"
                                    f"{code_context}\n"
                                    "```\n\n"
                                    "Answer clearly, concisely, and provide helpful code examples when appropriate."
                                )

                                api_messages = [{"role": "system", "content": sys_prompt}]
                                for m in st.session_state.messages:
                                    api_messages.append({"role": m["role"], "content": m["content"]})

                                response = groq_client.chat.completions.create(
                                    model="llama-3.1-8b-instant",
                                    messages=api_messages,
                                    temperature=float(temp),
                                    max_tokens=int(max_tokens),
                                )

                                ai_reply = response.choices[0].message.content
                                st.markdown(ai_reply)
                                st.session_state.messages.append({"role": "assistant", "content": ai_reply})

                        except Exception as e:
                            st.error(f"❌ Assistant Error: {e}")
            
            st.rerun()

# --------- Footer ---------
st.markdown("<div class='footer'>CRAFTED WITH 💡 BY AN 18.YEAR.OLD FOUNDER • EDUFIX AI STUDIO V4.0 PRO</div>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center;'><a href='https://discord.gg' target='_blank' style='color: #FF4B4B; text-decoration: none; font-weight: bold;'>💬 Join the Official EduFix Discord Community</a></p>", unsafe_allow_html=True)
