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

	# SQLite DB file used by mdblogs/database.py. Change path if desired.
	DATABASE = str(BASE_DIR / 'app.db')

	# Schema file path used to initialize the DB
	SCHEMA = str(BASE_DIR / 'mdblogs' / 'schema.sql')

	# Simple admin credentials used by the demo login handler.
	ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
	ADMIN_PASS = os.environ.get('ADMIN_PASS', 'password')

	# Development flags
	DEBUG = os.environ.get('FLASK_DEBUG', '1') == '1'


default_config = Config()
