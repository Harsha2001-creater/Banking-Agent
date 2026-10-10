import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from dotenv import load_dotenv, find_dotenv

# Search directory tree for .env
load_dotenv(find_dotenv())

DB_HOST = os.getenv("AWS_DB_HOST")
DB_NAME = os.getenv("AWS_DB_NAME", "postgres")
DB_USER = os.getenv("AWS_DB_USER", "postgres")
DB_PASSWORD = os.getenv("AWS_DB_PASSWORD")
DB_PORT = os.getenv("AWS_DB_PORT", "5432")

@contextmanager
def get_db_connection():
    """Context manager for AWS PostgreSQL database connections."""
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        sslmode="require",  # Required by AWS RDS
        cursor_factory=RealDictCursor # Returns rows as dictionaries
    )
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initializes the database schema and injects initial mock data."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # 1. Accounts Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    account_id VARCHAR(50) PRIMARY KEY,
                    user_id VARCHAR(50) NOT NULL,
                    balance NUMERIC(15, 2) NOT NULL,
                    kyc_status VARCHAR(20) DEFAULT 'PENDING'
                )
            ''')
            
            # 2. Transactions Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id SERIAL PRIMARY KEY,
                    account_id VARCHAR(50) REFERENCES accounts(account_id),
                    amount NUMERIC(15, 2) NOT NULL,
                    type VARCHAR(10) NOT NULL,
                    description TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 3. Service Requests Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS service_requests (
                    request_id SERIAL PRIMARY KEY,
                    user_id VARCHAR(50) NOT NULL,
                    request_type VARCHAR(50) NOT NULL,
                    status VARCHAR(20) DEFAULT 'OPEN',
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 4. Inject Mock Data for the Agent to find
            cursor.execute("SELECT COUNT(*) as count FROM accounts")
            if cursor.fetchone()['count'] == 0:
                cursor.execute("""
                    INSERT INTO accounts (account_id, user_id, balance, kyc_status) 
                    VALUES ('account_123', 'user_001', 5500.00, 'VERIFIED')
                """)
                print("Injected mock account_123 into the database.")
            
        conn.commit()
        print("✅ AWS PostgreSQL schema initialized successfully.")

if __name__ == "__main__":
    init_db()