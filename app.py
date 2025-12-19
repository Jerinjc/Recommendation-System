"""
Flask application for SHL assessment recommendation.

This service exposes REST endpoints to retrieve SHL assessment
recommendations based on a natural language query.
"""

import os
from typing import Dict, Any
from flask import render_template
from flask import Flask, jsonify, request
from dotenv import load_dotenv

from recommender.recommend import recommend

# Environment setup

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError("GOOGLE_API_KEY missing from environment variables.")

# Flask application

app = Flask(__name__)
print("RUNNING SHL RECOMMENDER APP ...")

@app.route("/", methods=["GET"])
def home():
    """
    Render the frontend UI.
    """
    return render_template("index.html")

# Health check endpoint

@app.route("/health", methods=["GET"])
def health() -> tuple[Dict[str, str], int]:
    """
    Health check endpoint.

    Returns:
        tuple: JSON response with status and HTTP status code.
    """
    return jsonify({"status": "healthy"}), 200

# Recommendation endpoint

@app.route("/recommend", methods=["POST"])
def recommend_endpoint() -> tuple[Dict[str, Any], int]:
    """
    Generate SHL assessment recommendations.

    Expects a JSON payload with a 'query' field.

    Returns:
        tuple: JSON response containing recommended assessments and
        HTTP status code.
    """
    data = request.get_json(silent=True)

    if not data or "query" not in data:
        return jsonify({"error": "Missing 'query' field"}), 400

    query = data["query"].strip()
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    results = recommend(query)

    response: Dict[str, Any] = {
        "recommended_assessments": []
    }

    for result in results[:10]:
        response["recommended_assessments"].append(
            {
                "url": result.get("url"),
                "name": result.get("name"),
                "adaptive_support": result.get("adaptive_support"),
                "description": result.get("description"),
                "duration": result.get("duration"),
                "remote_support": result.get("remote_support"),
                "test_type": (
                    result["test_type"]
                    if isinstance(result.get("test_type"), list)
                    else [result.get("test_type")]
                ),
            }
        )

    return jsonify(response), 200


# Local execution

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
