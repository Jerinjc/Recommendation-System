"""
Evaluation module for SHL assessment recommender.

This script computes Recall@10 for each query in the labeled training
dataset and reports the mean Recall@10 across all queries.
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable, List, Set

# Add project root to Python path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from recommender.recommend import recommend  # noqa: E402

# URL normalization

def normalize_url(url: str) -> str:
    """
    Normalize SHL URLs for reliable comparison.

    This function removes protocol, domain differences, trailing slashes,
    and inconsistent path prefixes (e.g., '/solutions').

    Args:
        url (str): Original URL.

    Returns:
        str: Normalized URL string.
    """
    normalized = url.lower().strip()

    if "shl.com" in normalized:
        normalized = normalized.split("shl.com")[-1]

    normalized = normalized.replace("/solutions", "")
    normalized = normalized.rstrip("/")

    return normalized

# Recall@K metric

def recall_at_k(
    predicted_urls: List[str],
    relevant_urls: Iterable[str],
    k: int = 10,
    ) -> float:

    """
    Compute Recall@K for a single query.

    Args:
        predicted_urls (List[str]): Ranked list of predicted URLs.
        relevant_urls (Iterable[str]): Ground-truth relevant URLs.
        k (int): Cutoff rank.

    Returns:
        float: Recall@K score.
    """
    relevant_set: Set[str] = set(relevant_urls)

    if not relevant_set:
        return 0.0

    hits = len(set(predicted_urls[:k]) & relevant_set)
    return hits / len(relevant_set)


# Main evaluation logic

def main() -> None:
    """
    Run Recall@10 evaluation on the labeled training dataset.
    """
    csv_path = BASE_DIR / "evaluation" / "train.csv"

    # Step 1: Group relevant URLs by query
    ground_truth: defaultdict[str, Set[str]] = defaultdict(set)

    with open(csv_path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            query = row["Query"]
            url = normalize_url(row["Assessment_url"])
            ground_truth[query].add(url)

    print(f"Total unique queries: {len(ground_truth)}\n")

    # Step 2: Compute Recall@10 per query
    scores: List[float] = []

    for query, relevant_urls in ground_truth.items():
        results = recommend(query)

        predicted_urls = [
            normalize_url(result["url"]) for result in results
        ]

        score = recall_at_k(
            predicted_urls=predicted_urls,
            relevant_urls=relevant_urls,
            k=10,
        )
        scores.append(score)

        print(f"Query: {query}")
        print(f"Relevant assessments: {len(relevant_urls)}")
        print(f"Recall@10: {score:.2f}")
        print("-" * 60)

    # Step 3: Mean Recall@10
    mean_recall = sum(scores) / len(scores) if scores else 0.0

    print("=" * 60)
    print(f"Mean Recall@10: {mean_recall:.4f}")
    print("=" * 60)


if __name__ == "__main__":
    main()