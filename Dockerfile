# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.6
FROM python:${PYTHON_VERSION}-slim

# --------------------------------------------------
# Environment configuration
# --------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# --------------------------------------------------
# Create non-root user
# --------------------------------------------------
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# --------------------------------------------------
# Install dependencies
# --------------------------------------------------
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# --------------------------------------------------
# Copy application code
# --------------------------------------------------
COPY . .

# --------------------------------------------------
# Create writable ChromaDB directory
# --------------------------------------------------
RUN mkdir -p vector_db/chroma_db \
    && chown -R appuser:appuser vector_db

# Switch to non-root user
USER appuser

# --------------------------------------------------
# Expose port and run app
# --------------------------------------------------
EXPOSE 8000
CMD ["python", "app.py"]
