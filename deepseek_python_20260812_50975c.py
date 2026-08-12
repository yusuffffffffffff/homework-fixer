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
:root{
  --bg-color: #0f1724; /* dark navy */
  --card-color: #0b1220; /* slightly lighter */
  --accent: #FF6B6B; /* coral */
  --muted: #94a3b8;
}

[data-testid="stAppViewContainer"] {
  background: linear-gradient(180deg, #071025 0%, #081125 100%);
  color: #e6eef8;
}

.stApp, .css-18e3th9 { background: transparent }

h1, h2, h3 { color: #ffffff }

.card {
  background: var(--card-color);
  padding: 18px;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(2,6,23,0.6);
}

.header-left { display: flex; gap: 14px; align-items: center }
.logo {
  background: linear-gradient(120deg, #FFB199, #FF6B6B);
  width: 72px; height: 72px; border-radius: 14px; display:flex; align-items:center; justify-content:center; font-size:34px;
}

.small-muted { color: var(--muted); font-size: 13px }

.stButton>button {
  background: linear-gradient(90deg,var(--accent), #FF9A9A) !important;
  color: white !important; border: none; padding: 10px 18px; font-weight:600; border-radius: 10px;
}

textarea { background-color: #020617; color: #e6eef8 }

.output-code {
  background: #021022; padding: 12px; border-radius: 8px; color: #dbeafe; font-family: monospace; white-space: pre-wrap; overflow:auto;
}

.footer { color: #9aa6b2; font-size:12px; text-align:center; padding-top: 12px }
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
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(
            """
            <div class='logo'>🎓</div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown("<div class='header-left'>", unsafe_allow_html=True)
        st.markdown("<div style='margin-left:8px'>")
        st.markdown("<h1 style='margin:0'>EduFix AI</h1>")
        # Improved descriptive text
        st.markdown("<div class='small-muted'>An encouraging code tutor that explains problems clearly and returns working fixes.</div>")
        st.markdown("</div>")
        st.markdown("</div>")

st.markdown("<div class='card'>", unsafe_allow_html=True)

# Use tabs for input and examples
tab_input, tab_examples = st.tabs(["🔧 Input", "💡 Examples & Tips"])

with tab_input:
    st.markdown("### Paste your code below")
    st.markdown("For the most accurate suggestions, also paste the full error or traceback (optional).")

    # Two-column layout for code + error
    left, right = st.columns([2, 1])
    with left:
        broken_code_input = st.text_area(
            "Code Input",
            height=300,
            placeholder="def my_function():\n    print('Hello')",
            label_visibility="collapsed",
            key="code_input",
        )

    with right:
        error_input = st.text_area(
            "Error Input",
            height=300,
            placeholder="Full traceback or compiler error (optional)",
            label_visibility="collapsed",
            key="error_input",
        )

    # Advanced options in an expander
    with st.expander("Advanced options (Model settings)"):
        temp = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.05)
        max_tokens = st.slider("Max output tokens", min_value=128, max_value=2048, value=800, step=64)

    # Action row
    action_col, status_col = st.columns([1, 3])
    with action_col:
        analyze = st.button("🚀 Diagnose & Fix", help="Diagnose and fix my code")

    with status_col:
        st.markdown("<div class='small-muted'>Tip: Paste the entire error or traceback (including file and line numbers) for a more precise fix.</div>", unsafe_allow_html=True)

with tab_examples:
    st.markdown("### Common issues the tool handles")
    st.markdown("- Missing colon in a function, loop, or conditional")
    st.markdown("- Indentation errors from mixing tabs and spaces")
    st.markdown("- NameError: using a variable before it's defined")
    st.markdown("- TypeError from invalid operations or wrong function arguments")
    st.markdown("\nTip: Paste both code and the exact error message to help the tutor pinpoint the issue faster.")

# Outcome area
st.markdown("</div>", unsafe_allow_html=True)  # close card

st.divider()

if analyze:
    if not broken_code_input or not broken_code_input.strip():
        st.warning("Please paste your code before running the analyzer.")
    else:
        with st.spinner("🧠 Diagnosing — generating a clear fix..."):
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

                # Extract the assistant content from the response
                response_text = completion.choices[0].message.content

                # Present the result in a nice layout
                st.balloons()
                st.success("Analysis complete — see the suggested fix below.")

                st.markdown("### 🛠️ AI Tutor — Suggested Fix")

                # Try to split explanation and fixed code if the model used code fences
                fixed_code = None
                explanation = response_text or ""
                if response_text and "```" in response_text:
                    parts = response_text.split("```")
                    # Either: [text, lang+code, text] or [text, code]
                    if len(parts) >= 2:
                        before = parts[0].strip()
                        # find the part that is likely code (the first fenced block)
                        code_block = parts[1]
                        # remove optional language token from the first line
                        code_lines = code_block.splitlines()
                        if code_lines and code_lines[0].strip().isalpha():
                            code_content = "\n".join(code_lines[1:]).strip()
                        else:
                            code_content = code_block.strip()

                        fixed_code = code_content
                        explanation = before

                if explanation:
                    st.markdown(f"**Explanation (plain language):** {explanation}")

                if fixed_code:
                    st.markdown("**Fixed code (copy & run):**")
                    # Download + Copy controls
                    dl_col, copy_col, code_col = st.columns([0.6, 0.6, 6])
                    with dl_col:
                        st.download_button(
                            label="📥 Download",
                            data=fixed_code,
                            file_name="fixed_code.py",
                            mime="text/plain",
                        )
                    with copy_col:
                        # best-effort HTML+JS copy button; falls back to manual selection below
                        copy_id = "copy-btn-" + uuid.uuid4().hex
                        copy_html = f"""
                        <button id='{copy_id}' style='background:linear-gradient(90deg,#FF6B6B,#FF9A9A);color:white;border:none;border-radius:8px;padding:6px 10px;cursor:pointer'>📋 Copy</button>
                        <script>
                        const btn = document.getElementById('{copy_id}');
                        if (btn) {{
                          btn.addEventListener('click', async () => {{
                            try {{
                              await navigator.clipboard.writeText({json.dumps(fixed_code)});
                              const old = btn.innerText;
                              btn.innerText = '✅ Copied';
                              setTimeout(()=>btn.innerText = '📋 Copy', 1500);
                            }} catch(e) {{
                              btn.innerText = '❌ Copy failed';
                              setTimeout(()=>btn.innerText = '📋 Copy',1500);
                            }}
                          }});
                        }}
                        </script>
                        """
                        st.markdown(copy_html, unsafe_allow_html=True)
                    with code_col:
                        st.code(fixed_code, language='python')
                else:
                    st.markdown("**Model output:**")
                    st.markdown(f"<div class='output-code'>{response_text}</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"An error occurred: {e}")

st.markdown("<div class='footer'>Built with care by an 18‑year‑old founder • EduFix AI</div>", unsafe_allow_html=True)