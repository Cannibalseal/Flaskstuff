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


default_config = Config()
