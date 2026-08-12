import streamlit as st
from groq import Groq
import json
import uuid

# Page configuration
st.set_page_config(
    page_title="EduFix AI | Premium Homework Assistant",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------- Custom CSS for visual enhancement ----------
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap');

:root {
  --bg-color: #030305;
  --glass-bg: rgba(22, 28, 48, 0.7); /* Warmer glass */
  --glass-border: rgba(255, 255, 255, 0.06); /* Finer border */
  --primary: #7c7fed; /* Refined Indigo */
  --accent: #f472b6; /* Refined Magenta */
  --glow: rgba(124, 127, 237, 0.25); /* Diffused glow */
  --text-main: #f1f5f9;
  --text-muted: #94a3b8;
}

/* Base typography for premium feel */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    letter-spacing: -0.01em;
}

/* Deep, swirling cosmic gradient */
[data-testid="stAppViewContainer"] {
  background: radial-gradient(circle at 75% 25%, #231f6d 0%, var(--bg-color) 45%, var(--bg-color) 100%);
  color: var(--text-main);
}

.stApp, .css-18e3th9 { background: transparent }

h1, h2, h3 { 
    color: #ffffff; 
    font-weight: 700;
    letter-spacing: -0.03em;
    margin-bottom: 0.5rem;
}

/* Elevated Glassmorphism Card */
.card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: 30px;
  border-radius: 20px;
  border: 1px solid var(--glass-border);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
  margin-bottom: 25px;
}

/* Header styling and polished logo */
.header-left { display: flex; gap: 20px; align-items: center; margin-bottom: 25px;}
.logo {
  background: linear-gradient(135deg, var(--primary), var(--accent));
  width: 80px; height: 80px; 
  border-radius: 20px; 
  display:flex; align-items:center; justify-content:center; 
  font-size:40px;
  box-shadow: 0 10px 25px var(--glow);
}

.small-muted { color: var(--text-muted); font-size: 15px; line-height: 1.6; }

/* Premium, Animated Call-to-Action Button */
.stButton>button {
  background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
  color: white !important; 
  border: none; 
  padding: 12px 28px; 
  font-weight: 700; 
  font-size: 16px;
  border-radius: 14px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px var(--glow);
}

.stButton>button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px var(--glow);
}

/* Modern inputs with focus states */
textarea, [data-baseweb="input"] { 
    background-color: rgba(0,0,0,0.3) !important; 
    color: var(--text-main) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 10px !important;
    font-family: 'Fira Code', monospace !important;
}

textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px var(--glow) !important;
}

/* Distinctive Output Code Block */
.output-code {
  background: rgba(0, 0, 0, 0.5); 
  border: 1px solid var(--glass-border);
  padding: 20px; 
  border-radius: 14px; 
  color: #c7d2fe; 
  font-family: 'Fira Code', monospace; 
  white-space: pre-wrap; 
  overflow:auto;
  margin-top: 15px;
}

/* Polished Scrollbar for code blocks */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); border-radius: 5px; }
::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 5px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

.footer { color: #8096ac; font-size:14px; text-align:center; padding-top: 40px; padding-bottom: 30px; font-weight: 600; opacity: 0.8;}
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
        st.markdown(
            """
            <div class='header-left'>
                <div style='margin-left:4px'>
                    <h1 style='margin:0; padding-bottom:6px;'>EduFix AI</h1>
                    <div class='small-muted'>An encouraging code tutor that explains problems clearly and returns working fixes.</div>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )

st.markdown("<div class='card'>", unsafe_allow_html=True)

# Tabs with premium language
tab_input, tab_examples = st.tabs(["🚀 Analysis Terminal", "💡 Tutorial Guidance"])

with tab_input:
    st.markdown("### Paste your source code below")
    st.markdown("<div class='small-muted' style='margin-bottom: 16px;'>For the highest quality response, also paste the entire error or traceback sequence (optional).</div>", unsafe_allow_html=True)

    # Clean two-column input layout
    left, right = st.columns([2, 1])
    with left:
        broken_code_input = st.text_area(
            "Source Code",
            height=300,
            placeholder="e.g.,\ndef say_hello():\n    print('Hello World')",
            label_visibility="collapsed",
            key="code_input",
        )

    with right:
        error_input = st.text_area(
            "Compiler / Runtime Error",
            height=300,
            placeholder="Paste full traceback sequence here (optional)",
            label_visibility="collapsed",
            key="error_input",
        )

    # Advanced options are now premium settings
    with st.expander("⚙️ Fine-Tune Analysis Parameters"):
        temp = st.slider("Temperature (0.0=Deterministic, 1.0=Creative)", min_value=0.0, max_value=1.0, value=0.2, step=0.05)
        max_tokens = st.slider("Max Response Tokens", min_value=128, max_value=2048, value=800, step=64)

    st.markdown("<br>", unsafe_allow_html=True)

    # Primary Action Row
    action_col, status_col = st.columns([1, 2.5])
    with action_col:
        analyze = st.button("🚀 Diagnose & Fix", help="Initiate AI analysis", use_container_width=True)

    with status_col:
        st.markdown("<div class='small-muted' style='padding-top: 12px;'><i>Tip: Including explicit file paths and line numbers in your error simplifies diagnosis.</i></div>", unsafe_allow_html=True)

with tab_examples:
    st.markdown("### Common issues we optimize for:")
    st.markdown("- 🔵 Missing colons (syntax standard compliance)")
    st.markdown("- 🔵 Indentation deviations (mixing tabs and spaces)")
    st.markdown("- 🔵 `NameError` (undefined variable identification)")
    st.markdown("- 🔵 `TypeError` (invalid operation sequence detection)")
    st.info("Pro Tip: Context is key. The more environmental data you can provide (like the full error box), the faster the AI can precisely optimize your solution.")

st.markdown("</div>", unsafe_allow_html=True)  # close card

if analyze:
    if not broken_code_input or not broken_code_input.strip():
        st.warning("⚠️ Please paste your source code before running the analyzer.")
    else:
        with st.spinner("🧠 Performing deep analysis... generating a precise optimization..."):
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
                
                # New card for the premium output sequence
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("### 🛠️ AI Tutor Solution")
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
                        <button id='{copy_id}' style='background:linear-gradient(135deg,#7c7fed,#f472b6);color:white;border:none;border-radius:14px;padding:10px 10px;cursor:pointer;width:100%;font-weight:700;font-family:Inter;letter-spacing:-0.02em;transition:all 0.3s ease;'>📋 Copy Code</button>
                        <script>
                        const btn = document.getElementById('{copy_id}');
                        if (btn) {{
                          btn.addEventListener('click', async () => {{
                            try {{
                              await navigator.clipboard.writeText({json.dumps(fixed_code)});
                              btn.innerText = '✅ Copied!';
                              btn.style.boxShadow = '0 0 10px #7c7fed';
                              setTimeout(() => {{
                                  btn.innerText = '📋 Copy Code';
                                  btn.style.boxShadow = 'none';
                              }}, 2000);
                            }} catch(e) {{
                              btn.innerText = '❌ Failed';
                              setTimeout(() => btn.innerText = '📋 Copy Code', 2000);
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

st.markdown("<div class='footer'>Crafted with 💡 by an 18‑year‑old founder • EduFix AI Premium</div>", unsafe_allow_html=True)
