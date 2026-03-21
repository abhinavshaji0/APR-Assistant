import streamlit as st
import traceback
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
def evaluate_code(repaired_code, test_code):
    """Executes the repaired code and the test cases together."""
    # Combine the function definition and the test execution
    full_code = f"{repaired_code}\n\n{test_code}"
    
    # Create an isolated environment dictionary for execution
    local_env = {}
    
    try:
        # Attempt to run the combined code
        exec(full_code, {}, local_env)
        return True, "Success: All tests passed!"
    except Exception as e:
        # If it fails, capture the exact error traceback
        error_trace = traceback.format_exc()
        return False, error_trace
    
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
    
    if st.button("Generate Repair & Test", type="primary"):
     if buggy_code:
        # Create a placeholder in the UI so we can update the status live
        status_text = st.empty()
        
        max_retries = 3
        attempt = 1
        success = False
        
        # We will build up the context if it fails
        current_prompt = f"Buggy Code:\n{buggy_code}\n\nFix this code and provide the output as raw Python."

        while attempt <= max_retries and not success:
            status_text.info(f"🔄 Attempt {attempt} of {max_retries}: Generating repair...")
            
            # 1. Ask the LLM for the fix
            repair_response = model.generate_content(current_prompt)
            # (Assuming you parse out just the Python code into a variable called 'repaired_code')
            repaired_code = repair_response.text.replace("```python", "").replace("```", "").strip()
            
            # 2. Ask the LLM to write a unit test for this specific function
            status_text.info(f"🧪 Attempt {attempt}: Generating unit tests...")
            test_prompt = f"Write a strict Python assert test for this code snippet. Only output raw Python code:\n{buggy_code}"
            test_response = model.generate_content(test_prompt)
            test_code = test_response.text.replace("```python", "").replace("```", "").strip()
            
            # 3. Execute and Evaluate
            status_text.info(f"⚙️ Attempt {attempt}: Executing tests...")
            passed, result_msg = evaluate_code(repaired_code, test_code)
            
            if passed:
                success = True
                status_text.success("✅ Repair successful and verified by automated tests!")
                st.session_state['repair_output'] = repaired_code
                st.session_state['test_output'] = test_code
            else:
                status_text.warning(f"❌ Attempt {attempt} failed. Capturing error and retrying...")
                # 4. The Feedback Loop: Append the error to the prompt for the next attempt
                current_prompt += f"\n\nYour previous fix failed with this error:\n{result_msg}\n\nPlease analyze the error and provide a corrected fix."
                attempt += 1
        
        if not success:
            status_text.error(f"🚨 Failed to generate a passing repair after {max_retries} attempts.")
            st.error(result_msg) # Show the final error

     else:
        st.warning("Please provide some code to repair.")
with col2:
    st.subheader("Repair Output")
    if 'repair_output' in st.session_state:
        st.markdown(st.session_state['repair_output'])