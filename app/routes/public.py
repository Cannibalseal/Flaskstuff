"""Public routes for viewing articles and pages."""

from flask import Blueprint, render_template, request, jsonify, make_response, flash, url_for, redirect
import logging
from urllib.parse import parse_qs
from app.models import db, Article, Newsletter
from app.forms import NewsletterForm

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
        # Accept JSON or form data. request.values covers form and querystring.
        data = request.get_json(silent=True) or {}
        title = data.get('title') or request.values.get('title')
        content = data.get('content') or request.values.get('content', '')
        summary = data.get('summary') or request.values.get('summary', '')
        # Determine published flag: accept JSON value or form value; if missing, default to published
        pub_raw = None
        if 'published' in data:
            pub_raw = data.get('published')
        else:
            pub_raw = request.values.get('published', None)

        def _to_bool(v):
            if v is None:
                return None
            if isinstance(v, bool):
                return v
            try:
                s = str(v).strip().lower()
            except Exception:
                return False
            return s in ('1', 'true', 'yes', 'on')

        pub_bool = _to_bool(pub_raw)
        # If client omitted the published flag, default to published (show immediately)
        if pub_bool is None:
            published = 1
        else:
            published = 1 if pub_bool else 0
        if not title:
            raw = request.get_data(as_text=True) or ''
            # If Content-Type header is missing but body looks urlencoded, try to parse it
            if raw and '=' in raw and '&' in raw:
                try:
                    parsed = parse_qs(raw, keep_blank_values=True)
                    # parse_qs returns lists for each key
                    title = parsed.get('title', [None])[0]
                    content = parsed.get('content', [content])[0] or content
                    summary = parsed.get('summary', [summary])[0] or summary
                except Exception:
                    pass
            if not title:
                # Helpful debug info to diagnose why the client isn't sending the title
                logging.debug('POST /articles missing title; headers=%s', dict(request.headers))
                debug = {
                    'error': 'Missing title',
                    'content_type': request.content_type,
                    'form_keys': list(request.form.keys()),
                    'values_keys': list(request.values.keys()),
                    'raw_body': (raw[:200] + '...') if raw else ''
                }
                # Return JSON when client sent JSON or for easier debugging in API clients
                if request.is_json:
                    return jsonify(debug), 400
                return (str(debug), 400)
        
        slug = Article.generate_slug(title)
        article_obj = Article(slug=slug, title=title, summary=summary, content=content, published=published)
        db.session.add(article_obj)
        db.session.commit()
        article = article_obj.to_dict()
        
        if request.is_json:
            return jsonify(article), 201
        # Flash success message for HTML clients
        flash(f'Article "{title}" created successfully!', 'success')
        # For HTML clients (browsers or API tools that expect the page), return
        # the rendered articles list instead of a 302 redirect so the caller
        # immediately receives the updated page content.
        page = request.args.get('page', 1, type=int)
        per_page = 10
        pagination = Article.query.filter_by(published=1).order_by(Article.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        all_articles = [a.to_dict() for a in pagination.items]
        resp = make_response(render_template('public/articles.jinja', articles=all_articles, pagination=pagination), 201)
        # Location header points to the new article detail (REST-friendly)
        try:
            resp.headers['Location'] = url_for('public.article_detail', slug=article.get('slug'))
        except Exception:
            pass
        return resp

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
    article = article_obj.to_dict()
    return render_template('public/article.jinja', article=article)


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
            
            # Send welcome email asynchronously
            try:
                from app.core.tasks import send_welcome_email_task
                send_welcome_email_task.delay(subscriber.email)
                flash('Thanks for subscribing! Check your email for confirmation.', 'success')
            except Exception as e:
                flash('Subscription successful, but confirmation email failed to send.', 'info')
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

