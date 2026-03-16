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
import streamlit as st
import google.generativeai as genai
import os

# Configure API Key (Make sure to set this in your environment variables)
os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Define the model and system prompt
model = genai.GenerativeModel('gemini-2.5-flash', 
                              system_instruction=APR_SYSTEM_PROMPT)

st.set_page_config(page_title="APR Code Assistant", layout="wide")
st.title("🛠️ Automated Program Repair (APR) Assistant")
st.markdown("A research-to-prototype application demonstrating LLM-driven code repair workflows.")

# Input section
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Buggy Code")
    buggy_code = st.text_area("Paste the problematic Python snippet here:", height=300)
    error_msg = st.text_input("Optional: Paste the error message (if any)")
    
    if st.button("Generate Repair", type="primary"):
        if buggy_code:
            with st.spinner("Analyzing and generating repair strategy..."):
                # Construct the user prompt
                user_prompt = f"Buggy Code:\n{buggy_code}\n\n"
                if error_msg:
                    user_prompt += f"Error Message:\n{error_msg}\n"
                
                # Call the API
                response = model.generate_content(user_prompt)
                
                # Store response in session state to display in the second column
                st.session_state['repair_output'] = response.text
        else:
            st.warning("Please provide some code to repair.")

with col2:
    st.subheader("Repair Output")
    if 'repair_output' in st.session_state:
        st.markdown(st.session_state['repair_output'])