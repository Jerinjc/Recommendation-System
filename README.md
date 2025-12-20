# SHL Assessment Recommendation System

The below image shows a simple example of the recommendation system that I developed.

<img width="1709" height="858" alt="image" src="https://github.com/user-attachments/assets/85c495e5-6aac-4555-9d84-9a72a18becae" />

## Problem Overview and Approach

Hiring managers and recruiters often face difficulties in identifying the most suitable assessments for the roles they are hiring for. The existing process primarily relies on keyword-based searches and manual filtering, which can be time-consuming and inefficient. The goal of this project is to build an intelligent recommendation system that simplifies this workflow. Given a natural language hiring query, a job description (JD), or a URL containing a JD, the application returns a list of relevant SHL assessments from the product catalog.

The SHL product catalog available at  
https://www.shl.com/solutions/products/product-catalog/  
was used as the primary data source for this project.

---

## Data Collection and Preparation

The first step involved scraping the SHL product catalog using Selenium. A total of 377 assessment products were extracted from the website. For each product, relevant information such as the assessment name, URL, description, duration, test type, and delivery attributes were collected. Since detailed descriptions and durations were not available on the catalog listing pages, individual product pages were visited to extract these details.

During data inspection, it was observed that some product descriptions contained multilingual content, particularly French and other non-English language text. To handle this correctly and avoid encoding-related issues, the scraped dataset was saved using UTF-8 encoding with a Byte Order Mark (UTF-8-BOM). The final cleaned dataset was stored as a CSV file and used for downstream processing.

---

## Embedding and Vector Storage

Once the data was cleaned and structured, the assessment descriptions were transformed into vector representations using a large language model embedding. Each assessment description was embedded into a high-dimensional vector space and stored in a persistent ChromaDB vector database. This allowed the system to perform efficient semantic similarity searches rather than relying on keyword matching.

---

## Recommendation Pipeline

At query time, the user-provided hiring query or job description is converted into a vector embedding using the same embedding model. A vector similarity search is then performed against the stored assessment embeddings in ChromaDB. The most semantically relevant assessments are retrieved based on cosine similarity in the vector space. The recommendation results include the assessment name, URL, description, duration, test type, and delivery attributes.

---

## Evaluation Methodology

To evaluate the effectiveness of the recommendation system, Recall@10 was used as the primary evaluation metric. Given the small size of the labeled dataset provided by the organization, model predictions were limited; however, the system was still able to retrieve relevant assessments based on semantic similarity.

The labeled training dataset contained queries paired with relevant assessment URLs. For evaluation, the `assessment_url` column was excluded from the input during prediction to avoid data leakage, and only the query text was used. The predicted assessment URLs were then compared against the ground truth URLs to compute Recall@10 for each query. The final evaluation score was reported as the mean Recall@10 across all queries.

---

## Frontend and Deployment

After validating the recommendation performance, a minimal web frontend was developed using Flask. The application exposes REST endpoints using GET and POST methods, allowing users to submit queries and receive recommendations in JSON format. The frontend provides a simple browser-based interface for testing the system without requiring external tools such as Postman.

Finally, the entire application was containerized using Docker. A Docker image was created to ensure consistent deployment across environments, and environment variables (such as API keys) were securely managed using a `.env` file. This makes the system fully reproducible, portable, and ready for deployment or evaluation.

## Website

You can go and test this at http://98.93.97.149:8000/.
It works well, but I trained it on only 10 queries, so the output might not always be good, but it still generates based on the semantic relationship between the query and the products from the dataset rather than focusing on keyword or lexical searching.
