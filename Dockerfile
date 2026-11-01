FROM python:3.11-slim

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Ensure upload and frames cache directories exist
RUN mkdir -p /app/data/uploads /app/data/frames

# Dynamic port binding (Render, Hugging Face Spaces, Railway, Koyeb)
ENV PORT=8000
EXPOSE 8000

# Start Uvicorn bound to 0.0.0.0
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

