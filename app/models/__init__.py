"""SQLAlchemy models for mdblogs application."""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
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
    
    # Author relationship
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    author = db.relationship('User', backref='articles', foreign_keys=[author_id])
    
    # Relationships for comments and likes
    comments = db.relationship('Comment', backref='article', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='article', lazy='dynamic', cascade='all, delete-orphan')
    
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
            'author': self.author.to_dict() if self.author else None,
            'comments_count': self.comments.count(),
            'likes_count': self.likes.count(),
        }
    
    def get_likes_count(self):
        """Get the number of likes for this article."""
        return self.likes.count()
    
    def get_comments_count(self):
        """Get the number of comments for this article."""
        return self.comments.filter_by(approved=True).count()
    
    def is_liked_by(self, user_id):
        """Check if a user has liked this article."""
        return self.likes.filter_by(user_id=user_id).first() is not None
    
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
    must_change_password = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Profile fields
    display_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    bio = db.Column(db.Text)
    profile_picture = db.Column(db.String(200))  # Filename or URL
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    twitter = db.Column(db.String(100))
    github = db.Column(db.String(100))
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name or self.username,
            'email': self.email,
            'bio': self.bio,
            'profile_picture': self.profile_picture,
            'location': self.location,
            'website': self.website,
            'twitter': self.twitter,
            'github': self.github,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class Tag(db.Model):
    """Tag model for article categorization."""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Tag {self.name}>'


class Newsletter(db.Model):
    """Newsletter subscriber model."""
    __tablename__ = 'newsletter'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    subscribed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Integer, nullable=False, default=1)
    
    def __repr__(self):
        return f'<Newsletter {self.email}>'


class Comment(db.Model):
    """Comment model for article comments."""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    approved = db.Column(db.Boolean, nullable=False, default=True)
    
    # Foreign keys
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='comments', foreign_keys=[user_id])
    
    def __repr__(self):
        return f'<Comment {self.id} by User {self.user_id}>'
    
    def to_dict(self):
        """Convert comment to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'user': {
                'username': self.user.username,
                'display_name': self.user.display_name or self.user.username,
                'profile_picture': self.user.profile_picture,
            } if self.user else None,
            'approved': self.approved,
        }


class Like(db.Model):
    """Like model for article likes."""
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Foreign keys
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='likes', foreign_keys=[user_id])
    
    # Unique constraint to prevent duplicate likes
    __table_args__ = (db.UniqueConstraint('article_id', 'user_id', name='unique_article_like'),)
    
    def __repr__(self):
        return f'<Like article={self.article_id} user={self.user_id}>'
