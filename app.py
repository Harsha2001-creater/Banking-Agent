import streamlit as st
import uuid
from agent import agent, system_prompt

st.set_page_config(page_title="NexusBank AI", page_icon="✨", layout="centered")

claude_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    div[data-testid="stChatMessage"]:has([data-testid="chat-avatar-user"]) {
        background-color: #F0EFEA;
        border-radius: 1rem;
        padding: 0.75rem 1.25rem;
        margin-bottom: 1rem;
        width: fit-content;
        margin-left: 0 !important;
        margin-right: auto !important;
        max-width: 85%;
    }

    div[data-testid="stChatMessage"]:has([data-testid="chat-avatar-assistant"]) {
        background-color: transparent;
        padding: 0.75rem 0rem;
    }

    [data-testid="stChatInput"] {
        border-radius: 1.5rem !important;
        border: 1px solid #E5E3D8 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
        background-color: #FFFFFF !important;
    }

    /* Style the st.status container to blend with the Claude palette */
    div[data-testid="stStatusWidget"] {
        border-radius: 0.75rem;
        border: 1px solid #E5E3D8;
        background-color: #F7F6F2;
        margin-bottom: 0.75rem;
    }
</style>
"""
st.markdown(claude_css, unsafe_allow_html=True)

# Friendly display names for tool calls
TOOL_LABELS = {
    "lookup_bank_policy": ("📚 S3 Policy Search", "Searching pgvector index for policy clauses..."),
    "get_balance": ("💳 Balance Inquiry", "Querying account balance from AWS RDS..."),
    "get_recent_transactions": ("📊 Ledger Analysis", "Fetching categorized transactions from RDS..."),
    "create_service_request": ("📝 Service Request", "Opening ticket in customer support system...")
}

# Sidebar: Thread Management via RDS
with st.sidebar:
    st.header("Session Management")
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = "user_session_default"

    active_thread = st.text_input("Thread ID (RDS Key)", value=st.session_state.thread_id)
    if active_thread != st.session_state.thread_id:
        st.session_state.thread_id = active_thread
        st.session_state.messages = []
        st.rerun()

    if st.button("Start New Session"):
        st.session_state.thread_id = f"session_{uuid.uuid4().hex[:8]}"
        st.session_state.messages = []
        st.rerun()

    st.caption("Active threads persist in AWS RDS PostgreSQL across reloads.")

st.markdown("<h2 style='text-align: center; font-weight: 500; margin-bottom: 2rem;'>Good afternoon. How can I help you today?</h2>", unsafe_allow_html=True)

config = {
    "configurable": {"thread_id": st.session_state.thread_id},
    "recursion_limit": 50
}

# Hydrate UI history from LangGraph RDS checkpoint
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = []
    state = agent.get_state(config)
    if state and state.values and "messages" in state.values:
        for m in state.values["messages"]:
            if m.type == "human":
                st.session_state.messages.append({"role": "user", "content": m.content})
            elif m.type == "ai" and m.content:
                st.session_state.messages.append({"role": "assistant", "content": m.content})

for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# User Chat Input
if prompt := st.chat_input("Message NexusBank AI..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant", avatar="✨"):
        status_box = st.status("Agent reasoning...", expanded=True)
        response_box = st.empty()
        final_answer = ""
        tool_count = 0

        try:
            # Stream graph node updates
            for event in agent.stream(
                {"messages": [("system", system_prompt), ("user", prompt)]},
                config=config,
                stream_mode="updates"
            ):
                for node, values in event.items():
                    # 1. Capture Agent Decision to Call Tools
                    if node == "agent":
                        last_message = values["messages"][-1]
                        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                            for call in last_message.tool_calls:
                                tool_name = call.get("name", "tool")
                                label, action_text = TOOL_LABELS.get(tool_name, (f"🛠️ {tool_name}", "Executing tool..."))
                                status_box.write(f"**{label}**: {action_text}")
                                tool_count += 1
                        elif last_message.content:
                            final_answer = last_message.content

                    # 2. Capture Tool Execution Results
                    elif node == "tools":
                        for tool_msg in values.get("messages", []):
                            tool_name = tool_msg.name
                            label, _ = TOOL_LABELS.get(tool_name, (f"🛠️ {tool_name}", ""))
                            status_box.write(f"✓ Completed **{label}**")

            # Finalize status container
            if tool_count > 0:
                status_box.update(
                    label=f"Completed {tool_count} tool action{'s' if tool_count > 1 else ''}",
                    state="complete",
                    expanded=False
                )
            else:
                status_box.update(label="Response generated", state="complete", expanded=False)

            response_box.markdown(final_answer)

        except Exception as e:
            status_box.update(label="Execution error", state="error", expanded=True)
            final_answer = f"⚠️ System Error: {str(e)}"
            response_box.markdown(final_answer)

    st.session_state.messages.append({"role": "assistant", "content": final_answer})