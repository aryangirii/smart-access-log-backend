# Use official Python image
FROM python:3.9-slim

# Set environment variables to prevent Python from buffering output
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose Flask port
EXPOSE 5000

# Run with Gunicorn in production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
