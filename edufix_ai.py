import streamlit as st
from groq import Groq
import re

# 1. Custom Premium Page Configuration
st.set_page_config(
    page_title="EduFix AI | Smart Homework Assistant",
    page_icon="🎓",
    layout="centered"
)

# 2. Securely Connect to the AI Brain
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_API_KEY)
except (KeyError, FileNotFoundError):
    st.error(
        "⚠️ No Groq API key found. Add `GROQ_API_KEY` to your Streamlit "
        "secrets (Settings → Secrets on Streamlit Cloud, or a local "
        "`.streamlit/secrets.toml` file) before running this app."
    )
    st.stop()

# 3. Clean Visual Header Section
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🎓 EduFix AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; color: #FAFAFA;'>The Intelligent Code Tutor for Students</p>", unsafe_allow_html=True)
st.write("Stop stressing over confusing terminal bugs. Paste your issue below for a friendly breakdown and an instant code correction.")
st.divider()

# 4. Organized Side-by-Side Input Columns
col1, col2 = st.columns(2)
with col1:
    st.markdown("### 📋 Your Code")
    broken_code_input = st.text_area(
        "Paste your broken code:",
        height=220,
        placeholder="def my_function()\n    print('Hello')",
        label_visibility="collapsed"
    )
with col2:
    st.markdown("### ❌ The Error")
    error_input = st.text_area(
        "Paste the error message (Optional):",
        height=220,
        placeholder="SyntaxError: expected ':'",
        label_visibility="collapsed"
    )

st.write("")  # Spacer

# 5. Full-Width Premium Action Button
if st.button("🚀 Analyze & Fix My Code", type="primary", use_container_width=True):
    if not broken_code_input.strip():
        st.warning("Please paste some code first!")
    else:
        with st.spinner("🧠 AI Agent diagnosing your script..."):
            try:
                system_instructions = (
                    "You are an expert, encouraging computer science tutor. "
                    "A student will give you broken code and an error message. "
                    "First, point out the exact line where the mistake is. "
                    "Second, explain the fix in simple, universal language under 3 sentences. "
                    "Third, output the completely fixed, working code in a single fenced "
                    "code block like ```python ... ```."
                )
                completion = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": f"Broken Code:\n{broken_code_input}\n\nError:\n{error_input}"}
                    ],
                    temperature=0.2,
                )

                response_text = completion.choices[0].message.content

                # 6. Beautiful, Structured Output Display
                st.balloons()  # Fun visual milestone celebration
                st.success("Analysis Complete!")

                # Split the explanation from the fixed code block so the
                # code gets its own syntax-highlighted, copy-ready box
                # instead of being dumped as one plain-text blob.
                code_match = re.search(r"```(?:python)?\s*\n?(.*?)```", response_text, re.DOTALL)

                if code_match:
                    explanation = response_text[:code_match.start()].strip()
                    fixed_code = code_match.group(1).strip()
                else:
                    explanation = response_text
                    fixed_code = None

                st.markdown("### 🛠️ What Went Wrong")
                st.info(explanation if explanation else "See the fixed code below.")

                if fixed_code:
                    st.markdown("### ✅ Fixed Code")
                    st.code(fixed_code, language="python")

            except Exception as e:
                st.error(f"An error occurred: {e}")

st.divider()
st.markdown("<p style='text-align: center; font-size: 12px; color: #888888;'>Built with 🧠 by an 18-year-old founder.</p>", unsafe_allow_html=True)
