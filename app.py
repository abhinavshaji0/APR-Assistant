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
"""

def evaluate_code(repaired_code, test_code):
    """Executes the repaired code and the test cases together."""
    full_code = f"{repaired_code}\n\n{test_code}"
    local_env = {}
    
    try:
        exec(full_code, {}, local_env)
        return True, "Success: All tests passed!"
    except Exception as e:
        # Capture the exact error traceback if the AI's code fails
        return False, traceback.format_exc()

# 2. Initialize Groq Client
# Ensure "GROQ_API_KEY" is set in your Streamlit secrets
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

# 3. Streamlit UI Setup
st.set_page_config(page_title="APR Code Assistant", layout="wide")
st.title("🛠️ Automated Program Repair (APR) Assistant")
st.markdown("A research-to-prototype application demonstrating agentic LLM-driven code repair via Groq.")

# 4. Input section
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Buggy Code")
    buggy_code = st.text_area("Paste the problematic Python snippet here:", height=300)
    
    if st.button("Generate Repair & Test", type="primary"):
        if buggy_code:
            status_text = st.empty()
            max_retries = 3
            attempt = 1
            success = False
            
            # The context that builds up if failures occur
            current_prompt = f"Buggy Code:\n{buggy_code}\n\nFix this code and provide the output as raw Python."

            while attempt <= max_retries and not success:
                status_text.info(f"🔄 Attempt {attempt} of {max_retries}: Generating repair...")
                
                try:
                    # Step 1: Ask the LLM for the fix
                    repair_response = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": APR_SYSTEM_PROMPT},
                            {"role": "user", "content": current_prompt}
                        ],
                        model="llama-3.1-70b-versatile",
                    )
                    repair_text = repair_response.choices[0].message.content
                    
                    # Extract just the Python code block for execution
                    if "```python" in repair_text:
                        repaired_code = repair_text.split("```python")[1].split("```")[0].strip()
                    else:
                        repaired_code = repair_text.replace("```python", "").replace("```", "").strip()
                    
                    # Step 2: Ask the LLM to write a unit test
                    status_text.info(f"🧪 Attempt {attempt}: Generating unit tests...")
                    test_prompt = f"Write a strict Python assert test for this code snippet. Only output raw Python code:\n{buggy_code}"
                    test_response = client.chat.completions.create(
                        messages=[{"role": "user", "content": test_prompt}],
                        model="llama-3.1-70b-versatile",
                    )
                    test_text = test_response.choices[0].message.content
                    
                    if "```python" in test_text:
                        test_code = test_text.split("```python")[1].split("```")[0].strip()
                    else:
                        test_code = test_text.replace("```python", "").replace("```", "").strip()
                    
                    # Step 3: Execute and Evaluate
                    status_text.info(f"⚙️ Attempt {attempt}: Executing tests...")
                    passed, result_msg = evaluate_code(repaired_code, test_code)
                    
                    if passed:
                        success = True
                        status_text.success("✅ Repair successful and verified by automated tests!")
                        # Save both the full explanation and the test to display in the UI
                        st.session_state['repair_full_text'] = repair_text
                        st.session_state['test_code'] = test_code
                    else:
                        status_text.warning(f"❌ Attempt {attempt} failed. Capturing error and retrying...")
                        # Step 4: The Feedback Loop
                        current_prompt += f"\n\nYour previous fix failed with this error:\n{result_msg}\n\nPlease analyze the error and provide a corrected fix."
                        attempt += 1
                        
                except Exception as e:
                    status_text.error(f"API Error: {str(e)}")
                    break
            
            if not success and attempt > max_retries:
                status_text.error(f"🚨 Failed to generate a passing repair after {max_retries} attempts.")
                st.error(result_msg) # Show the final error

        else:
            st.warning("Please provide some code to repair.")

with col2:
    st.subheader("Repair Output")
    if 'repair_full_text' in st.session_state:
        # Render the Analysis, Strategy, and Code beautifully formatted
        st.markdown(st.session_state['repair_full_text'])
        st.divider()
        st.markdown("### Generated Unit Test")
        st.code(st.session_state['test_code'], language='python')