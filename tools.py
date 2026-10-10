from langchain_core.tools import tool

# Mock core banking database
MOCK_DB = {
    "account_123": 5500.00,
    "account_456": 120.50,
}

@tool
def get_balance(account_id: str) -> str:
    """Fetches the current account balance for a given account ID."""
    print(f"\n[System: Executing get_balance for {account_id}]")
    if account_id in MOCK_DB:
        return f"Balance for {account_id} is ${MOCK_DB[account_id]:.2f}"
    return f"Account {account_id} not found. Please verify the account ID."