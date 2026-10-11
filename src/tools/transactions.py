from langchain_core.tools import tool
from src.db.database import get_db_connection

@tool
def get_recent_transactions(account_id: str, limit: int = 20) -> str:
    """
    Fetches the most recent transactions for a given account ID.
    Use this when a user asks about their recent history, purchases, spending habits, or deposits.
    """
    print(f"\n[System: Executing get_recent_transactions for {account_id}]")
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Include the new 'category' column in our SQL query
                cursor.execute(
                    """
                    SELECT amount, type, description, category, timestamp 
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
                
                formatted_txns = []
                for row in results:
                    date_str = row['timestamp'].strftime("%Y-%m-%d")
                    amount = float(row['amount'])
                    # Inject the new category into the text string the LLM reads
                    formatted_txns.append(
                        f"[{date_str}] {row['type']} of ${amount:,.2f} at {row['description']} (Category: {row['category']})"
                    )
                
                return "\n".join(formatted_txns)
    except Exception as e:
        return f"System error fetching transactions for {account_id}: {str(e)}"