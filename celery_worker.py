"""Celery worker entry point."""

from app import create_app

# Create Flask app
flask_app = create_app()

# Get Celery instance
from app import celery

# This allows running: celery -A celery_worker worker
