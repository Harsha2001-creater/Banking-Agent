from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from src.db.database import get_db_connection

# Initialize the embedding model globally
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

@tool
def lookup_bank_policy(search_query: str) -> str:
    """
    Searches the official banking knowledge base stored in AWS S3 and indexed in PostgreSQL.
    Use this tool before answering questions regarding fees, dispute rules, timelines, or regulations.
    """
    print(f"\n[System: Querying S3-backed pgvector knowledge base for: '{search_query}']")

    try:
        query_vector = embeddings.embed_query(search_query)

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # The <=> operator computes cosine similarity directly in PostgreSQL
                cursor.execute(
                    """
                    SELECT source_file, content 
                    FROM bank_policies 
                    ORDER BY embedding <=> %s::vector 
                    LIMIT 3
                    """,
                    (str(query_vector),)
                )
                results = cursor.fetchall()

                if not results:
                    return "No matching policies found in the knowledge base."

                formatted = []
                for row in results:
                    formatted.append(f"Source ({row['source_file']}):\n{row['content']}")

                return "Official Policy Documents:\n\n" + "\n\n".join(formatted)

    except Exception as e:
        return f"System error searching policies: {str(e)}"