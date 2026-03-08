#!/usr/bin/env python3
"""
One-time script to create an OpenAI vector store and upload the dbt study guide.
Run: uv run python setup_vector_store.py <path-to-study-guide.pdf>

Download the study guide from:
https://learn.getdbt.com/learn/article/analytics-engineering-exam-study-guide

Output: Prints vector_store_id to add to your .env file.
"""
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)
client = OpenAI()

if len(sys.argv) < 2:
    print("Usage: uv run python setup_vector_store.py <path-to-study-guide.pdf>")
    print("Download from: https://learn.getdbt.com/learn/article/analytics-engineering-exam-study-guide")
    sys.exit(1)

pdf_path = Path(sys.argv[1])
if not pdf_path.exists():
    print(f"File not found: {pdf_path}")
    sys.exit(1)

print("Creating vector store...")
vs = client.vector_stores.create(name="dbt-certification-study-guide")

print("Uploading study guide PDF...")
with open(pdf_path, "rb") as f:
    client.vector_stores.files.upload(vector_store_id=vs.id, file=f)

print("\nDone! Add this to your .env file:")
print(f"vector_store_id={vs.id}")
