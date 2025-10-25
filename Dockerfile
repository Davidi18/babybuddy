# Baby Buddy - Dockerfile for Coolify/Production
# Based on Python 3.11

FROM python:3.11.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    gettext \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files
COPY . /app/

# Create directories for data, static, and media
RUN mkdir -p /data /app/static /app/media && \
    chmod -R 755 /data /app/static /app/media

# Expose port 8000
EXPOSE 8000

# Make Procfile.sh executable
RUN chmod +x /app/Procfile.sh

# Run the application using Procfile.sh
CMD ["bash", "/app/Procfile.sh"]
