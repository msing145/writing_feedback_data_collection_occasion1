# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Set environment variables for production
ENV ENV=production
ENV DEBUG=false
ENV PYTHONPATH=/app

# Create directory for SQLite database (matches backend/data/)
RUN mkdir -p /app/backend/data

# Expose port (App Runner will map this automatically)
EXPOSE 8000

# Run the application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]