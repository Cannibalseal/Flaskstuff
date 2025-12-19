DEBUG = True

# Minimal development config: define only these two variables.
# DATABASE is a path relative to the project working directory.
## DATABASE = 'app.db' ## Uncomment to use a different path

# SQLAlchemy configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False