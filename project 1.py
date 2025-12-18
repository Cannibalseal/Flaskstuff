import os
from flask import Flask, render_template, request, redirect, url_for, session
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


@app.route('/articles/')
def articles():
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
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        admin_user = cfg.ADMIN_USER
        admin_pass = cfg.ADMIN_PASS
        if username == admin_user and password == admin_pass:
            session['logged_in'] = True
            next_page = request.args.get('next') or url_for('view_admin')
            return redirect(next_page)
        error = 'Invalid credentials.'
    return render_template('login.jinja', error=error)


@app.route('/logout')
def view_logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=cfg.DEBUG)