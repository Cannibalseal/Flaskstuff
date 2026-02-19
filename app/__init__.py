"""Flask application factory."""

from flask import Flask
from app.core import mail, csrf
from app.models import db, Article, User, Newsletter, CustomPage
from config import cfg
import markdown
from markupsafe import Markup


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Secret key for session
    app.secret_key = cfg.SECRET_KEY
    
    # WTForms CSRF protection - more lenient settings
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # No time limit
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False  # Don't check on all requests
    app.config['WTF_CSRF_METHODS'] = ['POST', 'PUT', 'PATCH', 'DELETE']  # Only protect mutation methods
    
    # Load config values into Flask app.config
    app.config.from_object(cfg)
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize Flask-Mail
    mail.init_app(app)
    
    # Initialize CSRF Protection
    csrf.init_app(app)
    
    # Note: Using threading for background emails instead of Celery/Redis
    # See app/core/tasks.py for send_welcome_email_background() and send_article_notification_background()
    
    # Add markdown filter for templates
    @app.template_filter('markdown')
    def markdown_filter(text):
        """Convert markdown to HTML."""
        return Markup(markdown.markdown(text, extensions=['fenced_code', 'tables', 'nl2br']))
    
    # Create tables if needed
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from app.routes.public import public_bp
    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    
    # Register context processor for site settings
    from app.models import SiteSettings
    
    @app.context_processor
    def inject_site_settings():
        """Make site settings and custom pages available to all templates."""
        def get_settings_wrapper():
            """Wrapper to safely get settings with error handling."""
            try:
                return SiteSettings.get_settings()
            except Exception as e:
                # Return default settings if database error
                app.logger.error(f"Error loading site settings: {e}")
                return SiteSettings()
        
        def get_custom_pages():
            """Get all published custom pages for navigation."""
            try:
                return CustomPage.query.filter_by(is_published=True).all()
            except Exception as e:
                app.logger.error(f"Error loading custom pages: {e}")
                return []
        
        return {
            'get_site_settings': get_settings_wrapper,
            'custom_pages': get_custom_pages()
        }
    
    # Register error handlers
    from flask import render_template
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors with humor."""
        return render_template('errors/404.jinja'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors with humor."""
        db.session.rollback()  # Rollback any failed transactions
        return render_template('errors/500.jinja'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 errors with humor."""
        return render_template('errors/403.jinja'), 403
    
    @app.errorhandler(Exception)
    def generic_error(error):
        """Catch-all error handler."""
        import traceback
        app.logger.error(f"Unhandled exception: {error}")
        app.logger.error(traceback.format_exc())
        
        error_code = getattr(error, 'code', 500)
        error_message = str(error)
        
        # Rollback database on any error
        try:
            db.session.rollback()
        except Exception:
            pass
        
        return render_template('errors/generic.jinja', 
                             error_code=error_code,
                             error_message=error_message), error_code
    
    return app
