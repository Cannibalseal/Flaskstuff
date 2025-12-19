import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response, flash
import logging
from urllib.parse import parse_qs
from mdblogs import database as db
from configs import cfg

# Use templates and static files from the `mdblogs` subfolder
app = Flask(__name__, template_folder='mdblogs/templates', static_folder='mdblogs/static')
# Secret key for session (override with FLASK_SECRET env var in production)
app.secret_key = cfg.SECRET_KEY
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
    return render_template('admin.jinja')


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
    # simple login handler for demo purposes
    error = None
    if request.method == 'POST':
        # Use values (form + querystring) for robustness; fallback to manual parse if Content-Type missing
        username = request.values.get('username', '')
        password = request.values.get('password', '')
        if not username or not password:
            raw = request.get_data(as_text=True) or ''
            if raw and '=' in raw:
                try:
                    parsed = parse_qs(raw, keep_blank_values=True)
                    username = parsed.get('username', [username])[0] or username
                    password = parsed.get('password', [password])[0] or password
                except Exception:
                    pass
        admin_user = cfg.ADMIN_USER
        admin_pass = cfg.ADMIN_PASS
        if username == admin_user and password == admin_pass:
            session['logged_in'] = True
            flash('Successfully logged in!', 'success')
            next_page = request.args.get('next') or url_for('view_admin')
            return redirect(next_page)
        error = 'Invalid credentials.'
        flash(error, 'error')
    return render_template('login.jinja', error=error)


@app.route('/logout')
def view_logout():
    session.pop('logged_in', None)
    flash('Successfully logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=cfg.DEBUG)