# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (only what’s needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# (Optional) copy frontend only if backend serves it
# COPY frontend/ ./frontend/

# Set environment variables
ENV ENV=production
ENV DEBUG=false
ENV PYTHONPATH=/app

# Expose port for App Runner
EXPOSE 8000

# Drop root for security
RUN useradd -m appuser
USER appuser

# Start app with Uvicorn
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
