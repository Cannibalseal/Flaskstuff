# Quick Deployment Guide

## 📦 What's Included

This package contains a production-ready Flask blog application with:
- Complete source code
- Database migrations (Alembic)
- Configuration templates
- Comprehensive documentation
- Deployment scripts

## 🚀 Quick Start (Production)

### 1. Upload Files
```bash
# Extract the package on your server
unzip flaskstuff-deployment.zip
cd Flaskstuff
```

### 2. Set Up Environment
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements-production.txt
```

### 3. Configure Environment
```bash
# Copy and edit environment file
cp .env.example .env
nano .env  # or vim/vi

# IMPORTANT: Change these values:
# - FLASK_SECRET (generate with: python -c "import secrets; print(secrets.token_hex(32))")
# - ADMIN_USER and ADMIN_PASS
# - MAIL_USERNAME and MAIL_PASSWORD
# - Set FLASK_DEBUG=0 for production
```

### 4. Set Up Database
```bash
# Run migrations
alembic upgrade head
```

### 5. Start Application

#### Option A: Gunicorn (Recommended)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

#### Option B: Development Server (Not for production!)
```bash
python run.py
```

### 6. Set Up Celery Worker (For Newsletter)
```bash
# In a separate terminal
celery -A celery_worker worker --loglevel=info
```

## 🔒 Security Checklist

Before going live:
- [ ] Changed FLASK_SECRET to a strong random key
- [ ] Changed default admin credentials
- [ ] Set FLASK_DEBUG=0
- [ ] Configured HTTPS/SSL
- [ ] Set up firewall rules
- [ ] Configured web server (Nginx/Apache)
- [ ] Set up automated backups
- [ ] Reviewed SECURITY.md

## 📁 Important Files

- `run.py` - Development server entry point
- `wsgi.py` - Production WSGI entry point
- `.env.example` - Environment configuration template
- `requirements.txt` - Python dependencies
- `requirements-production.txt` - Production dependencies (includes Gunicorn)
- `alembic.ini` - Database migration configuration
- `DEPLOYMENT_CHECKLIST.md` - Comprehensive deployment guide

## 📚 Documentation

Full documentation available in `/docs`:
- [Site Customization Guide](docs/SITE_CUSTOMIZATION.md)
- [Security Guidelines](docs/SECURITY.md)
- [Newsletter Setup](docs/NEWSLETTER_SETUP.md)
- [Celery & Redis Setup](docs/CELERY_REDIS_SETUP.md)

See `DEPLOYMENT_CHECKLIST.md` for complete deployment instructions.

## 🆘 Quick Troubleshooting

**Can't start application:**
- Check `.env` file exists and has correct values
- Verify all dependencies installed: `pip list`
- Check logs for errors

**Database errors:**
- Run migrations: `alembic upgrade head`
- Check database file permissions

**Email not working:**
- Verify SMTP credentials in `.env`
- Check if Redis is running: `redis-cli ping`
- Start Celery worker

## 🌐 Default Credentials

After first run, login with:
- **Username**: (value from ADMIN_USER in .env)
- **Password**: (value from ADMIN_PASS in .env)

**⚠️ CHANGE THESE IMMEDIATELY AFTER FIRST LOGIN!**

## 📞 Support

For issues or questions, refer to:
- `README.md` - Full project documentation
- `DEPLOYMENT_CHECKLIST.md` - Detailed deployment steps
- `docs/` folder - Feature-specific guides

---

**Version**: 1.0.0  
**Last Updated**: December 2025  
**Python Version**: 3.8+
