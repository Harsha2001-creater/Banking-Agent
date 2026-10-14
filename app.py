import streamlit as st
import uuid
from agent import agent, system_prompt 

# 1. Setup the Web Page
st.set_page_config(page_title="NexusBank AI", page_icon="✨", layout="centered")

# Custom CSS for Claude Theme (Left-Aligned User Chat)
claude_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Left-aligned User message pill */
    div[data-testid="stChatMessage"]:has([data-testid="chat-avatar-user"]) {
        background-color: #F0EFEA;
        border-radius: 1rem;
        padding: 0.75rem 1.25rem;
        margin-bottom: 1rem;
        width: fit-content;
        margin-left: 0 !important;      /* Aligns to the left */
        margin-right: auto !important;
        max-width: 85%;
    }

    /* Assistant message styling */
    div[data-testid="stChatMessage"]:has([data-testid="chat-avatar-assistant"]) {
        background-color: transparent;
        padding: 0.75rem 0rem;
    }

    /* Style the Chat Input Box */
    [data-testid="stChatInput"] {
        border-radius: 1.5rem !important;
        border: 1px solid #E5E3D8 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
        background-color: #FFFFFF !important;
    }
</style>
"""
st.markdown(claude_css, unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; font-weight: 500; margin-bottom: 2rem;'>Good afternoon. How can I help you today?</h2>", unsafe_allow_html=True)

# 2. Initialize Session State
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Display History (Updated to ✨)
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# 4. Chat Input Widget
if prompt := st.chat_input("Message NexusBank AI..."):
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    config = {
    "configurable": {"thread_id": st.session_state.thread_id},
    "recursion_limit": 50  # Increases the step limit to give the agent more time to think
}
    
    with st.spinner("Analyzing ledgers and policies..."):
        try:
            response = agent.invoke(
                {"messages": [("system", system_prompt), ("user", prompt)]}, 
                config=config
            )
            final_answer = response["messages"][-1].content
        except Exception as e:
            final_answer = f"⚠️ System Error: {str(e)}"

    # Display Agent Response (Updated to ✨)
    with st.chat_message("assistant", avatar="✨"):
        st.markdown(final_answer)
        
    st.session_state.messages.append({"role": "assistant", "content": final_answer})