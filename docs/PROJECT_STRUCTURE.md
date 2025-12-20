# Sealy's Flask Blog - Documentation

## Project Structure

```
Flaskstuff/
├── app/                        # Main application package
│   ├── core/                   # Core utilities and extensions
│   │   ├── __init__.py        # Flask extensions (Mail, CSRF)
│   │   └── utils.py           # Helper functions (newsletter emails)
│   ├── forms/                  # WTForms form definitions
│   │   └── __init__.py        # Login, Article, Newsletter forms
│   ├── models/                 # SQLAlchemy database models
│   │   └── __init__.py        # Article, User, Newsletter models
│   ├── routes/                 # Flask blueprints/routes
│   │   ├── admin.py           # Admin dashboard routes
│   │   ├── auth.py            # Authentication routes
│   │   └── public.py          # Public-facing routes
│   ├── static/                 # Static assets
│   │   ├── css/
│   │   │   └── main.css       # Custom styling
│   │   └── js/                # JavaScript files (if any)
│   ├── templates/              # Jinja2 templates
│   │   ├── admin/             # Admin templates
│   │   ├── auth/              # Authentication templates
│   │   ├── components/        # Reusable components
│   │   ├── errors/            # Error page templates
│   │   └── public/            # Public page templates
│   └── __init__.py            # Application factory
├── config/                     # Configuration files
│   ├── __init__.py
│   ├── default.py             # Default config
│   └── development.py         # Development config
├── docs/                       # Documentation
│   ├── PROJECT_STRUCTURE.md   # This file
│   └── NEWSLETTER_SETUP.md    # Newsletter configuration guide
├── migrations/                 # Alembic database migrations
├── tests/                      # Test suite
│   └── __init__.py
├── .gitignore                 # Git ignore rules
├── alembic.ini                # Alembic configuration
├── README.md                  # Project overview
├── requirements.txt           # Python dependencies
└── run.py                     # Application entry point

```

## Key Features

### 1. **Article Management**
- Create, edit, delete articles with Markdown editor (EasyMDE)
- Published/draft status
- Automatic slug generation
- Markdown to HTML rendering

### 2. **Authentication**
- Admin login system
- Password change functionality
- CSRF protection
- Session management

### 3. **Newsletter System**
- Email subscription form (in footer)
- Automatic email notifications for new articles
- Subscriber management dashboard
- Flask-Mail integration

### 4. **Responsive Design**
- Futuristic purple/cyan theme
- Bootstrap 5 integration
- jQuery support
- Mobile-responsive layout

### 5. **Error Handling**
- Custom 404, 403, 500 error pages
- User-friendly error messages
- Graceful error recovery

## Technology Stack

- **Framework**: Flask 3.1.2
- **Database**: SQLAlchemy with SQLite
- **Forms**: Flask-WTF, WTForms
- **Email**: Flask-Mail
- **Markdown**: Python-Markdown
- **Frontend**: Bootstrap 5, jQuery, EasyMDE
- **Authentication**: Werkzeug password hashing

## Getting Started

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python run.py
   ```

3. **Access the app**:
   - Homepage: http://localhost:5000
   - Admin: http://localhost:5000/admin
   - Default credentials: admin / password

4. **Configure email** (optional):
   See `docs/NEWSLETTER_SETUP.md` for email configuration

## Development

### Adding New Routes
Add routes in `app/routes/` and register blueprints in `app/__init__.py`

### Adding Models
Define models in `app/models/__init__.py` and create migrations

### Adding Forms
Define forms in `app/forms/__init__.py` using WTForms

### Styling
Edit `app/static/css/main.css` for custom styles

## Database

The app uses SQLite with the following tables:
- `articles` - Blog posts
- `users` - Admin users
- `newsletter` - Email subscribers
- `tags` - Article tags (planned)
- `article_tags` - Many-to-many relationship (planned)

## Security

- CSRF protection on all forms
- Password hashing with Werkzeug
- Session-based authentication
- Admin-only routes protected

## Future Enhancements

- [ ] Tag system implementation
- [ ] Article search functionality
- [ ] Comment system
- [ ] RSS feed
- [ ] API endpoints
- [ ] Unit tests
- [ ] Docker deployment
