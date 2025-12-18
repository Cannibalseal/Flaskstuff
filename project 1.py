from flask import Flask, render_template, abort
from mdblogs import database as db

# Use templates and static files from the `mdblogs` subfolder
app = Flask(__name__, template_folder='mdblogs/templates', static_folder='mdblogs/static')


@app.route('/')
def index():
    return render_template('welcome_page.jinja')


@app.route('/admin/')
def view_admin():
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


if __name__ == '__main__':
    app.run(debug=True)