from langchain_core.tools import tool
from src.db.database import get_db_connection

@tool
def get_balance(account_id: str) -> str:
    """
    Fetches the current account balance and KYC status for a given account ID.
    Always use this tool when a user asks for their balance.
    """
    print(f"\n[System: Executing get_balance for {account_id}]")
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # PostgreSQL uses %s for parameterized queries to prevent SQL injection
                cursor.execute(
                    "SELECT balance, kyc_status FROM accounts WHERE account_id = %s", 
                    (account_id,)
                )
                result = cursor.fetchone()
                
                if result:
                    # Format the balance with commas for readability (e.g., $5,500.00)
                    balance = float(result['balance'])
                    kyc_status = result['kyc_status']
                    return f"Balance for {account_id} is ${balance:,.2f}. (KYC Status: {kyc_status})"
                else:
                    return f"Account {account_id} not found. Please verify the account ID."
    except Exception as e:
        return f"System error fetching balance for {account_id}: {str(e)}"