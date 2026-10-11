import random
from faker import Faker
from datetime import datetime, timedelta
from src.db.database import get_db_connection

fake = Faker()

def seed_realistic_data():
    print("Connecting to AWS to expand schema and inject data...")
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # 1. Expand the schema (Add a new column)
                print("Adding 'category' column to transactions table...")
                cursor.execute("""
                    ALTER TABLE transactions 
                    ADD COLUMN IF NOT EXISTS category VARCHAR(50) DEFAULT 'Uncategorized';
                """)
                
                # 2. Delete the old 3 mock transactions so we have a clean slate
                cursor.execute("DELETE FROM transactions WHERE account_id = 'account_123'")
                
                # 3. Define realistic banking categories and merchants
                categories = {
                    "Groceries": ["Whole Foods", "Trader Joe's", "Kroger", "Safeway"],
                    "Dining": ["Starbucks", "Chipotle", "Local Steakhouse", "Uber Eats"],
                    "Utilities": ["PG&E", "Comcast", "Verizon", "Water Dept"],
                    "Entertainment": ["Netflix", "Spotify", "AMC Theaters", "Steam"],
                    "Shopping": ["Amazon", "Target", "Apple Store", "Walmart"]
                }

                # 4. Generate 50 randomized DEBIT transactions over the last 90 days
                print("Generating realistic debit history...")
                for _ in range(50):
                    cat = random.choice(list(categories.keys()))
                    merchant = random.choice(categories[cat])
                    # Generate a random amount between $5.00 and $150.00
                    amount = round(random.uniform(5.0, 150.0), 2) 
                    
                    # Generate a random date in the last 90 days
                    days_ago = random.randint(1, 90)
                    txn_date = datetime.now() - timedelta(days=days_ago)

                    cursor.execute("""
                        INSERT INTO transactions (account_id, amount, type, description, timestamp, category)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, ('account_123', amount, 'DEBIT', merchant, txn_date, cat))
                
                # 5. Generate 3 realistic bi-weekly CREDIT salary deposits
                print("Generating payroll deposits...")
                for i in [15, 45, 75]: # Days ago
                    salary_date = datetime.now() - timedelta(days=i)
                    cursor.execute("""
                        INSERT INTO transactions (account_id, amount, type, description, timestamp, category)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, ('account_123', 3200.00, 'CREDIT', 'TechCorp Payroll', salary_date, 'Income'))

                # Commit all 53 rows to AWS
                conn.commit()
                print("✅ Expanded schema and injected 53 realistic transactions successfully!")
    except Exception as e:
        print(f"❌ Error injecting data: {e}")

if __name__ == "__main__":
    seed_realistic_data()