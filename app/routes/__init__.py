"""Routes package - blueprint registration."""

from app.routes.public import public_bp
from app.routes.admin import admin_bp
from app.routes.auth import auth_bp
from app.routes.profile import profile_bp

__all__ = ['public_bp', 'admin_bp', 'auth_bp', 'profile_bp']
