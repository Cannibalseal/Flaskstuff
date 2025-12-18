"""Database-backed article helpers.

This module uses a local SQLite database file (app.db at the project root)
and `schema.sql` in the mdblogs folder to create required tables.
It also seeds a few sample articles if the articles table is empty.
"""

import os
import sqlite3
from datetime import datetime
from configs import cfg


DB_PATH = cfg.DATABASE
SCHEMA_PATH = cfg.SCHEMA


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the database file and run the schema if needed."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    # If schema file missing, nothing to do
    if not os.path.exists(SCHEMA_PATH):
        return
    # Execute schema script (creates tables if not exists)
    with sqlite3.connect(DB_PATH) as conn:
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            sql = f.read()
        conn.executescript(sql)


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
