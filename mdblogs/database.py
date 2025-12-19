"""Database-backed article helpers.

This module uses a local SQLite database file (app.db at the project root)
and `schema.sql` in the mdblogs folder to create required tables.
It also seeds a few sample articles if the articles table is empty.
"""

import os
import re
import sqlite3
from datetime import datetime
from configs import cfg


DB_PATH = os.path.expanduser(cfg.DATABASE)
if not os.path.isabs(DB_PATH):
    DB_PATH = os.path.abspath(DB_PATH)

SCHEMA_PATH = os.path.expanduser(cfg.SCHEMA)
if not os.path.isabs(SCHEMA_PATH):
    SCHEMA_PATH = os.path.abspath(SCHEMA_PATH)


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the database file and run the schema if needed."""
    parent = os.path.dirname(DB_PATH)
    if parent:
        os.makedirs(parent, exist_ok=True)
    # If schema file missing, nothing to do
    if not os.path.exists(SCHEMA_PATH):
        return
    # Execute schema script (creates tables if not exists)
    with sqlite3.connect(DB_PATH) as conn:
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            sql = f.read()
        conn.executescript(sql)
        # Enable WAL journaling to improve concurrency with external sqlite tools
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.commit()


def _seed_if_empty():
    """Insert sample articles if articles table is empty."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(1) as c FROM articles')
    row = cur.fetchone()
    if row and row['c'] == 0:
        samples = [
            ('flask-quickstart', 'Flask Quickstart', 'A tiny guide to get a Flask app running.', '<p>This article walks through creating a single-file Flask app, running it locally, and structuring simple templates.</p>', 1, '2025-01-05 00:00:00'),
            ('project-structure-tips', 'Project Structure Tips', 'Small project layout suggestions for clarity and reuse.', '<p>Keep templates, static, and small helper modules organized. Use a simple database.py for demo data.</p>', 1, '2025-02-12 00:00:00'),
            ('deploy-simple-app', 'Deploying a Simple App', 'Notes on lightweight deployment options for small Flask apps.', '<p>Options include simple WSGI servers behind a reverse proxy, or using containers for portability.</p>', 1, '2025-03-08 00:00:00'),
        ]
        cur.executemany(
            'INSERT INTO articles (slug, title, summary, content, published, created_at) VALUES (?, ?, ?, ?, ?, ?)', samples
        )
        conn.commit()
    conn.close()


def _row_to_article(row):
    if row is None:
        return None
    created = row['created_at']
    date_obj = None
    if created:
        try:
            date_obj = datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
        except Exception:
            try:
                date_obj = datetime.strptime(created.split('.')[0], '%Y-%m-%d %H:%M:%S')
            except Exception:
                date_obj = None
    return {
        'id': row['id'],
        'slug': row['slug'],
        'title': row['title'],
        'summary': row['summary'],
        'content': row['content'],
        'published': bool(row['published']),
        'date': date_obj,
    }


def get_all_articles():
    """Return published articles ordered by date descending as a list of dicts."""
    # ensure DB exists and seeded
    init_db()
    _seed_if_empty()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, slug, title, summary, content, published, created_at FROM articles WHERE published=1 ORDER BY created_at DESC")
    rows = cur.fetchall()
    articles = [_row_to_article(r) for r in rows]
    conn.close()
    return articles


def get_all_articles_admin():
    """Return all articles (published and unpublished) for admin view."""
    init_db()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, slug, title, summary, content, published, created_at FROM articles ORDER BY created_at DESC")
    rows = cur.fetchall()
    articles = [_row_to_article(r) for r in rows]
    conn.close()
    return articles


def get_article(slug):
    """Return a single article dict by slug, or None if not found."""
    init_db()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute('SELECT id, slug, title, summary, content, published, created_at FROM articles WHERE slug = ? LIMIT 1', (slug,))
    row = cur.fetchone()
    article = _row_to_article(row)
    conn.close()
    return article


def _generate_slug(title):
    base = re.sub(r"[^\w]+", "-", (title or '').lower()).strip('-')
    if not base:
        base = 'article'
    conn = _get_conn()
    cur = conn.cursor()
    slug = base
    i = 1
    while True:
        cur.execute('SELECT 1 FROM articles WHERE slug = ? LIMIT 1', (slug,))
        if not cur.fetchone():
            break
        i += 1
        slug = f"{base}-{i}"
    conn.close()
    return slug


def create_article(title, summary, content, published=0):
    """Insert a new article and return the created article dict."""
    init_db()
    slug = _generate_slug(title)
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO articles (slug, title, summary, content, published, created_at) VALUES (?, ?, ?, ?, ?, ?)',
        (slug, title, summary, content, int(published), created_at)
    )
    conn.commit()
    conn.close()
    article = get_article(slug)
    # Convert date to string for safer serialization
    if article and article.get('date'):
        article['date'] = article['date'].strftime('%Y-%m-%d %H:%M:%S')
    return article


def update_article(article_id, title, summary, content, published):
    """Update an existing article."""
    init_db()
    updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        'UPDATE articles SET title=?, summary=?, content=?, published=?, updated_at=? WHERE id=?',
        (title, summary, content, int(published), updated_at, article_id)
    )
    conn.commit()
    conn.close()
