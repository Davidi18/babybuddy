import os
from django.core.wsgi import get_wsgi_application

from dotenv import load_dotenv, find_dotenv

# Environment variables
# Check for and load environment variables from a .env file.
load_dotenv(find_dotenv())

# Set default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "babybuddy.settings.base")

application = get_wsgi_application()
