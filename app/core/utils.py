"""Utility functions for the Flask application.

Note: Email sending is now handled by Celery tasks in app/core/tasks.py
This file is kept for any future utility functions that don't need async processing.
"""

# Email functions have been moved to Celery background tasks
# See: app/core/tasks.py for:
#   - send_welcome_email_task (async welcome emails)
#   - send_article_notification_task (async article notifications)

# Add any synchronous utility functions here as needed

                continue
