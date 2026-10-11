import uuid
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from src.config.settings import get_llm
from src.tools.accounts import get_balance
from src.tools.transactions import get_recent_transactions
from src.tools.support import create_service_request
from src.tools.knowledge import lookup_bank_policy  # <-- Added RAG tool

llm = get_llm(temperature=0.0)

# Added lookup_bank_policy to the agent's toolset
tools = [
    get_balance, 
    get_recent_transactions, 
    create_service_request, 
    lookup_bank_policy
]

memory = MemorySaver()

# Initialize the ReAct agent with all 4 tools
agent = create_react_agent(llm, tools, checkpointer=memory)

system_prompt = """
You are an authorized autonomous Customer Support AI for a bank. 
You have permission to assist users with their accounts.

CRITICAL RULES:
1. POLICY & REGULATION RETRIEVAL:
   - If a customer asks about rules, fees, interest rates, timelines, card replacement, or eligibility, ALWAYS call the `lookup_bank_policy` tool first.
   - Ground your answer in the retrieved policy documents and cite the source file/S3 URI directly in your response.

2. DISPUTE WORKFLOW:
   - To open a dispute, you MUST confirm the exact merchant name and the exact transaction amount.
   - If the user does not provide both, either ask for the missing details or call `get_recent_transactions` to locate the charge yourself.
   - Check the policy manual via `lookup_bank_policy` to verify dispute eligibility (e.g., standard 60-day limits or overdraft refund guidelines).
   - ONLY AFTER you have confirmed the merchant, the amount, and policy eligibility, call `create_service_request` with request_type='DISPUTE'.
"""

if __name__ == "__main__":
    print("Banking Agent v6 (RAG + S3 Knowledge Active). Type 'exit' to quit.\n")
    
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}
    
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ["exit", "quit"]:
            break
            
        # Inject the system prompt alongside the user turn
        response = agent.invoke(
            {"messages": [("system", system_prompt), ("user", user_input)]}, 
            config=config
        )
        
        print(f"\nAgent: {response['messages'][-1].content}\n")