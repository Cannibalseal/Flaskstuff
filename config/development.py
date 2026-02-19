import os
from pathlib import Path

# Project base directory
BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = True

# SQLAlchemy configuration
SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR / "app.db"}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
