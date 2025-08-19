# Production Dockerfile for Snowflake Novel Generation Engine
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt1-dev \
    libzip-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY snowflake_guides/ ./snowflake_guides/
COPY *.txt ./

# Create artifacts directory
RUN mkdir -p artifacts

# Environment variables (to be overridden at runtime)
ENV ANTHROPIC_API_KEY=""
ENV OPENAI_API_KEY=""
ENV PYTHONPATH=/app
ENV ARTIFACTS_DIR=/app/artifacts

# Expose ports
EXPOSE 5000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/projects')" || exit 1

# Default command (can be overridden)
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]