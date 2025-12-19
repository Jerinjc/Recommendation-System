# SHL Assessment Recommendation System

This project implements a semantic recommendation system that suggests relevant SHL assessments based on a natural-language hiring query or job description. The system uses vector embeddings and similarity search to retrieve assessments from the SHL product catalog and exposes the recommendations through a REST API and a minimal web interface.

---

## Overview

The solution is designed as an API-first application with an optional browser-based frontend for easy testing. Each assessment in the catalog is embedded using a large language model embedding, stored in a persistent vector database, and retrieved at query time using semantic similarity. The system is evaluated using Recall@10 on a labeled dataset provided as part of the assignment.

---

## Architecture

- **Embedding & Retrieval**  
  Assessment descriptions are embedded using Google Gemini embeddings and stored in a persistent ChromaDB vector store. User queries are embedded at runtime and matched against the stored vectors using semantic similarity.

- **Backend Service**  
  A Flask application exposes REST endpoints for health checks and assessment recommendations.

- **Frontend**  
  A minimal HTML frontend allows users to enter queries in a browser and view recommended assessments.

- **Evaluation**  
  Offline evaluation is performed using Recall@10 on the labeled training dataset, with proper handling of multi-label relevance.

- **Deployment**  
  The application is containerized using Docker and can be run locally or deployed to a cloud platform.
  
---

## Environment Setup

Create a `.env` file in the project root with the following content:

```env```
GOOGLE_API_KEY=your_google_api_key_here

## Installation (Local)

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

## Running the Application (Local)
python app.py


The service will start on port 8000.

## API Endpoints

Health Check
GET /health


Response:

{
  "status": "healthy"
}

## Assessment Recommendation
POST /recommend
Content-Type: application/json


Request body:

{
  "query": "I am hiring for Java developers"
}


Response:

{
  "recommended_assessments": [
    {
      "name": "...",
      "url": "...",
      "description": "...",
      "duration": 0,
      "adaptive_support": "No",
      "remote_support": "Yes",
      "test_type": ["Knowledge & Skills"]
    }
  ]
}

## Web Frontend

A minimal browser-based frontend is available at:

http://localhost:8000/


This interface allows users to enter a query and view recommended assessments without using Postman or curl.

## Evaluation

The system is evaluated using Recall@10 on the labeled training dataset.

To run the evaluation:

python evaluation/evaluate.py


The script groups relevant assessment URLs by query, computes Recall@10 per query, and reports the mean Recall@10 across all queries. Evaluation data is used strictly for validation and does not influence recommendation logic.

Docker Usage
Build the Docker image
docker build -t shl-assessment .

Run the container
docker run --env-file .env -p 8000:8000 shl-assessment


The application will be available at:

Frontend: http://localhost:8000/

API: http://localhost:8000/recommend

The recommendation system relies purely on semantic similarity and does not use hard-coded rules.
Labeled datasets are used only for evaluation and iteration, not for training.
The system is fully reproducible and containerized.

