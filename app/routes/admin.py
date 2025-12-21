"""Admin routes for managing articles and dashboard."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from app.models import db, Article, User, Newsletter
from app.forms import ArticleForm

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
        
        # Send newsletter if article is published (synchronous for now, no Celery)
        if published:
            try:
                from app.core.tasks import send_article_notification_sync
                send_article_notification_sync(article.id)
                flash(f'Article "{title}" created and notifications sent!', 'success')
            except Exception as e:
                flash(f'Article "{title}" created, but email notifications failed: {str(e)}', 'warning')
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
