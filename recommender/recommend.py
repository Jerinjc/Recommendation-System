"""
Recommendation module for SHL assessment retrieval.

This module performs semantic retrieval of SHL assessments using a
persistent vector store and returns the most relevant results based
on vector similarity.
"""

import os
from pathlib import Path
from typing import Dict, List

import chromadb
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore


# Environment setup

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError("GOOGLE_API_KEY missing from environment variables.")


# Paths and embedding model

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_PATH = BASE_DIR / "vector_db" / "chroma_db"

EMBED_MODEL = GoogleGenAIEmbedding(
    model_name="models/text-embedding-004"
)

# Vector store and index

chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
collection = chroma_client.get_or_create_collection("shl_assessments")

vector_store = ChromaVectorStore(chroma_collection=collection)

index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    embed_model=EMBED_MODEL,
)

retriever = index.as_retriever(
    similarity_top_k=10,
    similarity_cutoff=0.0,
)

# Public API

def recommend(query: str, max_results: int = 10) -> List[Dict[str, str]]:
    """
    Retrieve SHL assessments relevant to a given query.

    Assessments are retrieved purely using semantic vector similarity
    between the query and assessment descriptions.

    Args:
        query (str): Job description or natural language query.
        max_results (int): Maximum number of recommendations to return.

    Returns:
        List[Dict[str, str]]: List of assessment metadata dictionaries.
    """
    nodes = retriever.retrieve(query)

    recommendations: List[Dict[str, str]] = []

    for node in nodes:
        metadata = dict(node.metadata)
        metadata["description"] = node.get_text()
        recommendations.append(metadata)

    return recommendations[:max_results]