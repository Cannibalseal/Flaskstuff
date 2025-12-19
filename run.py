"""Application entry point."""

from app import create_app
from config import cfg

app = create_app()

if __name__ == '__main__':
    app.run(debug=cfg.DEBUG)
