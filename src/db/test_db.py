import psycopg2
import os
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.abspath(os.path.join(current_dir, "../../.env"))
load_dotenv(dotenv_path=env_path)

def test_connection():
    db_host = os.getenv("AWS_DB_HOST")
    
    print(f"Attempting to connect to AWS RDS at {db_host}...")
    try:
        conn = psycopg2.connect(
            host=db_host,
            database=os.getenv("AWS_DB_NAME", "postgres"),
            user=os.getenv("AWS_DB_USER", "postgres"),
            password=os.getenv("AWS_DB_PASSWORD"),
            port=os.getenv("AWS_DB_PORT", "5432"),
            connect_timeout=10,
            sslmode="require"  # <-- Added to enforce encrypted connection
        )
        print("✅ Successfully connected to AWS PostgreSQL!")
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()