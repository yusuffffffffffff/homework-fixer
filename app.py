import streamlit as st
from groq import Groq
import json
import uuid

# Page configuration - Wide workspace layout
st.set_page_config(
    page_title="EduFix AI | Ultimate CS Studio",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize Chat History in Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- Custom CSS for Visual Enhancements ----------
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --bg-dark: #030408;
  --glass-bg: rgba(15, 20, 35, 0.65);
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

/* Animated Cosmic Background */
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

/* Directly style Streamlit Tab Panels as Glass Cards */
[data-testid="stTabPanel"] {
  background: var(--glass-bg);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  padding: 24px;
  border-radius: 0px 0px 20px 20px;
  border: 1px solid var(--glass-border);
  border-top: none;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6);
  margin-bottom: 20px;
}

/* Tab Bar Navigation */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: 8px;
  background: rgba(10, 14, 26, 0.7);
  padding: 6px;
  border-radius: 16px 16px 0px 0px;
  border: 1px solid var(--glass-border);
  border-bottom: none;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
  height: 44px;
  border-radius: 10px;
  color: var(--text-muted) !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  border: none !important;
  padding: 0px 20px !important;
  transition: all 0.2s ease !important;
}

[data-testid="stTabs"] [aria-selected="true"] {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(6, 182, 212, 0.3)) !important;
  color: #ffffff !important;
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
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
  width: 58px;
  height: 58px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  box-shadow: 0 8px 30px var(--glow);
}

.status-badge {
  background: rgba(16, 185, 129, 0.12);
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
}

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
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 30px var(--glow) !important;
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

/* Chat Input Bar Styling */
[data-testid="stChatInput"] {
    border-radius: 14px !important;
    border: 1px solid var(--primary) !important;
    background: rgba(10, 14, 26, 0.8) !important;
}

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
        "SELECT id, name, department_name \nFROM users \nJOIN departments ON users.dept_id = departments.id\nWHERE id = 5;",
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
            <div class='logo-badge'>🎓</div>
            <div>
                <h1 style='margin:0; font-size:28px;'>EduFix <span style='color: #06b6d4;'>AI</span> <span style='font-size:13px; color:#818cf8; font-weight:600; padding: 2px 8px; border: 1px solid #818cf8; border-radius: 12px; margin-left: 6px;'>Studio v3.0</span></h1>
                <div style='color:#94a3b8; font-size:14px; font-weight:500;'>Next-Gen Code Tutor, Diagnostic Hub & Interactive Assistant</div>
            </div>
        </div>
        <div class='status-badge'>
            <div class='pulse-dot'></div> Groq Llama-3.1 Engine Online
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- Widescreen Workspace Columns ----------
left_col, right_col = st.columns([1.1, 1], gap="large")

# ================= LEFT COLUMN: TERMINAL =================
with left_col:
    st.markdown("### 💻 Source Code Terminal")
    st.markdown("<div style='color:#94a3b8; font-size:13.5px; margin-bottom:16px;'>Paste your code and optional traceback logs to initiate AI diagnosis.</div>", unsafe_allow_html=True)

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

    broken_code_input = st.text_area(
        "Source Code Workspace",
        value=code_val,
        height=300,
        placeholder="Paste your source code here...",
        key="code_input_area"
    )

    error_input = st.text_area(
        "Traceback / Error Output (Optional)",
        value=err_val,
        height=100,
        placeholder="Paste compiler errors or logs here...",
        key="error_input_area"
    )

    with st.expander("⚙️ Advanced AI Parameters"):
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            temp = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.05)
        with p_col2:
            max_tokens = st.slider("Max Token Limit", min_value=256, max_value=2048, value=1024, step=64)

    st.markdown("<br>", unsafe_allow_html=True)
    analyze = st.button("🚀 Run Full System Diagnostics", use_container_width=True)


# ================= RIGHT COLUMN: DIAGNOSTICS & CHAT =================
with right_col:
    tab_diag, tab_chat = st.tabs(["📊 Diagnostic Hub", "💬 Live AI Assistant"])
    
    # ---------------- TAB 1: DIAGNOSTIC HUB ----------------
    with tab_diag:
        if not analyze:
            st.markdown("### 🧠 Waiting for deployment...")
            st.markdown("<div style='color:#94a3b8; font-size:13.5px; margin-bottom:20px;'>Paste your code on the left and hit <b>Run Full System Diagnostics</b> to inspect:</div>", unsafe_allow_html=True)

            st.markdown(
                """
                <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.08); padding:16px; border-radius:12px; margin-bottom:12px;'>
                    <h4 style='margin:0; font-size:15px; color:#c7d2fe;'>🎯 Root Cause Isolation</h4>
                    <p style='margin:4px 0 0 0; font-size:13px; color:#94a3b8;'>Pinpoints exact failing line numbers and logical flaws.</p>
                </div>
                <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.08); padding:16px; border-radius:12px; margin-bottom:12px;'>
                    <h4 style='margin:0; font-size:15px; color:#c7d2fe;'>📚 Conceptual Breakdown</h4>
                    <p style='margin:4px 0 0 0; font-size:13px; color:#94a3b8;'>Explains CS theory clearly without overwhelming jargon.</p>
                </div>
                <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.08); padding:16px; border-radius:12px; margin-bottom:12px;'>
                    <h4 style='margin:0; font-size:15px; color:#c7d2fe;'>⚡ Refactored Clean Code</h4>
                    <p style='margin:4px 0 0 0; font-size:13px; color:#94a3b8;'>Generates clean, execution-ready code snippets with 1-click export.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:
            if not broken_code_input or not broken_code_input.strip():
                st.warning("⚠️ Please paste code in the terminal before running diagnostics.")
            else:
                with st.spinner("🧠 Scanning code architecture & computing fix..."):
                    try:
                        system_instructions = (
                            "You are an elite Computer Science Professor and AI Code Tutor. "
                            f"Language context: {language}.\n"
                            "When analyzing broken code, strictly follow this clear format:\n"
                            "### 🔍 Root Cause Analysis\n"
                            "Pinpoint the line number and core issue in 1-2 clear sentences.\n\n"
                            "### 💡 Conceptual Breakdown\n"
                            "Explain *why* the bug occurred and the concept needed to avoid it in 2-3 friendly sentences.\n\n"
                            "### 🛠️ Refactored Solution\n"
                            "Provide the full fixed code inside a single fenced markdown block.\n\n"
                            "### ⚡ Pro CS Tip\n"
                            "Give one quick best practice tip regarding time complexity, readability, or standards."
                        )

                        completion = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[
                                {"role": "system", "content": system_instructions},
                                {"role": "user", "content": f"Language: {language}\n\nCode:\n{broken_code_input}\n\nError:\n{error_input}"}
                            ],
                            temperature=float(temp),
                            max_tokens=int(max_tokens),
                        )

                        response_text = completion.choices[0].message.content
                        st.balloons()

                        st.markdown("### 📊 Diagnostic Results")
                        st.divider()

                        # Extract Code Block
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

                        if fixed_code:
                            st.divider()
                            d_col1, d_col2 = st.columns([1, 1])
                            with d_col1:
                                st.download_button(
                                    label="📥 Download Fixed Code",
                                    data=fixed_code,
                                    file_name="fixed_code.txt",
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
                                      btn.innerText = '✅ Copied!';
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

                    except Exception as e:
                        st.error(f"❌ API Execution Error: {e}")

    # ---------------- TAB 2: LIVE AI ASSISTANT ----------------
    with tab_chat:
        st.markdown("### 🤖 Interactive Tutor Chat")
        st.markdown(
            "<div style='color:#94a3b8; font-size:13.5px; margin-bottom:15px;'>"
            "Ask follow-up questions about your code, request feature additions, or discuss CS concepts."
            "</div>",
            unsafe_allow_html=True
        )

        # Show initial greeting if no messages
        if not st.session_state.messages:
            st.info("👋 Hello! I'm your EduFix Assistant. Run a diagnostic first, or ask me anything about the code in your terminal right now!")

        # Render message history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Native Chat Input
        if prompt := st.chat_input("Ask a question about your code..."):
            # Render user prompt immediately
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate AI Assistant Response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        code_context = broken_code_input.strip() if broken_code_input else "No code provided."
                        sys_prompt = (
                            "You are an elite, friendly computer science tutor and coding assistant for EduFix AI. "
                            f"The user is working in {language}.\n\n"
                            "Current code in user's terminal:\n"
                            "```\n"
                            f"{code_context}\n"
                            "```\n\n"
                            "Answer the user's question directly, clearly, and concisely."
                        )

                        api_messages = [{"role": "system", "content": sys_prompt}]
                        for m in st.session_state.messages:
                            api_messages.append({"role": m["role"], "content": m["content"]})

                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=api_messages,
                            temperature=0.5,
                            max_tokens=800,
                        )

                        ai_reply = response.choices[0].message.content
                        st.markdown(ai_reply)
                        st.session_state.messages.append({"role": "assistant", "content": ai_reply})

                    except Exception as e:
                        st.error(f"❌ Assistant Error: {e}")

# ---------- Footer ----------
st.markdown("<div class='footer'>Crafted with 💡 by an 18‑year‑old founder • EduFix AI Ultimate Edition</div>", unsafe_allow_html=True)
