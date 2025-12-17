from flask import Flask, render_template

# Use templates and static files from the `mdblogs` subfolder
app = Flask(__name__, template_folder='mdblogs/templates', static_folder='mdblogs/static')


@app.route('/')
def index():
    return render_template('welcome_page.html')


@app.route('/admin/')
def view_admin():
    return "Admin Dashboard"


@app.route('/about/')
def about():
    return render_template('about_page.html')


@app.route('/articles/')
def articles():
    return "<html><body><h1>Articles</h1><p>List of articles will go here.</p><p><a href=\"/\">Back</a></p></body></html>"


if __name__ == '__main__':
    app.run(debug=True)