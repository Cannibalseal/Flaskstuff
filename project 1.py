import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response, flash
import logging
from urllib.parse import parse_qs
from mdblogs import database as db
from mdblogs.forms import LoginForm, ArticleForm
from configs import cfg

# Use templates and static files from the `mdblogs` subfolder
app = Flask(__name__, template_folder='mdblogs/templates', static_folder='mdblogs/static')
# Secret key for session (override with FLASK_SECRET env var in production)
app.secret_key = cfg.SECRET_KEY
# WTForms CSRF protection uses the same secret key
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = None  # Disable CSRF token expiration for testing
# Load other config values into Flask app.config for templates and extensions
app.config.from_object(cfg)


@app.route('/')
def index():
    return render_template('welcome_page.jinja')


@app.route('/admin/')
def view_admin():
    # simple access control: require session flag
    if not session.get('logged_in'):
        return redirect(url_for('view_login', next=url_for('view_admin')))
    # Show list of all articles (published and unpublished) for management
    all_articles = db.get_all_articles_admin()
    return render_template('admin.jinja', articles=all_articles)


@app.route('/admin/article/new', methods=['GET', 'POST'])
def new_article():
    if not session.get('logged_in'):
        return redirect(url_for('view_login', next=url_for('new_article')))
    
    form = ArticleForm()
    
    if form.validate_on_submit():
        title = form.title.data
        summary = form.summary.data or ''
        content = form.content.data
        published = 1 if form.published.data else 0
        
        article = db.create_article(title, summary, content, published)
        flash(f'Article "{title}" created successfully!', 'success')
        return redirect(url_for('view_admin'))
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'error')
    
    return render_template('article_form.jinja', form=form, mode='new')


@app.route('/admin/article/edit/<slug>', methods=['GET', 'POST'])
def edit_article(slug):
    if not session.get('logged_in'):
        return redirect(url_for('view_login', next=url_for('edit_article', slug=slug)))
    
    article = db.get_article(slug)
    if not article:
        flash('Article not found.', 'error')
        return redirect(url_for('view_admin'))
    
    form = ArticleForm()
    
    if form.validate_on_submit():
        title = form.title.data
        summary = form.summary.data or ''
        content = form.content.data
        published = 1 if form.published.data else 0
        
        db.update_article(article['id'], title, summary, content, published)
        flash(f'Article "{title}" updated successfully!', 'success')
        return redirect(url_for('view_admin'))
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'error')
    elif request.method == 'GET':
        # Populate form with existing data
        form.title.data = article['title']
        form.summary.data = article['summary']
        form.content.data = article['content']
        form.published.data = article['published']
    
    return render_template('article_form.jinja', form=form, mode='edit', article=article)


@app.route('/about/')
def about():
    return render_template('about_page.jinja')


@app.route('/articles/', methods=['GET', 'POST'])
def articles():
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
        article = db.create_article(title, summary, content, published)
        if request.is_json:
            return jsonify(article), 201
        # Flash success message for HTML clients
        flash(f'Article "{title}" created successfully!', 'success')
        # For HTML clients (browsers or API tools that expect the page), return
        # the rendered articles list instead of a 302 redirect so the caller
        # immediately receives the updated page content.
        all_articles = db.get_all_articles()
        resp = make_response(render_template('articles.jinja', articles=all_articles), 201)
        # Location header points to the new article detail (REST-friendly)
        try:
            resp.headers['Location'] = url_for('article_detail', slug=article.get('slug'))
        except Exception:
            pass
        return resp

    all_articles = db.get_all_articles()
    return render_template('articles.jinja', articles=all_articles)


@app.route('/articles/<slug>/')
def article_detail(slug):
    article = db.get_article(slug)
    if not article:
        return render_template('article_not_found.jinja', slug=slug), 404
    return render_template('article.jinja', article=article)


@app.route('/login', methods=['GET', 'POST'])
def view_login():
    # WTForms-based login handler
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        admin_user = cfg.ADMIN_USER
        admin_pass = cfg.ADMIN_PASS
        
        if username == admin_user and password == admin_pass:
            session['logged_in'] = True
            flash('Successfully logged in!', 'success')
            next_page = request.args.get('next') or url_for('view_admin')
            return redirect(next_page)
        
        flash('Invalid credentials.', 'error')
    elif request.method == 'POST':
        # Form validation failed - flash all errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'error')
    
    return render_template('login.jinja', form=form)


@app.route('/logout')
def view_logout():
    session.pop('logged_in', None)
    flash('Successfully logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=cfg.DEBUG)