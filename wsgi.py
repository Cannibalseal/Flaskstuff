"""
WSGI entry point for production deployment.
Used by Gunicorn, uWSGI, or Apache mod_wsgi.
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
