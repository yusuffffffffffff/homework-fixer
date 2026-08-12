import streamlit as st
from groq import Groq
import json
import uuid

# Page configuration - Wide workspace layout
st.set_page_config(
    page_title="EduFix AI | Next-Gen CS Code Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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
  --glow: rgba(99, 102, 241, 0.25);
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
}

/* Global Typography */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    letter-spacing: -0.015em;
}

/* Cosmic Gradient Background with Subtle Grid */
[data-testid="stAppViewContainer"] {
  background: 
    radial-gradient(circle at 85% 15%, rgba(99, 102, 241, 0.12) 0%, transparent 40%),
    radial-gradient(circle at 15% 85%, rgba(236, 72, 153, 0.1) 0%, transparent 40%),
    var(--bg-dark);
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

/* Glassmorphism Containers */
.studio-card {
  background: var(--glass-bg);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  padding: 24px;
  border-radius: 20px;
  border: 1px solid var(--glass-border);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
  margin-bottom: 20px;
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
  background: linear-gradient(135deg, var(--primary), var(--accent));
  width: 58px;
  height: 58px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  box-shadow: 0 8px 25px var(--glow);
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
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px var(--glow) !important;
}

/* Feature Showcase Cards (Idle Right Column) */
.feature-box {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  padding: 18px;
  margin-bottom: 14px;
  transition: border 0.3s ease;
}

.feature-box:hover {
  border-color: rgba(99, 102, 241, 0.4);
}

.feature-title {
  color: #c7d2fe;
  font-weight: 700;
  font-size: 15px;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.feature-desc {
  color: var(--text-muted);
  font-size: 13px;
  line-height: 1.5;
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

# Sample code snippets for 1-click testing
SAMPLE_BUGS = {
    "Select Sample...": ("", ""),
    "🐍 Python: Indentation & Type Error": (
        "def calculate_total(prices):\n    total = 0\n    for p in prices:\n    total += p\n    return total + 'USD'",
        "TypeError: unsupported operand type(s) for +: 'int' and 'str'"
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
            <div class='logo-badge'>🎓</div>
            <div>
                <h1 style='margin:0; font-size:26px;'>EduFix AI <span style='font-size:14px; color:#818cf8; font-weight:600; padding-left:8px;'>Studio v2.5</span></h1>
                <div style='color:#94a3b8; font-size:14px; font-weight:500;'>Intelligent Code Tutor & Automated Debugging Assistant</div>
            </div>
        </div>
        <div class='status-badge'>
            <div class='pulse-dot'></div> Groq Llama-3.1 8B Online
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- Widescreen Workspace Columns ----------
left_col, right_col = st.columns([1.1, 1], gap="large")

with left_col:
    st.markdown("<div class='studio-card'>", unsafe_allow_html=True)
    st.markdown("### 💻 Source Code Terminal")
    st.markdown("<div style='color:#94a3b8; font-size:13.5px; margin-bottom:16px;'>Paste your code and optional compiler error output to initiate diagnosis.</div>", unsafe_allow_html=True)

    # Top Toolbar controls
    ctrl_col1, ctrl_col2 = st.columns([1, 1])
    with ctrl_col1:
        language = st.selectbox("Language Context", ["Python", "JavaScript / TypeScript", "C++", "Java", "C#", "Go", "Rust", "SQL"], index=0)
    
    with ctrl_col2:
        sample_choice = st.selectbox("💡 Try a Sample Bug", list(SAMPLE_BUGS.keys()))
        if sample_choice != "Select Sample...":
            sample_code, sample_err = SAMPLE_BUGS[sample_choice]
        else:
            sample_code, sample_err = "", ""

    # Inputs
    code_val = sample_code if sample_code else ""
    err_val = sample_err if sample_err else ""

    broken_code_input = st.text_area(
        "Source Code",
        value=code_val,
        height=260,
        placeholder="Paste your source code here...",
        key="code_input_area"
    )

    error_input = st.text_area(
        "Compiler / Traceback Error (Optional)",
        value=err_val,
        height=120,
        placeholder="Paste runtime exceptions, traceback logs, or compiler errors...",
        key="error_input_area"
    )

    # Advanced Model Settings
    with st.expander("⚙️ Fine-Tune AI Parameters"):
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            temp = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.05, help="Lower values are more precise; higher values are more creative.")
        with p_col2:
            max_tokens = st.slider("Max Token Limit", min_value=256, max_value=2048, value=1024, step=64)

    st.markdown("<br>", unsafe_allow_html=True)
    analyze = st.button("🚀 Diagnose & Fix Code", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    if not analyze:
        # Default Workspace State (Feature Dashboard)
        st.markdown("<div class='studio-card'>", unsafe_allow_html=True)
        st.markdown("### 🧠 AI Tutor Intelligence Hub")
        st.markdown("<div style='color:#94a3b8; font-size:13.5px; margin-bottom:20px;'>Ready to diagnose your code. Here is how EduFix assists your learning process:</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class='feature-box'>
                <div class='feature-title'>🎯 Root Cause Isolation</div>
                <div class='feature-desc'>Identifies exact line numbers and logic bottlenecks causing syntax or runtime failures.</div>
            </div>
            <div class='feature-box'>
                <div class='feature-title'>📚 Educational Explanations</div>
                <div class='feature-desc'>Provides clear 2-3 sentence explanations without jargon so you learn the CS concepts behind the bug.</div>
            </div>
            <div class='feature-box'>
                <div class='feature-title'>⚡ Refactored Clean Code</div>
                <div class='feature-desc'>Generates complete, execution-ready code snippets with industry-standard best practices.</div>
            </div>
            <div class='feature-box'>
                <div class='feature-title'>🚀 1-Click Copy & Export</div>
                <div class='feature-desc'>Download corrected Python scripts directly or copy solutions instantly to your clipboard.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # Analysis Run State
        if not broken_code_input or not broken_code_input.strip():
            st.warning("⚠️ Please paste your code into the terminal before running the analyzer.")
        else:
            with st.spinner("🧠 Analyzing code structure & traceback context..."):
                try:
                    system_instructions = (
                        "You are an elite Computer Science Professor and AI Code Tutor. "
                        f"Language context: {language}.\n"
                        "When analyzing broken code, strictly follow this structured format:\n"
                        "### 🔍 Root Cause Analysis\n"
                        "Pinpoint the line number and core issue in 1-2 clear sentences.\n\n"
                        "### 💡 Pedagogical Explanation\n"
                        "Explain *why* the bug occurred and the concept needed to avoid it in 2-3 friendly sentences.\n\n"
                        "### 🛠️ Corrected Solution\n"
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
                    st.markdown("### 🛠️ AI Solution & Diagnostic Brief")
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

                    # Render Text Response
                    st.markdown(response_text)

                    # Export Controls if Code Exists
                    if fixed_code:
                        st.divider()
                        d_col1, d_col2 = st.columns([1, 1])
                        with d_col1:
                            st.download_button(
                                label="📥 Download Script",
                                data=fixed_code,
                                file_name="fixed_code.py",
                                mime="text/plain",
                                use_container_width=True
                            )
                        with d_col2:
                            copy_id = "copy-btn-" + uuid.uuid4().hex
                            copy_html = f"""
                            <button id='{copy_id}' style='background:linear-gradient(135deg,#6366f1,#ec4899);color:white;border:none;border-radius:12px;padding:10px 10px;cursor:pointer;width:100%;font-weight:700;font-family:"Plus Jakarta Sans", sans-serif;'>📋 Copy Corrected Code</button>
                            <script>
                            const btn = document.getElementById('{copy_id}');
                            if (btn) {{
                              btn.addEventListener('click', async () => {{
                                try {{
                                  await navigator.clipboard.writeText({json.dumps(fixed_code)});
                                  btn.innerText = '✅ Copied to Clipboard!';
                                  setTimeout(() => {{ btn.innerText = '📋 Copy Corrected Code'; }}, 2000);
                                }} catch(e) {{
                                  btn.innerText = '❌ Copy Failed';
                                  setTimeout(() => {{ btn.innerText = '📋 Copy Corrected Code'; }}, 2000);
                                }}
                              }});
                            }}
                            </script>
                            """
                            st.markdown(copy_html, unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"❌ An error occurred during API execution: {e}")

# ---------- Footer ----------
st.markdown("<div class='footer'>Crafted with 💡 by an 18‑year‑old founder • EduFix AI Studio</div>", unsafe_allow_html=True)
