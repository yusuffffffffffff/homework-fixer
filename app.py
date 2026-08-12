import streamlit as st
from groq import Groq
import json
import uuid
import time

# Page configuration - Wide workspace layout
st.set_page_config(
    page_title="EduFix AI | Ultimate CS Studio",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize Chat History in Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- Custom CSS for Stunning Visual Enhancements ----------
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --bg-dark: #02040a;
  --glass-bg: rgba(15, 20, 35, 0.45);
  --glass-border: rgba(255, 255, 255, 0.08);
  --primary: #6366f1;
  --accent: #ec4899;
  --cyan: #06b6d4;
  --glow: rgba(99, 102, 241, 0.35);
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
}

/* Global Typography */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    letter-spacing: -0.015em;
}

/* Animated Cosmic Gradient Background */
@keyframes gradientMove {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

[data-testid="stAppViewContainer"] {
  background: linear-gradient(-45deg, #02040a, #0f172a, #1e1b4b, #2e1065, #02040a);
  background-size: 400% 400%;
  animation: gradientMove 20s ease infinite;
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

/* Glassmorphism Containers with floating effect */
.studio-card {
  background: var(--glass-bg);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  padding: 24px;
  border-radius: 20px;
  border: 1px solid var(--glass-border);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6);
  margin-bottom: 20px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.studio-card:hover {
  box-shadow: 0 15px 50px rgba(99, 102, 241, 0.15);
}

/* Header & Status Banner */
.header-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0 25px 0;
  border-bottom: 1px solid var(--glass-border);
  margin-bottom: 25px;
}

.brand-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-badge {
  background: linear-gradient(135deg, var(--primary), var(--cyan));
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
  box-shadow: 0 8px 30px var(--glow);
  animation: pulseLogo 3s infinite alternate;
}

@keyframes pulseLogo {
  0% { box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3); }
  100% { box-shadow: 0 8px 45px rgba(6, 182, 212, 0.5); }
}

.status-badge {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #34d399;
  padding: 6px 14px;
  border-radius: 30px;
  font-size: 13px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background-color: #34d399;
  border-radius: 50%;
  box-shadow: 0 0 10px #34d399;
  animation: blink 1.5s infinite;
}

@keyframes blink { 0% {opacity: 1;} 50% {opacity: 0.4;} 100% {opacity: 1;} }

/* Styled Action Button */
.stButton>button {
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
  color: white !important; 
  border: none !important; 
  padding: 14px 28px !important; 
  font-weight: 700 !important; 
  font-size: 16px !important;
  border-radius: 14px !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  box-shadow: 0 6px 20px var(--glow) !important;
}

.stButton>button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 35px var(--glow) !important;
}

/* Chat Input Styling */
[data-testid="stChatInput"] {
    background: rgba(15, 20, 35, 0.8) !important;
    border: 1px solid var(--primary) !important;
    border-radius: 16px !important;
}

/* Chat Message Bubbles */
[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 15px;
    backdrop-filter: blur(10px);
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: rgba(99, 102, 241, 0.08);
    border: 1px solid rgba(99, 102, 241, 0.2);
}

/* Form Controls & Code Inputs */
textarea, [data-baseweb="input"], [data-baseweb="select"] { 
    background-color: rgba(5, 8, 18, 0.7) !important; 
    color: var(--text-main) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13.5px !important;
}

textarea:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.3) !important;
}

/* Custom Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99, 102, 241, 0.5); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* Footer */
.footer { 
  color: #64748b; 
  font-size: 13px; 
  text-align: center; 
  padding: 40px 0 20px 0; 
  font-weight: 600; 
}
"""

st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)

# Connect to Groq API securely
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("🔑 GROQ_API_KEY is missing from Streamlit secrets. Please add it and restart the app.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# Extensively Expanded Sample Bug Library
SAMPLE_BUGS = {
    "Select Sample...": ("", ""),
    "🐍 Python: Indentation & Type Error": (
        "def calculate_total(prices):\n    total = 0\n    for p in prices:\n    total += p\n    return total + 'USD'",
        "TypeError: unsupported operand type(s) for +: 'int' and 'str'"
    ),
    "⚛️ React: Hook Dependency Loop": (
        "import { useState, useEffect } from 'react';\n\nfunction Counter() {\n  const [count, setCount] = useState(0);\n  useEffect(() => {\n    setCount(count + 1);\n  });\n  return <div>{count}</div>;\n}",
        "Warning: Maximum update depth exceeded. This can happen when a component calls setState inside useEffect."
    ),
    "🦀 Rust: Borrow Checker Bug": (
        "fn main() {\n    let mut s = String::from(\"hello\");\n    let r1 = &s;\n    let r2 = &s;\n    let r3 = &mut s;\n    println!(\"{}, {}, {}\", r1, r2, r3);\n}",
        "error[E0502]: cannot borrow `s` as mutable because it is also borrowed as immutable"
    ),
    "🗄️ SQL: JOIN Syntax Ambiguity": (
        "SELECT id, name, department_name \nFROM users \nJOIN departments ON users.dept_id = departments.id\nWHERE id = 5;",
        "ERROR: column reference \"id\" is ambiguous"
    ),
    "⚡ JS: Scope & Async Error": (
        "async function fetchUserData(userId) {\n  let user = await api.getUser(userId);\n  console.log(user.name);\n}\nconsole.log(user.name);",
        "ReferenceError: user is not defined at line 5"
    ),
    "⚙️ C++: Off-by-One Array Bug": (
        "#include <iostream>\nusing namespace std;\n\nint main() {\n    int arr[5] = {1, 2, 3, 4, 5};\n    for(int i=0; i<=5; i++) {\n        cout << arr[i] << endl;\n    }\n    return 0;\n}",
        "Segmentation fault (core dumped) / Garbage output"
    )
}

# ---------- Top Navigation & Header ----------
st.markdown(
    """
    <div class='header-wrapper'>
        <div class='brand-title'>
            <div class='logo-badge'>✨</div>
            <div>
                <h1 style='margin:0; font-size:28px;'>EduFix <span style='color: #06b6d4;'>AI</span> <span style='font-size:14px; color:#818cf8; font-weight:600; padding-left:8px; border: 1px solid #818cf8; border-radius: 12px; padding: 2px 8px; margin-left: 6px;'>Ultimate</span></h1>
                <div style='color:#94a3b8; font-size:14.5px; font-weight:500;'>Next-Gen Code Tutor, Diagnostic Hub & Interactive Assistant</div>
            </div>
        </div>
        <div class='status-badge'>
            <div class='pulse-dot'></div> System Core Online
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- Widescreen Workspace Columns ----------
left_col, right_col = st.columns([1.2, 1], gap="large")

with left_col:
    st.markdown("<div class='studio-card'>", unsafe_allow_html=True)
    st.markdown("### 💻 Source Code Terminal")
    st.markdown("<div style='color:#94a3b8; font-size:13.5px; margin-bottom:16px;'>Paste code, select a language, or load a scenario to begin analysis.</div>", unsafe_allow_html=True)

    # Top Toolbar controls
    ctrl_col1, ctrl_col2 = st.columns([1, 1.2])
    with ctrl_col1:
        language = st.selectbox("Context Language", ["Python", "JavaScript / React", "C++", "Java", "Rust", "SQL", "Go"], index=0)
    
    with ctrl_col2:
        sample_choice = st.selectbox("💡 Load Scenario (Try it out)", list(SAMPLE_BUGS.keys()))
        if sample_choice != "Select Sample...":
            sample_code, sample_err = SAMPLE_BUGS[sample_choice]
        else:
            sample_code, sample_err = "", ""

    # Inputs
    code_val = sample_code if sample_code else ""
    err_val = sample_err if sample_err else ""

    broken_code_input = st.text_area(
        "Source Code Workspace",
        value=code_val,
        height=320,
        placeholder="Paste your source code here...",
        key="code_input_area"
    )

    error_input = st.text_area(
        "Traceback Log (Optional)",
        value=err_val,
        height=100,
        placeholder="Paste compiler errors or logs here...",
        key="error_input_area"
    )

    # Advanced Model Settings
    with st.expander("⚙️ Advanced AI Parameters"):
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            temp = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.05, help="Lower = strict, Higher = creative.")
        with p_col2:
            max_tokens = st.slider("Max Token Limit", min_value=256, max_value=2048, value=1024, step=64)

    st.markdown("<br>", unsafe_allow_html=True)
    analyze = st.button("🚀 Run Full System Diagnostics", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


with right_col:
    tab_diag, tab_chat = st.tabs(["📊 Diagnostic Hub", "💬 Live AI Assistant"])
    
    # ---------------- TAB 1: DIAGNOSTIC HUB ----------------
    with tab_diag:
        if not analyze:
            # Default Workspace State (Feature Dashboard)
            st.markdown("<div class='studio-card'>", unsafe_allow_html=True)
            st.markdown("### 🧠 Waiting for deployment...")
            st.markdown("<div style='color:#94a3b8; font-size:13.5px; margin-bottom:20px;'>Features active on diagnostic run:</div>", unsafe_allow_html=True)

            st.markdown(
                """
                <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); padding:16px; border-radius:12px; margin-bottom:12px;'>
                    <h4 style='margin:0; font-size:15px; color:#c7d2fe;'>🎯 Root Cause Isolation</h4>
                    <p style='margin:4px 0 0 0; font-size:13px; color:#94a3b8;'>Pinpoints exact failing lines automatically.</p>
                </div>
                <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); padding:16px; border-radius:12px; margin-bottom:12px;'>
                    <h4 style='margin:0; font-size:15px; color:#c7d2fe;'>📚 Pedagogical Learning</h4>
                    <p style='margin:4px 0 0 0; font-size:13px; color:#94a3b8;'>Explains the CS theory behind the fix.</p>
                </div>
                <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); padding:16px; border-radius:12px; margin-bottom:12px;'>
                    <h4 style='margin:0; font-size:15px; color:#c7d2fe;'>⚡ Instant Code Export</h4>
                    <p style='margin:4px 0 0 0; font-size:13px; color:#94a3b8;'>Generates clean code ready for your IDE.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("</div>", unsafe_allow_html=True)

        else:
            # Analysis Run State
            if not broken_code_input or not broken_code_input.strip():
                st.warning("⚠️ Please provide code in the terminal to run diagnostics.")
            else:
                with st.spinner("🧠 Compiling diagnostics & scanning structural integrity..."):
                    try:
                        system_instructions = (
                            "You are an elite Computer Science Professor and AI Code Tutor. "
                            f"Language context: {language}.\n"
                            "When analyzing broken code, strictly follow this format:\n"
                            "### 🔍 Root Cause Analysis\n"
                            "Pinpoint the line number and core issue in 1-2 clear sentences.\n\n"
                            "### 💡 Conceptual Breakdown\n"
                            "Explain *why* the bug occurred and the concept needed to avoid it in 2-3 friendly sentences.\n\n"
                            "### 🛠️ Refactored Solution\n"
                            "Provide the full fixed code inside a single fenced markdown block.\n\n"
                            "### ⚡ Pro CS Tip\n"
                            "Give one quick best practice tip regarding time complexity, readability, or language standards."
                        )

                        completion = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[
                                {"role": "system", "content": system_instructions},
                                {"role": "user", "content": f"Language: {language}\n\nCode:\n{broken_code_input}\n\nError / Traceback:\n{error_input}"}
                            ],
                            temperature=float(temp),
                            max_tokens=int(max_tokens),
                        )

                        response_text = completion.choices[0].message.content
                        st.balloons()

                        st.markdown("<div class='studio-card'>", unsafe_allow_html=True)
                        st.markdown("### 📊 Diagnostic Results")
                        st.divider()

                        # Extract Code Block if Present
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

                        st.markdown(response_text)

                        # Export Controls if Code Exists
                        if fixed_code:
                            st.divider()
                            d_col1, d_col2 = st.columns([1, 1])
                            with d_col1:
                                st.download_button(
                                    label="📥 Download Fixed Script",
                                    data=fixed_code,
                                    file_name="fixed_code_edufix.txt", # text by default to handle all languages safely
                                    mime="text/plain",
                                    use_container_width=True
                                )
                            with d_col2:
                                copy_id = "copy-btn-" + uuid.uuid4().hex
                                copy_html = f"""
                                <button id='{copy_id}' style='background:linear-gradient(135deg,#6366f1,#06b6d4);color:white;border:none;border-radius:12px;padding:10px 10px;cursor:pointer;width:100%;font-weight:700;font-family:"Plus Jakarta Sans", sans-serif;'>📋 Copy Solution</button>
                                <script>
                                const btn = document.getElementById('{copy_id}');
                                if (btn) {{
                                  btn.addEventListener('click', async () => {{
                                    try {{
                                      await navigator.clipboard.writeText({json.dumps(fixed_code)});
                                      btn.innerText = '✅ Copied to Clipboard!';
                                      setTimeout(() => {{ btn.innerText = '📋 Copy Solution'; }}, 2500);
                                    }} catch(e) {{
                                      btn.innerText = '❌ Copy Failed';
                                      setTimeout(() => {{ btn.innerText = '📋 Copy Solution'; }}, 2500);
                                    }}
                                  }});
                                }}
                                </script>
                                """
                                st.markdown(copy_html, unsafe_allow_html=True)

                        st.markdown("</div>", unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"❌ API Execution Error: {e}")

    # ---------------- TAB 2: LIVE AI ASSISTANT ----------------
    with tab_chat:
        st.markdown("<div class='studio-card' style='height: 600px; display: flex; flex-direction: column; overflow: hidden;'>", unsafe_allow_html=True)
        st.markdown("### 🤖 Interactive Tutor Chat", unsafe_allow_html=True)
        st.markdown("<p style='color:#94a3b8; font-size:13px;'>Ask follow-up questions about the code, theory, or request new features.</p>", unsafe_allow_html=True)
        st.divider()

        # Chat Message Container
        chat_container = st.container(height=380, border=False)
        
        with chat_container:
            if not st.session_state.messages:
                st.info("👋 Hello! I'm your EduFix Assistant. Run a diagnostic first, or ask me anything about the code in your terminal right now!")

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        st.markdown("</div>", unsafe_allow_html=True)

        # Chat Input Bar (Placed outside container so it anchors to the bottom)
        if prompt := st.chat_input("Ask a question about the code..."):
            # Append user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

            # Generate AI response incorporating the current terminal code
            with chat_container:
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    
                    # Contextual awareness prompt
                    context_prompt = (
                        "You are an elite, friendly coding assistant for EduFix AI. "
                        "The user is currently working on this code in their terminal:\n\n"
                        f"```{language}\n"
                        f"{broken_code_input}\n"
                        "```\n\n"
                        "Answer their following question directly, concisely, and helpfully."
                    )
