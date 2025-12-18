from datetime import date

# Simple in-memory articles store. Keyed by slug for easy routing.
articles = {
    "flask-quickstart": {
        "id": 1,
        "title": "Flask Quickstart",
        "slug": "flask-quickstart",
        "summary": "A tiny guide to get a Flask app running.",
        "content": "<p>This article walks through creating a single-file Flask app, running it locally, and structuring simple templates.</p>",
        "date": date(2025, 1, 5),
    },
    "project-structure-tips": {
        "id": 2,
        "title": "Project Structure Tips",
        "slug": "project-structure-tips",
        "summary": "Small project layout suggestions for clarity and reuse.",
        "content": "<p>Keep templates, static, and small helper modules organized. Use a simple `database.py` for demo data.</p>",
        "date": date(2025, 2, 12),
    },
    "deploy-simple-app": {
        "id": 3,
        "title": "Deploying a Simple App",
        "slug": "deploy-simple-app",
        "summary": "Notes on lightweight deployment options for small Flask apps.",
        "content": "<p>Options include simple WSGI servers behind a reverse proxy, or using containers for portability.</p>",
        "date": date(2025, 3, 8),
    },
}


def get_all_articles():
    """Return articles as a list ordered by date descending."""
    return sorted(articles.values(), key=lambda a: a["date"], reverse=True)


def get_article(slug):
    return articles.get(slug)
