"""SQLAlchemy models for mdblogs application."""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import re

db = SQLAlchemy()


class Article(db.Model):
    """Article model for blog posts."""
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text)
    content = db.Column(db.Text)
    published = db.Column(db.Integer, nullable=False, default=0, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Article {self.slug}>'
    
    def to_dict(self):
        """Convert article to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'slug': self.slug,
            'title': self.title,
            'summary': self.summary,
            'content': self.content,
            'published': bool(self.published),
            'date': self.created_at,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
        }
    
    @staticmethod
    def generate_slug(title, exclude_id=None):
        """Generate a unique slug from title."""
        base = re.sub(r"[^\w]+", "-", (title or '').lower()).strip('-')
        if not base:
            base = 'article'
        
        slug = base
        i = 1
        while True:
            query = Article.query.filter_by(slug=slug)
            if exclude_id:
                query = query.filter(Article.id != exclude_id)
            if not query.first():
                break
            i += 1
            slug = f"{base}-{i}"
        return slug


class User(db.Model):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Tag(db.Model):
    """Tag model for article categorization."""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Tag {self.name}>'


class ArticleTag(db.Model):
    """Many-to-many relationship between articles and tags."""
    __tablename__ = 'article_tags'
    
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id', ondelete='CASCADE'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)


class Comment(db.Model):
    """Comment model for article comments."""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False)
    author = db.Column(db.String(100))
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Comment {self.id} on Article {self.article_id}>'
