# backend/Dockerfile

# Base image — slim keeps it small; pin major.minor only so rebuilds pick up patch updates.
FROM python:3.11-slim-bookworm

# Apply Debian security updates (base image layers can lag; scanners flag unfixed CVEs).
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /app

# Copy dependencies first (Docker layer caching)
# This layer only rebuilds when requirements.txt changes
COPY requirements.txt .

# Install deps, then upgrade pip/setuptools/wheel (requirements can pin older wheel; CVE-2026-24049 needs wheel>=0.46.2)
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --upgrade "pip>=25.3" "setuptools>=82.0.1" "wheel>=0.46.2"

# Copy application code
COPY app/ ./app/

# Copy environment handling
COPY .env* ./

# Tell the container which port to listen on
EXPOSE 8080

# Start the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
