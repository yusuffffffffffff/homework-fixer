import streamlit as st
from groq import Groq

# 1. Page Configuration
st.set_page_config(page_title="EduFix AI", page_icon="🎓", layout="centered")

# 2. Connect to the free AI brain
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)


# 3. Design the Web Screen Headers
st.title("🎓 EduFix AI")
st.subheader("The Student AI Homework Coding Assistant")
st.write("Paste your broken python code and the error message below to get a friendly explanation and instant fix.")

st.divider()

# 4. Create Two Input Areas for the Student
broken_code_input = st.text_area("📋 Paste your broken code here:", height=150, placeholder="def my_function()\n    print('Hello')")
error_input = st.text_area("❌ Paste the error message here (Optional):", height=70, placeholder="SyntaxError: expected ':'")

# 5. Create the Action Button
if st.button("🚀 Fix My Homework", type="primary"):
    if not broken_code_input.strip():
        st.warning("Please paste some code first!")
    else:
        with st.spinner("AI Agent analyzing your bug..."):
            try:
                # System instructions telling the AI how to act
                system_instructions = (
                    "You are an expert, encouraging computer science tutor. "
                    "A student will give you broken code and an error message. "
                    "First, point out the exact line where the mistake is. "
                    "Second, explain the fix in simple, universal language under 3 sentences. "
                    "Third, output the completely fixed, working code block."
                )

                # Send input data to the AI model
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": f"Broken Code:\n{broken_code_input}\n\nError:\n{error_input}"}
                    ],
                    temperature=0.2,
                )
                
                # Display results beautifully on the screen
                st.success("Analysis Complete!")
                st.markdown("### 🛠️ AI Tutor Feedback")
                st.write(completion.choices[0].message.content)
                
            except Exception as e:
                st.error(f"An error occurred: {e}")

st.divider()
st.caption("Built with 🧠 by an 18-year-old founder.")
