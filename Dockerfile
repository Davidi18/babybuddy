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
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt gunicorn

# Copy project files
COPY . /app/

# Create directories for data, static, and media
RUN mkdir -p /data /data/media /app/static /app/media && \
    chmod -R 755 /data /app/static /app/media

# Collect static files at BUILD time (not at container startup).
#
# Static assets are hashed (CompressedManifestStaticFilesStorage) and served
# with "Cache-Control: immutable". That is only safe if the hashed filename for
# a given asset is identical across every running container and every restart.
# Collecting here bakes one consistent, fully-hashed set into the image, so the
# CSS/JS URLs referenced by the HTML always exist and never change unless the
# asset itself changes. --clear removes any stale pre-built output first so the
# manifest contains exactly one hash per file.
ENV DJANGO_SETTINGS_MODULE=babybuddy.settings.base
RUN SECRET_KEY=build-time-collectstatic \
    python manage.py collectstatic --noinput --clear

# Make entrypoint executable
RUN chmod +x /app/docker-entrypoint.sh

# Expose port 8000
EXPOSE 8000

# Run the application using docker-entrypoint.sh
CMD ["/app/docker-entrypoint.sh"]
