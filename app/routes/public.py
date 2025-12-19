"""Public routes for viewing articles and pages."""

from flask import Blueprint, render_template, request, jsonify, make_response, flash, url_for
import logging
from urllib.parse import parse_qs
from app.models import db, Article

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
        all_articles = [a.to_dict() for a in Article.query.filter_by(published=1).order_by(Article.created_at.desc()).all()]
        resp = make_response(render_template('public/articles.jinja', articles=all_articles), 201)
        # Location header points to the new article detail (REST-friendly)
        try:
            resp.headers['Location'] = url_for('public.article_detail', slug=article.get('slug'))
        except Exception:
            pass
        return resp

    all_articles = [a.to_dict() for a in Article.query.filter_by(published=1).order_by(Article.created_at.desc()).all()]
    return render_template('public/articles.jinja', articles=all_articles)


@public_bp.route('/articles/<slug>/')
def article_detail(slug):
    """View a single article."""
    article_obj = Article.query.filter_by(slug=slug).first()
    if not article_obj:
        return render_template('public/article_not_found.jinja', slug=slug), 404
    article = article_obj.to_dict()
    return render_template('public/article.jinja', article=article)
