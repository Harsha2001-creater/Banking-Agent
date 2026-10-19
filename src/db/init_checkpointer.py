import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver

load_dotenv()

def get_postgres_uri() -> str:
    user = os.getenv("AWS_DB_USER", "postgres")
    password = quote_plus(os.getenv("AWS_DB_PASSWORD", ""))
    host = os.getenv("AWS_DB_HOST")
    port = os.getenv("AWS_DB_PORT", "5432")
    dbname = os.getenv("AWS_DB_NAME", "postgres")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"

def setup_checkpoint_tables():
    uri = get_postgres_uri()
    print("Connecting to AWS RDS to initialize LangGraph checkpoint tables...")
    
    with ConnectionPool(conninfo=uri, max_size=5, kwargs={"autocommit": True}) as pool:
        checkpointer = PostgresSaver(pool)
        checkpointer.setup()
        print("✅ Checkpoint tables provisioned successfully in AWS RDS!")

if __name__ == "__main__":
    setup_checkpoint_tables()