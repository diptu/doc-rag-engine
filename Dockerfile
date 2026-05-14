# Use a slim Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# 1. Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic-dev \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# 2. COPY THE FILE FIRST
COPY requirements.txt .

# 3. NOW INSTALL
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir mkdocs

# Copy project files
COPY . .

# Expose API port and MkDocs port
EXPOSE 8000
EXPOSE 8001

# Run both the API and MkDocs server
# We use & to run mkdocs in the background and uvicorn in the foreground
CMD mkdocs serve -a 0.0.0.0:8000 & uvicorn app.main:app --host 0.0.0.0 --port 8001