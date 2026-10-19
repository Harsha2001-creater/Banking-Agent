import os
import uuid
from urllib.parse import quote_plus
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import create_react_agent

from src.config.settings import get_llm
from src.tools.accounts import get_balance
from src.tools.transactions import get_recent_transactions
from src.tools.support import create_service_request
from src.tools.knowledge import lookup_bank_policy

load_dotenv()

# Build RDS Connection URI with safe password escaping
user = os.getenv("AWS_DB_USER", "postgres")
password = quote_plus(os.getenv("AWS_DB_PASSWORD", ""))
host = os.getenv("AWS_DB_HOST")
port = os.getenv("AWS_DB_PORT", "5432")
dbname = os.getenv("AWS_DB_NAME", "postgres")

DB_URI = f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"

# Maintain an open connection pool for the agent lifecycle
pool = ConnectionPool(
    conninfo=DB_URI,
    max_size=10,
    kwargs={"autocommit": True, "prepare_threshold": 0}
)

checkpointer = PostgresSaver(pool)

llm = get_llm(temperature=0.0)

tools = [
    get_balance, 
    get_recent_transactions, 
    create_service_request, 
    lookup_bank_policy
]

# Replaces MemorySaver with persistent RDS checkpointer
agent = create_react_agent(llm, tools, checkpointer=checkpointer)

system_prompt = """
You are an authorized autonomous Customer Support AI for a bank. 
You have permission to assist users with their accounts.

CRITICAL RULES:
1. POLICY & REGULATION RETRIEVAL:
   - If a customer asks about rules, fees, interest rates, timelines, card replacement, or eligibility, use the `lookup_bank_policy` tool.
   - Ground your answer in the retrieved policy documents and cite the source file/S3 URI directly in your response.

2. SEARCH EXECUTION & ANTI-LOOP SAFEGUARDS:
   - NEVER call `lookup_bank_policy` more than TWO times for a single user query.
   - Do NOT run repetitive searches with slight wording changes.
   - If the retrieved excerpts do not explicitly contain the specific answer, STOP searching immediately. Provide the general requirements found in the documents or state clearly that the manual does not list specific details.

3. DISPUTE WORKFLOW:
   - To open a dispute, you MUST confirm the exact merchant name and the exact transaction amount.
   - If the user does not provide both, either ask for the missing details or call `get_recent_transactions` to locate the charge yourself.
   - Check the policy manual via `lookup_bank_policy` to verify dispute eligibility (e.g., standard 60-day limits or overdraft refund guidelines).
   - ONLY AFTER you have confirmed the merchant, the amount, and policy eligibility, call `create_service_request` with request_type='DISPUTE'.
"""

if __name__ == "__main__":
    print("Banking Agent v7 (AWS RDS Persistent State Active). Type 'exit' to quit.\n")
    
    session_id = input("Enter session/thread ID (or press Enter for new): ").strip()
    if not session_id:
        session_id = str(uuid.uuid4())
    print(f"Active Thread ID: {session_id}\n")
    
    config = {
        "configurable": {"thread_id": session_id},
        "recursion_limit": 50
    }
    
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ["exit", "quit"]:
            break
            
        response = agent.invoke(
            {"messages": [("system", system_prompt), ("user", user_input)]}, 
            config=config
        )
        
        print(f"\nAgent: {response['messages'][-1].content}\n")