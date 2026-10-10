from src.db.database import get_db_connection

def seed_transactions():
    """Injects sample transaction data for testing."""
    print("Connecting to AWS to inject mock transactions...")
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Check if transactions already exist to prevent duplicates if run twice
                cursor.execute("SELECT COUNT(*) as count FROM transactions WHERE account_id = 'account_123'")
                if cursor.fetchone()['count'] == 0:
                    cursor.execute("""
                        INSERT INTO transactions (account_id, amount, type, description)
                        VALUES 
                        ('account_123', 3200.00, 'CREDIT', 'Employer Salary Deposit'),
                        ('account_123', 145.50, 'DEBIT', 'Whole Foods Market'),
                        ('account_123', 85.00, 'DEBIT', 'Verizon Wireless Bill')
                    """)
                    conn.commit()
                    print("✅ Mock transactions injected successfully for account_123.")
                else:
                    print("⚠️ Transactions already exist. Skipping injection to prevent duplicates.")
    except Exception as e:
        print(f"❌ Error injecting transactions: {e}")

if __name__ == "__main__":
    seed_transactions()