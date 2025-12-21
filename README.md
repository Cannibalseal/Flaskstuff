# Flask Blog Application

A feature-rich blog application built with Flask, featuring user authentication, article management, comments, likes, social sharing, and an admin dashboard.

## 🚀 Features

- **User Management**
  - User registration and authentication
  - Profile management (display name, bio, avatar, social links)
  - Admin and guest user roles
  - Password change functionality

- **Article System**
  - Create, edit, and delete articles
  - Rich text editor support
  - Article author tracking
  - Article tags and categories
  - SEO-friendly URLs (slugs)

- **Engagement Features**
  - Comment system with user profiles
  - Like/unlike articles
  - Social sharing (Twitter, Facebook, LinkedIn)
  - Comment and like counters

- **Admin Dashboard**
  - Comprehensive site customization system with built-in code editors
  - Manage all articles
  - User management (view, delete, toggle admin privileges)
  - View user activity (articles, comments, likes)
  - Newsletter subscriber management
  - Customize site identity, content, styling, SEO, and features
  - Upload logo and favicon
  - Feature toggles (comments, likes, newsletter, social sharing)

- **Newsletter**
  - Email subscription system
  - Professional email templates
  - Celery async task processing

- **Site Customization**
  - Admin-only customization panel with CodeMirror editors
  - Custom HTML/CSS/JavaScript injection
  - Logo and favicon upload
  - SEO meta tags configuration
  - Color scheme customization
  - Feature toggles for comments, likes, newsletter, and social sharing
  - Live content editing for welcome and about pages

- **Profile Customization**
  - Custom background images with automatic color extraction
  - Custom colors (background, text, accent)
  - Custom font settings (size, family)
  - Social media links (Twitter, GitHub, LinkedIn, Website)

## 📁 Project Structure

```
Flaskstuff/
├── app/                          # Main application package
│   ├── __init__.py              # App factory and initialization
│   ├── core/                    # Core utilities
│   │   ├── celery_app.py       # Celery configuration
│   │   ├── tasks.py            # Background tasks
│   │   └── utils.py            # Utility functions
│   ├── forms/                   # WTForms definitions
│   │   └── __init__.py         # All form classes
│   ├── models/                  # Database models
│   │   ├── __init__.py         # Article, User, Comment, Like, Newsletter
│   │   └── site_settings.py    # Site customization settings
│   ├── routes/                  # Blueprint routes
│   │   ├── admin.py            # Admin dashboard routes
│   │   ├── auth.py             # Authentication routes
│   │   ├── profile.py          # User profile routes
│   │   └── public.py           # Public routes
│   ├── static/                  # Static files
│   │   ├── css/
│   │   │   └── main.css        # Custom styles
│   │   └── uploads/            # User-uploaded files (gitignored)
│   │       ├── backgrounds/    # Profile backgrounds
│   │       ├── profiles/       # Profile pictures
│   │       └── site/           # Logo, favicon
│   └── templates/               # Jinja2 templates
│       ├── admin/              # Admin templates
│       ├── auth/               # Auth templates
│       ├── components/         # Reusable components
│       ├── errors/             # Error pages
│       ├── profile/            # Profile templates
│       └── public/             # Public templates
│
├── config/                      # Configuration files
│   ├── __init__.py
│   ├── default.py              # Default configuration
│   └── development.py          # Development settings
│
├── docs/                        # Documentation
│   ├── CELERY_REDIS_SETUP.md  # Celery and Redis setup guide
│   ├── NEW_FEATURES.md         # Recent features documentation
│   ├── NEWSLETTER_SETUP.md     # Newsletter configuration
│   ├── PROJECT_STRUCTURE.md    # Detailed structure guide
│   ├── SECURITY.md             # Security guidelines
│   ├── TESTING_GUIDE.md        # Testing instructions
│   └── UPDATES.md              # Update history
│
├── instance/                    # Instance-specific files (gitignored)
│
├── migrations/                  # Alembic database migrations
│   └── versions/               # Migration scripts
│
├── tests/                       # Test suite
│   └── __init__.py
│
├── .env                         # Environment variables (gitignored)
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── alembic.ini                  # Alembic configuration
├── app.db                       # SQLite database (gitignored)
├── celery_worker.py             # Celery worker entry point
├── README.md                    # This file
├── requirements.txt             # Python dependencies
└── run.py                       # Application entry point
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Redis (optional, for Celery tasks)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Flaskstuff
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Initialize the database**
   ```bash
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

7. **Access the application**
   - Open browser: http://127.0.0.1:5000
   - Default admin credentials (if seeded): admin/admin

## ⚙️ Configuration

Key environment variables in `.env`:

```env
# Flask Configuration
FLASK_SECRET=your-secret-key-here
FLASK_DEBUG=1

# Admin Credentials (Change these!)
ADMIN_USER=admin
ADMIN_PASS=change-this-password

# Gmail SMTP Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password-here
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Celery/Redis Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Database Configuration (Optional - defaults to SQLite)
# DATABASE_URL=sqlite:///app.db
```

## 🔧 Development

### Running with Celery (optional)
```bash
# Start Redis
redis-server

# Start Celery worker
celery -A celery_worker worker --loglevel=info
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📚 Documentation

Detailed documentation is available in the `/docs` folder:
- [Project Structure](docs/PROJECT_STRUCTURE.md)
- [Site Customization Guide](docs/SITE_CUSTOMIZATION.md) - **NEW!** Comprehensive admin customization system
- [Newsletter Setup](docs/NEWSLETTER_SETUP.md)
- [Celery & Redis Setup](docs/CELERY_REDIS_SETUP.md)
- [Security Guidelines](docs/SECURITY.md)
- [Testing Guide](docs/TESTING_GUIDE.md)
- [New Features](docs/NEW_FEATURES.md)
- [Update History](docs/UPDATES.md)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## 🚢 Deployment

Before deploying to production:

1. Set `FLASK_ENV=production`
2. Generate strong `SECRET_KEY`
3. Use PostgreSQL instead of SQLite
4. Configure production email server
5. Set up HTTPS/SSL
6. Enable rate limiting
7. Review security settings in [SECURITY.md](docs/SECURITY.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

Built with:
- Flask 3.1.2
- SQLAlchemy 2.0.45
- Bootstrap 5.3.2
- Bootstrap Icons 1.11.3
- CodeMirror 5.65.16 (Dracula theme)
- Pillow 11.1.0 (image processing)
- Celery 5.4.0 & Redis 5.2.1
- Alembic 1.14.0
- Flask-WTF & WTForms
