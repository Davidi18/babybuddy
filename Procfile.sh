#!/bin/bash

# Run database migrations
python manage.py migrate

# Collect static files (CSS, JS, images)
python manage.py collectstatic --noinput

# Create admin user from environment variables
python scripts/init_admin.py

# Start Gunicorn server
gunicorn babybuddy.wsgi:application --timeout 30 --log-file -