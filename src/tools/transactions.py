from langchain_core.tools import tool
from src.db.database import get_db_connection

@tool
def get_recent_transactions(account_id: str, limit: int = 5) -> str:
    """
    Fetches the most recent transactions for a given account ID.
    Use this when a user asks about their recent history, purchases, or deposits.
    """
    print(f"\n[System: Executing get_recent_transactions for {account_id}]")
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Fetch recent transactions ordered by newest first
                cursor.execute(
                    """
                    SELECT amount, type, description, timestamp 
                    FROM transactions 
                    WHERE account_id = %s 
                    ORDER BY timestamp DESC 
                    LIMIT %s
                    """, 
                    (account_id, limit)
                )
                results = cursor.fetchall()
                
                if not results:
                    return f"No recent transactions found for account {account_id}."
                
                # Format the results into a readable string for the LLM
                formatted_txns = []
                for row in results:
                    date_str = row['timestamp'].strftime("%Y-%m-%d")
                    amount = float(row['amount'])
                    formatted_txns.append(
                        f"[{date_str}] {row['type']} of ${amount:,.2f} - {row['description']}"
                    )
                
                return "\n".join(formatted_txns)
    except Exception as e:
        return f"System error fetching transactions for {account_id}: {str(e)}"