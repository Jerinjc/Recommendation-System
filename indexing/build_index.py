"""Module to build a persistent vector index for SHL assessments.

This module handles the ingestion of assessment data from a CSV file, cleans the 
content, and stores vector embeddings in a persistent ChromaDB instance using 
LlamaIndex and Google GenAI.
"""

import os
from pathlib import Path

import pandas as pd
import chromadb
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Document, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding


# Load environment variables
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError("GOOGLE_API_KEY missing from environment")

# Initialize stable embedding model
embed_model = GoogleGenAIEmbedding(
    model_name="models/text-embedding-004"
)

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_PATH = BASE_DIR / "vector_db" / "chroma_db"

# Set up persistent ChromaDB storage
chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
collection = chroma_client.get_or_create_collection("shl_assessments")
vector_store = ChromaVectorStore(chroma_collection=collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)


def build_index():
    """Build and persist the vector index if it does not already exist.

    This function reads assessment data from a local CSV, transforms each row
    into a Document object with relevant metadata, and utilizes a
    VectorStoreIndex to generate and store embeddings.
    """
    if collection.count() > 0:
        print("Index already exists. Skipping build process.")
        return

    # Using raw string for Windows paths to avoid escape sequence issues
    csv_path = r"C:\Jerin\SHL\scraper\shl_assessments.csv"
    
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_path}")
        return

    documents = []

    for _, row in df.iterrows():
        # Clean data and prepare document metadata
        doc_metadata = {
            "name": row["name"],
            "url": row["url"],
            "test_type": row["test_type"],
            "duration": int(row["duration"]),
            "adaptive_support": row["adaptive_support"],
            "remote_support": row["remote_support"],
        }

        documents.append(
            Document(
                text=str(row["description"]),
                metadata=doc_metadata
            )
        )

    # Generate the index and store it in the persistent vector store
    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model
    )

    print(f"Successfully indexed {len(documents)} assessments.")


if __name__ == "__main__":
    build_index()