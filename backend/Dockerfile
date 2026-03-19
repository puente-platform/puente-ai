# backend/Dockerfile

# Base image — slim keeps it small
FROM python:3.11-slim-bookworm

# Set working directory inside the container
WORKDIR /app

# Copy dependencies first (Docker layer caching)
# This layer only rebuilds when requirements.txt changes
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Copy environment handling
COPY .env* ./

# Tell the container which port to listen on
EXPOSE 8080

# Start the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
