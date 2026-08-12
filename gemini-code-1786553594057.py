import streamlit as st
from groq import Groq
import json
import uuid

# Page configuration
st.set_page_config(
    page_title="EduFix AI | Smart Homework Assistant",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------- Custom CSS for visual enhancement ----------
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap');

:root {
  --bg-color: #050505; 
  --glass-bg: rgba(17, 24, 39, 0.65);
  --glass-border: rgba(255, 255, 255, 0.08);
  --primary: #6366f1; /* Indigo */
  --accent: #ec4899; /* Pink */
  --glow: rgba(99, 102, 241, 0.4);
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
}

/* Base typography */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Background gradient */
[data-testid="stAppViewContainer"] {
  background: radial-gradient(circle at top right, #1e1b4b 0%, var(--bg-color) 40%, var(--bg-color) 100%);
  color: var(--text-main);
}

.stApp, .css-18e3th9 { background: transparent }

h1, h2, h3 { 
    color: #ffffff; 
    font-weight: 700;
    letter-spacing: -0.02em;
}

/* Glassmorphism Card */
.card {
  background: var(--glass-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  padding: 24px;
  border-radius: 16px;
  border: 1px solid var(--glass-border);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
  margin-bottom: 20px;
}

/* Header styling */
.header-left { display: flex; gap: 18px; align-items: center; margin-bottom: 20px;}
.logo {
  background: linear-gradient(135deg, var(--primary), var(--accent));
  width: 72px; height: 72px; 
  border-radius: 18px; 
  display:flex; align-items:center; justify-content:center; 
  font-size:36px;
  box-shadow: 0 8px 20px var(--glow);
}

.small-muted { color: var(--text-muted); font-size: 14px; line-height: 1.5; }

/* Animated Buttons */
.stButton>button {
  background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
  color: white !important; 
  border: none; 
  padding: 10px 24px; 
  font-weight: 600; 
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px var(--glow);
}

/* Inputs and Textareas */
textarea, [data-baseweb="input"] { 
    background-color: rgba(0,0,0,0.3) !important; 
    color: var(--text-main) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 8px !important;
    font-family: 'Fira Code', monospace !important;
}

textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 1px var(--primary) !important;
}

/* Output Code Block */
.output-code {
  background: rgba(0, 0, 0, 0.4); 
  border: 1px solid var(--glass-border);
  padding: 16px; 
  border-radius: 12px; 
  color: #a5b4fc; 
  font-family: 'Fira Code', monospace; 
  white-space: pre-wrap; 
  overflow:auto;
}

/* Custom Scrollbar for code blocks */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); border-radius: 4px; }
::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

.footer { color: #64748b; font-size:13px; text-align:center; padding-top: 30px; padding-bottom: 20px; font-weight: 500;}
"""

st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)

# Connect to Groq securely
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY is missing from Streamlit secrets. Please add it and restart the app.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# ---------- Header ----------
with st.container():
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(
            """
            <div class='logo'>🎓</div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown("<div class='header-left'>", unsafe_allow_html=True)
        st.markdown("<div style='margin-left:4px'>")
        st.markdown("<h1 style='margin:0; padding-bottom:4px;'>EduFix AI</h1>")
        st.markdown("<div class='small-muted'>An encouraging code tutor that explains problems clearly and returns working fixes.</div>")
        st.markdown("</div>")
        st.markdown("</div>")

st.markdown("<div class='card'>", unsafe_allow_html=True)

# Use tabs for input and examples
tab_input, tab_examples = st.tabs(["⚡ Input & Fix", "💡 Tips & Examples"])

with tab_input:
    st.markdown("### Paste your code below")
    st.markdown("<div class='small-muted' style='margin-bottom: 12px;'>For the most accurate suggestions, also paste the full error or traceback (optional).</div>", unsafe_allow_html=True)

    # Two-column layout for code + error
    left, right = st.columns([2, 1])
    with left:
        broken_code_input = st.text_area(
            "Code Input",
            height=280,
            placeholder="def my_function():\n    print('Hello')",
            label_visibility="collapsed",
            key="code_input",
        )

    with right:
        error_input = st.text_area(
            "Error Input",
            height=280,
            placeholder="Paste full traceback or compiler error here (optional)",
            label_visibility="collapsed",
            key="error_input",
        )

    # Advanced options in an expander
    with st.expander("⚙️ Advanced Model Settings"):
        temp = st.slider("Temperature (Creativity vs Strictness)", min_value=0.0, max_value=1.0, value=0.2, step=0.05)
        max_tokens = st.slider("Max output tokens", min_value=128, max_value=2048, value=800, step=64)

    st.markdown("<br>", unsafe_allow_html=True)

    # Action row
    action_col, status_col = st.columns([1, 2.5])
    with action_col:
        analyze = st.button("🚀 Diagnose & Fix", help="Send to AI for analysis", use_container_width=True)

    with status_col:
        st.markdown("<div class='small-muted' style='padding-top: 10px;'><i>Tip: Including line numbers in your error speeds up diagnosis.</i></div>", unsafe_allow_html=True)

with tab_examples:
    st.markdown("### Common issues handled")
    st.markdown("- 🔴 Missing colons in functions, loops, or conditionals")
    st.markdown("- 🔴 Indentation errors (mixing tabs and spaces)")
    st.markdown("- 🔴 `NameError`: using a variable before it's defined")
    st.markdown("- 🔴 `TypeError` from invalid operations or wrong arguments")
    st.info("Pro Tip: The more context you provide in the error box, the better the AI can pinpoint the exact flaw in your logic.")

st.markdown("</div>", unsafe_allow_html=True)  # close card

if analyze:
    if not broken_code_input or not broken_code_input.strip():
        st.warning("⚠️ Please paste your code before running the analyzer.")
    else:
        with st.spinner("🧠 Analyzing code & generating a clear fix..."):
            try:
                system_instructions = (
                    "You are an expert and encouraging computer science tutor. "
                    "When given broken code and an optional error message, do the following: "
                    "1) Identify the exact line(s) causing the problem. "
                    "2) Explain the fix in clear, friendly language (no more than 3 sentences). "
                    "3) Provide the full, corrected code inside a single fenced code block. "
                    "If the language is unclear, assume Python. Keep the response concise and focused on the student learning the fix."
                )

                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": f"Broken Code:\n{broken_code_input}\n\nError:\n{error_input}"}
                    ],
                    temperature=float(temp),
                    max_tokens=int(max_tokens),
                )

                response_text = completion.choices[0].message.content

                st.balloons()
                
                # Create a new card for the output
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("### 🛠️ AI Tutor Suggested Fix")
                st.divider()

                fixed_code = None
                explanation = response_text or ""
                if response_text and "```" in response_text:
                    parts = response_text.split("```")
                    if len(parts) >= 2:
                        before = parts[0].strip()
                        code_block = parts[1]
                        code_lines = code_block.splitlines()
                        if code_lines and code_lines[0].strip().isalpha():
                            code_content = "\n".join(code_lines[1:]).strip()
                        else:
                            code_content = code_block.strip()

                        fixed_code = code_content
                        explanation = before

                if explanation:
                    st.markdown(f"**Explanation:** \n {explanation}")
                    st.markdown("<br>", unsafe_allow_html=True)

                if fixed_code:
                    st.markdown("**Corrected Code:**")
                    dl_col, copy_col, empty_col = st.columns([1, 1, 4])
                    
                    with dl_col:
                        st.download_button(
                            label="📥 Download .py",
                            data=fixed_code,
                            file_name="fixed_code.py",
                            mime="text/plain",
                            use_container_width=True
                        )
                    with copy_col:
                        copy_id = "copy-btn-" + uuid.uuid4().hex
                        copy_html = f"""
                        <button id='{copy_id}' style='background:linear-gradient(135deg,#6366f1,#ec4899);color:white;border:none;border-radius:12px;padding:9px 10px;cursor:pointer;width:100%;font-weight:600;font-family:Inter;'>📋 Copy Code</button>
                        <script>
                        const btn = document.getElementById('{copy_id}');
                        if (btn) {{
                          btn.addEventListener('click', async () => {{
                            try {{
                              await navigator.clipboard.writeText({json.dumps(fixed_code)});
                              btn.innerText = '✅ Copied!';
                              setTimeout(()=>btn.innerText = '📋 Copy Code', 2000);
                            }} catch(e) {{
                              btn.innerText = '❌ Failed';
                              setTimeout(()=>btn.innerText = '📋 Copy Code', 2000);
                            }}
                          }});
                        }}
                        </script>
                        """
                        st.markdown(copy_html, unsafe_allow_html=True)
                    
                    st.code(fixed_code, language='python')
                else:
                    st.markdown("**Model Output:**")
                    st.markdown(f"<div class='output-code'>{response_text}</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True) # close output card

            except Exception as e:
                st.error(f"An error occurred during API call: {e}")

st.markdown("<div class='footer'>Crafted with 💡 by an 18‑year‑old founder • EduFix AI</div>", unsafe_allow_html=True)