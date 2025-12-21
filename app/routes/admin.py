"""Admin routes for managing articles and dashboard."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.utils import secure_filename
from app.models import db, Article, User, Newsletter
from app.models.site_settings import SiteSettings
from app.forms import ArticleForm
import os
from pathlib import Path

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def require_login():
    """Check if user is logged in and is admin."""
    if not session.get('logged_in'):
        return redirect(url_for('auth.login', next=request.url))
    
    # Check if user is admin
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)
        if user:
            # Check if password change is required (using database value, not session)
            if user.must_change_password == 1:
                flash('Please change your password before continuing.', 'info')
                return redirect(url_for('auth.change_password'))
            
            # Check if user is admin
            if not user.is_admin:
                abort(403)
    return None


def require_writer_or_admin():
    """Check if user is logged in and can write articles (writer or admin)."""
    if not session.get('logged_in'):
        return redirect(url_for('auth.login', next=request.url))
    
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)
        if user:
            # Check if password change is required (using explicit == 1)
            if user.must_change_password == 1:
                flash('Please change your password before continuing.', 'info')
                return redirect(url_for('auth.change_password'))
            
            # Check if user can write articles or is admin
            if not user.can_write_articles and not user.is_admin:
                flash('You do not have permission to create articles.', 'error')
                abort(403)
    return None


@admin_bp.route('/')
def dashboard():
    """Admin dashboard - show all articles."""
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    # Show list of all articles (published and unpublished) for management
    all_articles = [article.to_dict() for article in Article.query.order_by(Article.created_at.desc()).all()]
    return render_template('admin/admin.jinja', articles=all_articles)


@admin_bp.route('/article/new', methods=['GET', 'POST'])
def new_article():
    """Create a new article (for writers and admins)."""
    redirect_response = require_writer_or_admin()
    if redirect_response:
        return redirect_response
    
    form = ArticleForm()
    
    if form.validate_on_submit():
        title = form.title.data
        summary = form.summary.data or ''
        content = form.content.data
        published = 1 if form.published.data else 0
        
        slug = Article.generate_slug(title)
        article = Article(
            slug=slug, 
            title=title, 
            summary=summary, 
            content=content, 
            published=published,
            author_id=session.get('user_id')  # Track who created it
        )
        db.session.add(article)
        db.session.commit()
        
        # Send newsletter in background thread if article is published (works without Redis/Celery!)
        if published:
            try:
                from app.core.tasks import send_article_notification_background
                send_article_notification_background(article.id)
                flash(f'Article "{title}" created and notifications are being sent!', 'success')
            except Exception as e:
                flash(f'Article "{title}" created, but email notifications may be delayed: {str(e)}', 'warning')
        else:
            flash(f'Article "{title}" created successfully!', 'success')
        
        return redirect(url_for('admin.dashboard'))
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'error')
    
    return render_template('admin/article_form.jinja', form=form, mode='new')


@admin_bp.route('/article/edit/<slug>', methods=['GET', 'POST'])
def edit_article(slug):
    """Edit an existing article (admins can edit all, writers can edit their own)."""
    redirect_response = require_writer_or_admin()
    if redirect_response:
        return redirect_response
    
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        flash('Article not found.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Check if user can edit this article
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)
    
    # Writers can only edit their own articles, admins can edit all
    if not user.is_admin and article.author_id != user_id:
        flash('You can only edit your own articles.', 'error')
        abort(403)
    
    form = ArticleForm()
    
    if form.validate_on_submit():
        article.title = form.title.data
        article.summary = form.summary.data or ''
        article.content = form.content.data
        article.published = 1 if form.published.data else 0
        article.updated_at = db.func.now()
        
        db.session.commit()
        flash(f'Article "{article.title}" updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'error')
    elif request.method == 'GET':
        # Populate form with existing data
        form.title.data = article.title
        form.summary.data = article.summary
        form.content.data = article.content
        form.published.data = bool(article.published)
    
    return render_template('admin/article_form.jinja', form=form, mode='edit', article=article.to_dict())


@admin_bp.route('/article/delete/<slug>', methods=['POST'])
def delete_article(slug):
    """Delete an article (admins can delete all, writers can delete their own)."""
    redirect_response = require_writer_or_admin()
    if redirect_response:
        return redirect_response
    
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        flash('Article not found.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Check if user can delete this article
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)
    
    # Writers can only delete their own articles, admins can delete all
    if not user.is_admin and article.author_id != user_id:
        flash('You can only delete your own articles.', 'error')
        abort(403)
    
    title = article.title
    db.session.delete(article)
    db.session.commit()
    
    flash(f'Article "{title}" deleted successfully!', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/newsletter/subscribers')
def newsletter_subscribers():
    """View all newsletter subscribers."""
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    subscribers = Newsletter.query.order_by(Newsletter.subscribed_at.desc()).all()
    return render_template('admin/newsletter_subscribers.jinja', subscribers=subscribers)


@admin_bp.route('/newsletter/delete/<int:subscriber_id>', methods=['POST'])
def delete_subscriber(subscriber_id):
    """Delete a newsletter subscriber."""
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    subscriber = db.session.get(Newsletter, subscriber_id)
    if not subscriber:
        flash('Subscriber not found.', 'error')
        return redirect(url_for('admin.newsletter_subscribers'))
    
    email = subscriber.email
    db.session.delete(subscriber)
    db.session.commit()
    
    flash(f'Subscriber "{email}" removed successfully!', 'success')
    return redirect(url_for('admin.newsletter_subscribers'))


@admin_bp.route('/users')
def users():
    """View all users."""
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    all_users = User.query.order_by(User.created_at.desc()).all()
    current_user_id = session.get('user_id')
    
    # Get activity stats for each user
    users_with_stats = []
    for user in all_users:
        from app.models import Comment, Like
        stats = {
            'user': user,
            'articles_count': len(user.articles),
            'comments_count': Comment.query.filter_by(user_id=user.id).count(),
            'likes_count': Like.query.filter_by(user_id=user.id).count(),
        }
        users_with_stats.append(stats)
    
    return render_template('admin/users.jinja', users=users_with_stats, current_user_id=current_user_id)


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
def toggle_admin(user_id):
    """Toggle admin privileges for a user."""
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    current_user_id = session.get('user_id')
    if user_id == current_user_id:
        flash('You cannot change your own admin privileges.', 'error')
        return redirect(url_for('admin.users'))
    
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.users'))
    
    user.is_admin = 1 if user.is_admin == 0 else 0
    db.session.commit()
    
    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin privileges {status} for user "{user.username}".', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/toggle-writer', methods=['POST'])
def toggle_writer(user_id):
    """Toggle article writing permissions for a user."""
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.users'))
    
    user.can_write_articles = 1 if user.can_write_articles == 0 else 0
    db.session.commit()
    
    status = 'granted' if user.can_write_articles else 'revoked'
    flash(f'Article writing permission {status} for user "{user.username}".', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete a user."""
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    current_user_id = session.get('user_id')
    if user_id == current_user_id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.users'))
    
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User "{username}" deleted successfully!', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/activity')
def user_activity(user_id):
    """View detailed activity for a user."""
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.users'))
    
    from app.models import Comment, Like
    
    # Get user's articles
    articles = Article.query.filter_by(author_id=user_id).order_by(Article.created_at.desc()).all()
    
    # Get user's comments
    comments = Comment.query.filter_by(user_id=user_id).order_by(Comment.created_at.desc()).limit(50).all()
    
    # Get user's likes
    likes = Like.query.filter_by(user_id=user_id).order_by(Like.created_at.desc()).limit(50).all()
    
    activity_data = {
        'user': user,
        'articles': articles,
        'comments': comments,
        'likes': likes,
        'stats': {
            'total_articles': len(articles),
            'total_comments': Comment.query.filter_by(user_id=user_id).count(),
            'total_likes': Like.query.filter_by(user_id=user_id).count(),
        }
    }
    
    return render_template('admin/user_activity.jinja', **activity_data)


@admin_bp.route('/customize-site', methods=['GET', 'POST'])
def customize_site():
    """Admin-only site customization page with built-in editor."""
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    settings = SiteSettings.get_settings()
    
    if request.method == 'POST':
        # Site Identity
        settings.site_name = request.form.get('site_name', 'My Blog')
        settings.site_tagline = request.form.get('site_tagline', '')
        settings.site_description = request.form.get('site_description', '')
        
        # Page Content
        settings.welcome_page_content = request.form.get('welcome_page_content', '')
        settings.about_page_content = request.form.get('about_page_content', '')
        settings.footer_content = request.form.get('footer_content', '')
        
        # Custom Styling
        settings.custom_css = request.form.get('custom_css', '')
        settings.custom_js = request.form.get('custom_js', '')
        
        # SEO
        settings.meta_keywords = request.form.get('meta_keywords', '')
        settings.meta_description = request.form.get('meta_description', '')
        
        # Social Media
        settings.site_twitter = request.form.get('site_twitter', '')
        settings.site_github = request.form.get('site_github', '')
        settings.site_email = request.form.get('site_email', '')
        
        # Appearance
        settings.primary_color = request.form.get('primary_color', '#06b6d4')
        settings.secondary_color = request.form.get('secondary_color', '#8b5cf6')
        
        # Features Toggle
        settings.enable_comments = 'enable_comments' in request.form
        settings.enable_likes = 'enable_likes' in request.form
        settings.enable_newsletter = 'enable_newsletter' in request.form
        settings.enable_social_sharing = 'enable_social_sharing' in request.form
        
        # Handle logo upload
        if 'logo' in request.files:
            logo = request.files['logo']
            if logo and logo.filename:
                filename = secure_filename(logo.filename)
                timestamp = os.urandom(8).hex()
                file_ext = os.path.splitext(filename)[1]
                unique_filename = f'logo_{timestamp}{file_ext}'
                
                upload_folder = Path('app/static/uploads/site')
                upload_folder.mkdir(parents=True, exist_ok=True)
                filepath = upload_folder / unique_filename
                logo.save(filepath)
                
                # Delete old logo
                if settings.logo_path:
                    old_path = Path('app/static') / settings.logo_path.lstrip('/')
                    if old_path.exists():
                        old_path.unlink()
                
                settings.logo_path = f'uploads/site/{unique_filename}'
        
        # Handle favicon upload
        if 'favicon' in request.files:
            favicon = request.files['favicon']
            if favicon and favicon.filename:
                filename = secure_filename(favicon.filename)
                timestamp = os.urandom(8).hex()
                file_ext = os.path.splitext(filename)[1]
                unique_filename = f'favicon_{timestamp}{file_ext}'
                
                upload_folder = Path('app/static/uploads/site')
                upload_folder.mkdir(parents=True, exist_ok=True)
                filepath = upload_folder / unique_filename
                favicon.save(filepath)
                
                # Delete old favicon
                if settings.favicon_path:
                    old_path = Path('app/static') / settings.favicon_path.lstrip('/')
                    if old_path.exists():
                        old_path.unlink()
                
                settings.favicon_path = f'uploads/site/{unique_filename}'
        
        db.session.commit()
        flash('Site settings saved successfully!', 'success')
        return redirect(url_for('admin.customize_site'))
    
    return render_template('admin/customize_site.jinja', settings=settings)

