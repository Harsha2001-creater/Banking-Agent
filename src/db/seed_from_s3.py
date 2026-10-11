import io
import os
import boto3
from pypdf import PdfReader
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.db.database import get_db_connection

load_dotenv()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-east-2"),
)

BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")

def load_pdf_from_s3(bucket: str, key: str) -> str:
    """Streams a PDF file from S3 into memory and extracts text."""
    response = s3_client.get_object(Bucket=bucket, Key=key)
    pdf_bytes = io.BytesIO(response["Body"].read())
    reader = PdfReader(pdf_bytes)

    full_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text.append(text)
    return "\n".join(full_text)

def seed_from_s3():
    print(f"Connecting to S3 bucket: {BUCKET_NAME}...")

    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix="policies/")
    contents = response.get("Contents", [])
    pdf_keys = [item["Key"] for item in contents if item["Key"].endswith(".pdf")]

    if not pdf_keys:
        print("No PDF files found in S3 bucket.")
        return

    print(f"Found {len(pdf_keys)} PDFs in S3. Initializing text splitter and embeddings...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " "]
    )
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # 1. Enable the pgvector extension for similarity search
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                
                # 2. Create the table capable of holding our 384-dimensional text embeddings
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS bank_policies (
                        id SERIAL PRIMARY KEY,
                        source_file TEXT,
                        content TEXT,
                        embedding VECTOR(384)
                    );
                """)
                cursor.execute("TRUNCATE bank_policies;")

                for key in pdf_keys:
                    s3_uri = f"s3://{BUCKET_NAME}/{key}"
                    print(f"Reading from S3: {s3_uri}")
                    raw_text = load_pdf_from_s3(BUCKET_NAME, key)

                    chunks = text_splitter.split_text(raw_text)
                    print(f"  Generated {len(chunks)} chunks. Vectorizing...")

                    for chunk in chunks:
                        vector = embeddings.embed_query(chunk)
                        
                        # 3. Insert the raw text alongside the vector embedding map
                        cursor.execute("""
                            INSERT INTO bank_policies (source_file, content, embedding)
                            VALUES (%s, %s, %s::vector)
                        """, (s3_uri, chunk, str(vector)))

                conn.commit()
                print("✅ Vectorization complete. All S3 documents indexed in pgvector.")
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    seed_from_s3()