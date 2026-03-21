import streamlit as st
from groq import Groq
import os

# 1. Configuration & System Prompt
APR_SYSTEM_PROMPT = """
You are an expert Automated Program Repair (APR) system. Your task is to analyze buggy code and provide a robust, syntactically correct fix. 

Follow this strict methodology:
1. ANALYSIS: Briefly identify the root cause of the bug in the provided code snippet.
2. REPAIR STRATEGY: Outline the step-by-step logic required to resolve the issue, focusing on minimal intrusion to the original code structure.
3. REPAIRED CODE: Provide the corrected code. Ensure it is fully functional and optimized.

Format your response exactly with the headers:
### Analysis
### Repair Strategy
### Repaired Code
"""

# 2. Initialize Groq Client
# Ensure "GROQ_API_KEY" is set in your environment variables or Streamlit secrets
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

# 3. Streamlit UI Setup
st.set_page_config(page_title="APR Code Assistant", layout="wide")
st.title("🛠️ Automated Program Repair (APR) Assistant")
st.markdown("A research-to-prototype application demonstrating LLM-driven code repair via Groq.")

# 4. Input section
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Buggy Code")
    buggy_code = st.text_area("Paste the problematic Python snippet here:", height=300)
    error_msg = st.text_input("Optional: Paste the error message (if any)")
    
    if st.button("Generate Repair", type="primary"):
        if buggy_code:
            with st.spinner("Analyzing with Groq LPU™..."):
                try:
                    # Construct the messages for Groq
                    prompt_content = f"Buggy Code:\n{buggy_code}"
                    if error_msg:
                        prompt_content += f"\n\nError Message:\n{error_msg}"

                    # Call Groq API
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": APR_SYSTEM_PROMPT},
                            {"role": "user", "content": prompt_content},
                        ],
                        model="llama-3.3-70b-versatile", # High-performance coding model
                        temperature=0.2, # Lower temperature for more consistent code repair
                    )
                    
                    # Store response
                    st.session_state['repair_output'] = chat_completion.choices[0].message.content
                except Exception as e:
                    st.error(f"Error calling Groq API: {e}")
        else:
            st.warning("Please provide some code to repair.")

with col2:
    st.subheader("Repair Output")
    if 'repair_output' in st.session_state:
        st.markdown(st.session_state['repair_output'])