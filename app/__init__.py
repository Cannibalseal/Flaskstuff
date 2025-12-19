"""Flask application factory."""

from flask import Flask
from app.models import db, Article, User
from config import cfg


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Secret key for session
    app.secret_key = cfg.SECRET_KEY
    
    # WTForms CSRF protection
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = None
    
    # Load config values into Flask app.config
    app.config.from_object(cfg)
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Create tables and seed data if needed
    with app.app_context():
        db.create_all()
        
        # Create default admin user if users table is empty
        if User.query.count() == 0:
            admin = User(
                username=cfg.ADMIN_USER,
                is_admin=1,
                must_change_password=1
            )
            admin.set_password(cfg.ADMIN_PASS)
            db.session.add(admin)
            db.session.commit()
        
        # Seed sample data if articles table is empty
        if Article.query.count() == 0:
            samples = [
                Article(slug='flask-quickstart', title='Flask Quickstart', 
                       summary='A tiny guide to get a Flask app running.', 
                       content='<p>This article walks through creating a single-file Flask app, running it locally, and structuring simple templates.</p>', 
                       published=1),
                Article(slug='project-structure-tips', title='Project Structure Tips', 
                       summary='Small project layout suggestions for clarity and reuse.', 
                       content='<p>Keep templates, static, and small helper modules organized. Use a simple database.py for demo data.</p>', 
                       published=1),
                Article(slug='deploy-simple-app', title='Deploying a Simple App', 
                       summary='Notes on lightweight deployment options for small Flask apps.', 
                       content='<p>Options include simple WSGI servers behind a reverse proxy, or using containers for portability.</p>', 
                       published=1),
            ]
            db.session.add_all(samples)
            db.session.commit()
    
    # Register blueprints
    from app.routes.public import public_bp
    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    
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
        error_code = getattr(error, 'code', 500)
        error_message = str(error)
        return render_template('errors/generic.jinja', 
                             error_code=error_code,
                             error_message=error_message), error_code
    
    return app
