"""Public routes for viewing articles and pages."""

from flask import Blueprint, render_template, request, jsonify, flash, url_for, redirect, session
from app.models import db, Article, Newsletter, Comment, Like
from app.forms import NewsletterForm
import logging

logger = logging.getLogger(__name__)

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def index():
    """Home page."""
    return render_template('public/welcome_page.jinja')


@public_bp.route('/about/')
def about():
    """About page."""
    return render_template('public/about_page.jinja')


@public_bp.route('/articles/', methods=['GET', 'POST'])
def articles():
    """List all published articles or create new article via API."""
    if request.method == 'POST':
        # This route is for API/testing - production should use admin interface
        # Get data from JSON or form
        data = request.get_json(silent=True) or {}
        title = data.get('title') or request.form.get('title')
        content = data.get('content', '') or request.form.get('content', '')
        summary = data.get('summary', '') or request.form.get('summary', '')
        
        # Determine published flag
        published_str = data.get('published', '1') if data else request.form.get('published', '1')
        published = 1 if str(published_str).lower() in ('1', 'true', 'yes', 'on') else 0
        
        if not title:
            error_msg = {'error': 'Title is required'}
            return jsonify(error_msg) if request.is_json else (str(error_msg), 400)
        
        slug = Article.generate_slug(title)
        article_obj = Article(slug=slug, title=title, summary=summary, content=content, published=published)
        db.session.add(article_obj)
        db.session.commit()
        
        if request.is_json:
            return jsonify(article_obj.to_dict()), 201
        
        flash(f'Article "{title}" created successfully!', 'success')
        return redirect(url_for('public.articles'))

    # Pagination for GET requests
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = Article.query.filter_by(published=1).order_by(Article.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    all_articles = [a.to_dict() for a in pagination.items]
    return render_template('public/articles.jinja', articles=all_articles, pagination=pagination)


@public_bp.route('/articles/<slug>/')
def article_detail(slug):
    """View a single article."""
    article_obj = Article.query.filter_by(slug=slug).first()
    if not article_obj:
        return render_template('public/article_not_found.jinja', slug=slug), 404
    
    # Get comments for this article
    comments = Comment.query.filter_by(article_id=article_obj.id, approved=True).order_by(Comment.created_at.desc()).all()
    
    # Check if current user has liked the article
    user_has_liked = False
    if session.get('logged_in') and session.get('user_id'):
        user_has_liked = article_obj.is_liked_by(session.get('user_id'))
    
    article = article_obj.to_dict()
    article['comments'] = [c.to_dict() for c in comments]
    article['user_has_liked'] = user_has_liked
    
    return render_template('public/article.jinja', article=article, article_obj=article_obj)


@public_bp.route('/newsletter/subscribe', methods=['POST'])
def newsletter_subscribe():
    """Handle newsletter subscription."""
    form = NewsletterForm()
    
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        
        # Check if email already exists
        existing = Newsletter.query.filter_by(email=email).first()
        if existing:
            if existing.is_active:
                flash('This email is already subscribed to our newsletter!', 'info')
            else:
                # Reactivate subscription
                existing.is_active = 1
                db.session.commit()
                flash('Welcome back! Your subscription has been reactivated.', 'success')
        else:
            # Add new subscriber
            subscriber = Newsletter(email=email)
            db.session.add(subscriber)
            db.session.commit()
            
            # Send welcome email in background thread (works without Redis/Celery!)
            try:
                from app.core.tasks import send_welcome_email_background
                send_welcome_email_background(subscriber.email)
                flash('Thanks for subscribing! Check your email for confirmation.', 'success')
            except Exception as e:
                logger.error(f"Error starting background email thread: {e}")
                flash('Subscription successful, but confirmation email may be delayed.', 'warning')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'error')
    
    # Redirect back to the page they came from, or home
    return redirect(request.referrer or url_for('public.index'))


@public_bp.route('/newsletter/unsubscribe')
def newsletter_unsubscribe():
    """Handle newsletter unsubscription."""
    email = request.args.get('email', '').lower().strip()
    
    if not email:
        flash('Invalid unsubscribe link.', 'error')
        return redirect(url_for('public.index'))
    
    subscriber = Newsletter.query.filter_by(email=email).first()
    
    if subscriber and subscriber.is_active:
        subscriber.is_active = 0
        db.session.commit()
        flash('You have been successfully unsubscribed from our newsletter.', 'success')
    elif subscriber:
        flash('You are already unsubscribed.', 'info')
    else:
        flash('Email not found in our subscription list.', 'info')
    
    return redirect(url_for('public.index'))


@public_bp.route('/articles/<slug>/comment', methods=['POST'])
def add_comment(slug):
    """Add a comment to an article."""
    # Check if user is logged in
    if not session.get('logged_in'):
        flash('You must be logged in to comment.', 'error')
        return redirect(url_for('auth.login', next=request.url))
    
    article_obj = Article.query.filter_by(slug=slug).first()
    if not article_obj:
        flash('Article not found.', 'error')
        return redirect(url_for('public.articles'))
    
    content = request.form.get('content', '').strip()
    if not content:
        flash('Comment cannot be empty.', 'error')
        return redirect(url_for('public.article', slug=slug))
    
    # Create comment
    comment = Comment(
        content=content,
        article_id=article_obj.id,
        user_id=session.get('user_id'),
        approved=True  # Auto-approve for now; can add moderation later
    )
    db.session.add(comment)
    db.session.commit()
    
    flash('Comment added successfully!', 'success')
    return redirect(url_for('public.article', slug=slug))


@public_bp.route('/articles/<slug>/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(slug, comment_id):
    """Delete a comment (owner or admin only)."""
    # Check if user is logged in
    if not session.get('logged_in'):
        flash('You must be logged in to delete comments.', 'error')
        return redirect(url_for('auth.login', next=request.url))
    
    comment = Comment.query.get_or_404(comment_id)
    user_id = session.get('user_id')
    is_admin = session.get('is_admin')
    
    # Check if user owns the comment or is admin
    if comment.user_id != user_id and not is_admin:
        flash('You do not have permission to delete this comment.', 'error')
        return redirect(url_for('public.article', slug=slug))
    
    db.session.delete(comment)
    db.session.commit()
    
    flash('Comment deleted successfully!', 'success')
    return redirect(url_for('public.article', slug=slug))


@public_bp.route('/articles/<slug>/like', methods=['POST'])
def toggle_like(slug):
    """Toggle like on an article."""
    # Check if user is logged in
    if not session.get('logged_in'):
        return jsonify({'error': 'Must be logged in'}), 401
    
    article_obj = Article.query.filter_by(slug=slug).first()
    if not article_obj:
        return jsonify({'error': 'Article not found'}), 404
    
    user_id = session.get('user_id')
    
    # Check if user has already liked
    existing_like = Like.query.filter_by(article_id=article_obj.id, user_id=user_id).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        db.session.commit()
        liked = False
    else:
        # Like
        like = Like(article_id=article_obj.id, user_id=user_id)
        db.session.add(like)
        db.session.commit()
        liked = True
    
    return jsonify({
        'success': True,
        'liked': liked,
        'likes_count': article_obj.get_likes_count()
    })

