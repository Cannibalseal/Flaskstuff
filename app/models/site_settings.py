"""Site settings model for admin customization."""
from app.models import db
from datetime import datetime


class SiteSettings(db.Model):
    """Model for storing site-wide customization settings."""
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Site Identity
    site_name = db.Column(db.String(100), default='My Blog')
    site_tagline = db.Column(db.String(200), default='Welcome to our community')
    site_description = db.Column(db.Text, default='A place for sharing ideas')
    
    # Page Content (HTML supported)
    welcome_page_content = db.Column(db.Text, default='<h1>Welcome!</h1><p>This is the welcome page.</p>')
    about_page_content = db.Column(db.Text, default='<h1>About Us</h1><p>Learn more about us here.</p>')
    footer_content = db.Column(db.Text, default='<p>&copy; 2025 My Blog. All rights reserved.</p>')
    
    # Custom Styling
    custom_css = db.Column(db.Text, default='/* Add your custom CSS here */')
    custom_js = db.Column(db.Text, default='// Add your custom JavaScript here')
    
    # SEO Settings
    meta_keywords = db.Column(db.String(500), default='blog, articles, community')
    meta_description = db.Column(db.String(500), default='A community blog platform')
    
    # Social Media
    site_twitter = db.Column(db.String(100))
    site_github = db.Column(db.String(100))
    site_email = db.Column(db.String(100))
    
    # Appearance
    primary_color = db.Column(db.String(20), default='#06b6d4')
    secondary_color = db.Column(db.String(20), default='#8b5cf6')
    logo_path = db.Column(db.String(255))
    favicon_path = db.Column(db.String(255))
    
    # Features Toggle
    enable_comments = db.Column(db.Boolean, default=True)
    enable_likes = db.Column(db.Boolean, default=True)
    enable_newsletter = db.Column(db.Boolean, default=True)
    enable_social_sharing = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SiteSettings {self.site_name}>'
    
    @staticmethod
    def get_settings():
        """Get or create site settings."""
        try:
            settings = SiteSettings.query.first()
            if not settings:
                # Create default settings
                settings = SiteSettings(
                    site_name='My Blog',
                    site_tagline='Welcome to our community',
                    site_description='A place for sharing ideas',
                    welcome_page_content='<h1>Welcome!</h1><p>This is the welcome page.</p>',
                    about_page_content='<h1>About Us</h1><p>Learn more about us here.</p>',
                    footer_content='<p>&copy; 2025 My Blog. All rights reserved.</p>',
                    custom_css='/* Add your custom CSS here */',
                    custom_js='// Add your custom JavaScript here',
                    meta_keywords='blog, articles, community',
                    meta_description='A community blog platform',
                    primary_color='#06b6d4',
                    secondary_color='#8b5cf6',
                    enable_comments=True,
                    enable_likes=True,
                    enable_newsletter=True,
                    enable_social_sharing=True
                )
                db.session.add(settings)
                db.session.commit()
            return settings
        except Exception as e:
            # If database error, return default settings object (not saved to DB)
            db.session.rollback()
            return SiteSettings(
                site_name='My Blog',
                site_tagline='Welcome to our community',
                site_description='A place for sharing ideas',
                welcome_page_content='<h1>Welcome!</h1><p>This is the welcome page.</p>',
                about_page_content='<h1>About Us</h1><p>Learn more about us here.</p>',
                footer_content='<p>&copy; 2025 My Blog. All rights reserved.</p>',
                custom_css='',
                custom_js='',
                meta_keywords='blog, articles, community',
                meta_description='A community blog platform',
                primary_color='#06b6d4',
                secondary_color='#8b5cf6',
                enable_comments=True,
                enable_likes=True,
                enable_newsletter=True,
                enable_social_sharing=True
            )
