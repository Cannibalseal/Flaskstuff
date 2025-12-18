from flask import Flask, render_template

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
    return render_template('articles.jinja')


if __name__ == '__main__':
    app.run(debug=True)