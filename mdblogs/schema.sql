-- SQLite schema for the mdblogs sample site
-- Run with: sqlite3 app.db < mdblogs/schema.sql

PRAGMA foreign_keys = ON;

-- Users table: simple user store for admin/auth
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT (datetime('now'))
);

-- Articles table: store posts and basic metadata
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT,
    published INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
    updated_at DATETIME
);

CREATE INDEX IF NOT EXISTS idx_articles_slug ON articles(slug);
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published);

-- Tags and many-to-many relationship
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS article_tags (
    article_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (article_id, tag_id),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Comments (optional)
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    author TEXT,
    body TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

-- Example admin user insert (replace password hash with a real hash)
-- INSERT INTO users (username, password_hash, is_admin) VALUES ('admin', '<bcrypt-or-other-hash>', 1);

-- Example articles (uncomment to seed database):
-- INSERT INTO articles (slug, title, summary, content, published) VALUES
-- ('flask-quickstart', 'Flask Quickstart', 'A tiny guide to get a Flask app running.', '<p>Example content</p>', 1);

-- Vacuum and optimize hints
ANALYZE;
