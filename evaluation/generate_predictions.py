"""
Prediction generation module for SHL assessment recommender.

This script generates a submission-ready predictions CSV by running the
recommender once per unique query in the test dataset.
"""

import csv
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Dict

# Add project root to Python path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from recommender.recommend import recommend  # noqa: E402

# Main prediction logic

def main() -> None:
    """
    Generate predictions.csv for submission.

    The test dataset may contain duplicate queries and assessment URLs.
    This script ensures that the recommender is run once per unique query
    and outputs top-ranked assessment URLs for each query.
    """
    input_csv = BASE_DIR / "evaluation" / "test.csv"
    output_csv = BASE_DIR / "evaluation" / "predictions.csv"

    # Step 1: Collect unique queries (preserve order)
    unique_queries: Dict[str, bool] = OrderedDict()

    with open(input_csv, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            query = row["Query"]
            unique_queries[query] = True

    print(f"Unique queries found: {len(unique_queries)}")

    # Step 2: Generate predictions
    with open(output_csv, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)

        # Required submission header
        writer.writerow(["Query", "Assessment_url"])

        for query in unique_queries:
            results = recommend(query)

            for result in results:
                writer.writerow([query, result["url"]])

    print("predictions.csv generated successfully")
    print(f"Location: {output_csv}")


if __name__ == "__main__":
    main()