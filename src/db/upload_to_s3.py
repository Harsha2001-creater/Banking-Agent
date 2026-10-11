import os
import boto3
from dotenv import load_dotenv

load_dotenv()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-east-2"),
)

BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")

def upload_corpus_to_s3(local_folder: str = "data/banking_corpus"):
    if not os.path.exists(local_folder):
        print(f"Directory {local_folder} does not exist.")
        return

    files = [f for f in os.listdir(local_folder) if f.endswith(".pdf")]
    print(f"Uploading {len(files)} PDFs to s3://{BUCKET_NAME}/...")

    for file_name in files:
        file_path = os.path.join(local_folder, file_name)
        s3_key = f"policies/{file_name}"

        try:
            s3_client.upload_file(file_path, BUCKET_NAME, s3_key)
            print(f"Uploaded: {file_name} -> s3://{BUCKET_NAME}/{s3_key}")
        except Exception as e:
            print(f"Failed to upload {file_name}: {e}")

    print("All uploads complete.")

if __name__ == "__main__":
    upload_corpus_to_s3()