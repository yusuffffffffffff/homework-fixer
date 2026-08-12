import streamlit as st
from groq import Groq

# 1. Custom Premium Page Configuration
st.set_page_config(
    page_title="EduFix AI | Smart Homework Assistant",
    page_icon="🎓",
    layout="centered"
)

# 2. Securely Connect to the AI Brain
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY is missing from Streamlit secrets. Please add it and restart the app.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

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
if st.button("🚀 Analyze & Fix My Code"):
    if not broken_code_input or not broken_code_input.strip():
        st.warning("Please paste some code first!")
    else:
        with st.spinner("🧠 AI Agent diagnosing your script..."):
            try:
                system_instructions = (
                    "You are an expert, encouraging computer science tutor. "
                    "A student will give you broken code and an error message. "
                    "First, point out the exact line where the mistake is. "
                    "Second, explain the fix in simple, universal language under 3 sentences. "
                    "Third, output the completely fixed, working code block."
                )

                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": f"Broken Code:\n{broken_code_input}\n\nError:\n{error_input}"}
                    ],
                    temperature=0.2,
                )

                # Try to robustly extract the assistant content from common response shapes
                response_text = None
                try:
                    # completion.choices is common; try index 0
                    choices = getattr(completion, "choices", None) or completion.get("choices") if isinstance(completion, dict) else None
                    if choices:
                        first = choices[0] if isinstance(choices, (list, tuple)) else choices
                        # possible shapes:
                        # first.message.content, first['message']['content'], first.get('text')
                        if isinstance(first, dict):
                            response_text = first.get("message", {}).get("content") or first.get("text")
                        else:
                            # object-like
                            msg = getattr(first, "message", None)
                            if msg:
                                response_text = getattr(msg, "content", None) or (msg.get("content") if isinstance(msg, dict) else None)
                            else:
                                response_text = getattr(first, "text", None)
                except Exception:
                    response_text = None

                # Fallback to stringifying whole completion if nothing else worked
                if not response_text:
                    try:
                        response_text = str(completion)
                    except Exception:
                        response_text = "Could not parse model response."

                # 6. Beautiful Tabbed & Structured Output Display
                st.balloons()  # Fun visual milestone celebration
                st.success("Analysis Complete!")

                st.markdown("### 🛠️ AI Tutor Solution")
                st.info(response_text)

            except Exception as e:
                st.error(f"An error occurred: {e}")

st.divider()
st.markdown("<p style='text-align: center; font-size: 12px; color: #888888;'>Built with 🧠 by an 18-year-old founder.</p>", unsafe_allow_html=True)