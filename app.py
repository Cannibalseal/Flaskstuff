from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response, flash
import logging
from urllib.parse import parse_qs
from mdblogs.models import db, Article, User
from mdblogs.forms import LoginForm, ArticleForm, ChangePasswordForm
from configs import cfg

# Use templates and static files from the `mdblogs` subfolder
app = Flask(__name__, template_folder='mdblogs/templates', static_folder='mdblogs/static')
# Secret key for session (override with FLASK_SECRET env var in production)
app.secret_key = cfg.SECRET_KEY
# WTForms CSRF protection uses the same secret key
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = None  # Disable CSRF token expiration for testing
# Load config values into Flask app.config
app.config.from_object(cfg)

# Initialize SQLAlchemy
db.init_app(app)

# Create tables if they don't exist
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


@app.route('/')
def index():
    return render_template('welcome_page.jinja')


@app.route('/admin/')
def view_admin():
    # simple access control: require session flag
    if not session.get('logged_in'):
        return redirect(url_for('view_login', next=url_for('view_admin')))
    
    # Check if password change is required
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user and user.must_change_password:
            flash('Please change your password before continuing.', 'info')
            return redirect(url_for('change_password'))
    
    # Show list of all articles (published and unpublished) for management
    all_articles = [article.to_dict() for article in Article.query.order_by(Article.created_at.desc()).all()]
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
        
        slug = Article.generate_slug(title)
        article = Article(slug=slug, title=title, summary=summary, content=content, published=published)
        db.session.add(article)
        db.session.commit()
        
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
    
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        flash('Article not found.', 'error')
        return redirect(url_for('view_admin'))
    
    form = ArticleForm()
    
    if form.validate_on_submit():
        article.title = form.title.data
        article.summary = form.summary.data or ''
        article.content = form.content.data
        article.published = 1 if form.published.data else 0
        article.updated_at = db.func.now()
        
        db.session.commit()
        flash(f'Article "{article.title}" updated successfully!', 'success')
        return redirect(url_for('view_admin'))
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
    
    return render_template('article_form.jinja', form=form, mode='edit', article=article.to_dict())


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
        resp = make_response(render_template('articles.jinja', articles=all_articles), 201)
        # Location header points to the new article detail (REST-friendly)
        try:
            resp.headers['Location'] = url_for('article_detail', slug=article.get('slug'))
        except Exception:
            pass
        return resp

    all_articles = [a.to_dict() for a in Article.query.filter_by(published=1).order_by(Article.created_at.desc()).all()]
    return render_template('articles.jinja', articles=all_articles)


@app.route('/articles/<slug>/')
def article_detail(slug):
    article_obj = Article.query.filter_by(slug=slug).first()
    if not article_obj:
        return render_template('article_not_found.jinja', slug=slug), 404
    article = article_obj.to_dict()
    return render_template('article.jinja', article=article)


@app.route('/login', methods=['GET', 'POST'])
def view_login():
    # WTForms-based login handler
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Check user in database
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['logged_in'] = True
            session['user_id'] = user.id
            session['username'] = user.username
            
            # Check if password change is required
            if user.must_change_password:
                flash('Please change your password before continuing.', 'info')
                return redirect(url_for('change_password'))
            
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


@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    # Require login
    if not session.get('logged_in'):
        return redirect(url_for('view_login'))
    
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('view_login'))
    
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        
        # Verify current password
        if not user.check_password(current_password):
            flash('Current password is incorrect.', 'error')
        else:
            # Update password
            user.set_password(new_password)
            user.must_change_password = 0
            db.session.commit()
            
            flash('Password changed successfully!', 'success')
            return redirect(url_for('view_admin'))
    elif request.method == 'POST':
        # Form validation failed - flash all errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'error')
    
    # Check if this is a forced password change
    is_required = user.must_change_password == 1
    return render_template('change_password.jinja', form=form, is_required=is_required)


@app.route('/logout')
def view_logout():
    session.clear()
    flash('Successfully logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=cfg.DEBUG)