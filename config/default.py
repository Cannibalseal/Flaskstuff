import os
from pathlib import Path

# Project base directory (one level up from configs/)
BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
	"""Default configuration values for the Flask project.

	Override any of these using environment variables in production.
	"""

	# Secret for sessions and signing. Override with FLASK_SECRET in env.
	SECRET_KEY = os.environ.get('FLASK_SECRET', 'dev-secret')

	# SQLAlchemy configuration
	SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR / "app.db"}'
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# Simple admin credentials used by the demo login handler.
	ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
	ADMIN_PASS = os.environ.get('ADMIN_PASS', 'password')

	# Development flags
	DEBUG = os.environ.get('FLASK_DEBUG', '1') == '1'

	# Flask-Mail configuration
	MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
	MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
	MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', '1') == '1'
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
	MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@yourblog.com')

	# Celery configuration
	CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
	CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
	CELERY_TASK_SERIALIZER = 'json'
	CELERY_RESULT_SERIALIZER = 'json'
	CELERY_ACCEPT_CONTENT = ['json']
	CELERY_TIMEZONE = 'UTC'
	CELERY_ENABLE_UTC = True


default_config = Config()
