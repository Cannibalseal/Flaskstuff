"""Admin routes for managing articles and dashboard."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from app.models import db, Article, User, Newsletter
from app.forms import ArticleForm
from app.core.utils import send_new_article_notification

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
            # Check if password change is required
            if user.must_change_password:
                flash('Please change your password before continuing.', 'info')
                return redirect(url_for('auth.change_password'))
            
            # Check if user is admin
            if not user.is_admin:
                abort(403)
    return None


@admin_bp.route('/secret-area')
def secret_area():
    """Demo route to show 403 error - intentionally requires no login."""
    if not session.get('logged_in'):
        abort(403)
    return "You found the secret area! 🎉"


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
    """Create a new article."""
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    form = ArticleForm()
    
    if form.validate_on_submit():
        title = form.title.data
        summary = form.summary.data or ''
        content = form.content.data
        published = 1 if form.published.data else 0
        
        slug = Article.generate_slug(title)
        article = Article(slug=slug, title=title, summary=summary, content=content, published=published)
        db.session.add(article)
        db.session.commit()
        
        # Send newsletter if article is published
        if published:
            try:
                send_new_article_notification(article)
                flash(f'Article "{title}" created and newsletter sent to subscribers!', 'success')
            except Exception as e:
                flash(f'Article "{title}" created successfully, but newsletter failed to send: {e}', 'info')
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
    """Edit an existing article."""
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        flash('Article not found.', 'error')
        return redirect(url_for('admin.dashboard'))
    
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
    """Delete an article."""
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        flash('Article not found.', 'error')
        return redirect(url_for('admin.dashboard'))
    
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
