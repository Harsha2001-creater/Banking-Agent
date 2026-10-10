import uuid
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from src.config.settings import get_llm
from src.tools.accounts import get_balance
from src.tools.transactions import get_recent_transactions
from src.tools.support import create_service_request

llm = get_llm(temperature=0.0)
tools = [get_balance, get_recent_transactions, create_service_request]
memory = MemorySaver()

# Removed the modifier argument entirely to avoid version crashes
agent = create_react_agent(llm, tools, checkpointer=memory)

system_prompt = """
You are an authorized autonomous Customer Support AI for a bank. 
You have permission to assist users with their accounts.

CRITICAL RULES FOR DISPUTES:
1. To open a dispute, you MUST know the exact merchant name and the exact transaction amount.
2. If you do not know the amount, DO NOT open the ticket. First, either ask the user for the amount, or use the get_recent_transactions tool to find the Whole Foods charge yourself.
3. ONLY AFTER you have confirmed the exact merchant and amount, use the create_service_request tool to open the ticket. Set request_type to 'DISPUTE'.
"""

if __name__ == "__main__":
    print("Banking Agent v6 (Persona Active). Type 'exit' to quit.\n")
    
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}
    
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ["exit", "quit"]:
            break
            
        # Inject the system prompt natively into the message list
        response = agent.invoke(
            {"messages": [("system", system_prompt), ("user", user_input)]}, 
            config=config
        )
        
        print(f"\nAgent: {response['messages'][-1].content}\n")