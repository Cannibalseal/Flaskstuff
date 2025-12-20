"""Core utilities and extensions for the Flask application."""

from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
mail = Mail()
csrf = CSRFProtect()

__all__ = ['mail', 'csrf']
