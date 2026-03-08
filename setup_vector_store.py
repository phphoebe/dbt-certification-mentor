#!/usr/bin/env python3
"""
One-time script to create an OpenAI vector store and upload the dbt study guide.
Run from project root: uv run python setup_vector_store.py

Output: Prints vector_store_id to add to your .env file.
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)
client = OpenAI()

# Path to study guide (relative to Assignments root)
ASSIGNMENTS_ROOT = Path(__file__).parent.parent.parent
STUDY_GUIDE = ASSIGNMENTS_ROOT / "Instructions" / "week-2" / "Resources"
PDF_NAME = "dbt_Certificate Study Guide_Analytics_Engineer_Developer.pdf"
pdf_path = STUDY_GUIDE / PDF_NAME

if not pdf_path.exists():
    print(f"Expected PDF at: {pdf_path}")
    print("Please download the study guide and place it there, or edit this script.")
    exit(1)

print("Creating vector store...")
vs = client.vector_stores.create(name="dbt-certification-study-guide")

print("Uploading study guide PDF...")
with open(pdf_path, "rb") as f:
    client.vector_stores.files.upload(vector_store_id=vs.id, file=f)

print("\nDone! Add this to your .env file:")
print(f"vector_store_id={vs.id}")
