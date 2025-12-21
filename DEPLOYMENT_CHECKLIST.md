# Deployment Checklist

## Pre-Deployment Security Review

### Environment Configuration
- [ ] Copy `.env.example` to `.env` on production server
- [ ] Generate strong `FLASK_SECRET` (use: `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] Change default `ADMIN_USER` and `ADMIN_PASS`
- [ ] Configure production email credentials (Gmail or other SMTP)
- [ ] Set `FLASK_DEBUG=0` in production
- [ ] Verify `.env` is in `.gitignore` (✅ Already configured)

### Database
- [ ] Consider switching from SQLite to PostgreSQL for production
- [ ] Run all migrations: `alembic upgrade head`
- [ ] Backup database before deployment
- [ ] Set up automated database backups

### File Uploads
- [ ] Verify upload directories exist:
  - `app/static/uploads/backgrounds/`
  - `app/static/uploads/profiles/`
  - `app/static/uploads/site/`
- [ ] Ensure proper file permissions (writable by application)
- [ ] Configure file size limits in server (Nginx/Apache)
- [ ] Consider using cloud storage (S3, Azure Blob) for uploads

### Redis & Celery
- [ ] Install and configure Redis server
- [ ] Update `CELERY_BROKER_URL` with production Redis URL
- [ ] Set up Celery worker as system service (systemd/supervisord)
- [ ] Configure Celery logging and monitoring
- [ ] Test newsletter email sending

### Security Headers
- [ ] Configure HTTPS/SSL certificate (Let's Encrypt recommended)
- [ ] Set up security headers in web server config:
  ```nginx
  add_header X-Frame-Options "SAMEORIGIN" always;
  add_header X-Content-Type-Options "nosniff" always;
  add_header X-XSS-Protection "1; mode=block" always;
  add_header Referrer-Policy "no-referrer-when-downgrade" always;
  add_header Content-Security-Policy "default-src 'self' https: data: 'unsafe-inline' 'unsafe-eval';" always;
  ```
- [ ] Enable HSTS (HTTP Strict Transport Security)
- [ ] Disable directory listing in web server

### Application Security
- [ ] Review admin permissions (only trusted users should have admin access)
- [ ] Review custom CSS/JS in site settings (ensure no malicious code)
- [ ] Set up rate limiting (Flask-Limiter recommended)
- [ ] Configure session security:
  - Set `SESSION_COOKIE_SECURE=True` (HTTPS only)
  - Set `SESSION_COOKIE_HTTPONLY=True`
  - Set `SESSION_COOKIE_SAMESITE='Lax'`
- [ ] Review [SECURITY.md](docs/SECURITY.md) for additional guidelines

### Code Review
- [ ] Remove debug print statements
- [ ] Check for hardcoded credentials (none found ✅)
- [ ] Verify all sensitive data uses environment variables ✅
- [ ] Test all features in staging environment
- [ ] Run security scanner (Bandit, Safety)

### Dependencies
- [ ] Update all packages to latest secure versions:
  ```bash
  pip list --outdated
  pip install --upgrade <package>
  pip freeze > requirements.txt
  ```
- [ ] Check for known vulnerabilities:
  ```bash
  pip install safety
  safety check
  ```

### Git Repository
- [ ] Verify `.gitignore` is complete ✅
- [ ] Ensure `.env` is never committed (check history):
  ```bash
  git log --all -- .env
  ```
- [ ] Ensure `*.db` files are not committed ✅
- [ ] Ensure upload directories have `.gitkeep` files ✅
- [ ] Remove sensitive data from git history if found (use BFG Repo-Cleaner)

### Web Server Configuration

#### Nginx Example
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/Flaskstuff/app/static;
        expires 30d;
    }
}
```

#### Apache Example
```apache
<VirtualHost *:80>
    ServerName your-domain.com
    Redirect permanent / https://your-domain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName your-domain.com

    SSLEngine on
    SSLCertificateFile /path/to/fullchain.pem
    SSLCertificateKeyFile /path/to/privkey.pem

    WSGIDaemonProcess flaskapp user=www-data group=www-data threads=5
    WSGIScriptAlias / /path/to/Flaskstuff/wsgi.py

    <Directory /path/to/Flaskstuff>
        WSGIProcessGroup flaskapp
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>

    Alias /static /path/to/Flaskstuff/app/static
    <Directory /path/to/Flaskstuff/app/static>
        Require all granted
    </Directory>
</VirtualHost>
```

### WSGI Configuration
Create `wsgi.py` in project root:
```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
```

### Systemd Service (Gunicorn)
Create `/etc/systemd/system/flaskapp.service`:
```ini
[Unit]
Description=Flask Blog Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/Flaskstuff
Environment="PATH=/path/to/Flaskstuff/.venv/bin"
ExecStart=/path/to/Flaskstuff/.venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 wsgi:app

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable flaskapp
sudo systemctl start flaskapp
```

### Celery Worker Service
Create `/etc/systemd/system/celery-worker.service`:
```ini
[Unit]
Description=Celery Worker
After=network.target redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/Flaskstuff
Environment="PATH=/path/to/Flaskstuff/.venv/bin"
ExecStart=/path/to/Flaskstuff/.venv/bin/celery -A celery_worker worker --loglevel=info

[Install]
WantedBy=multi-user.target
```

### Monitoring & Logging
- [ ] Set up application logging:
  ```python
  # In config/default.py
  import logging
  logging.basicConfig(
      filename='/var/log/flaskapp/app.log',
      level=logging.INFO,
      format='%(asctime)s %(levelname)s: %(message)s'
  )
  ```
- [ ] Configure log rotation (logrotate)
- [ ] Set up error monitoring (Sentry recommended)
- [ ] Configure uptime monitoring (UptimeRobot, Pingdom)
- [ ] Set up performance monitoring (New Relic, DataDog)

### Testing Before Go-Live
- [ ] Test user registration and login
- [ ] Test article creation, editing, deletion
- [ ] Test comment system
- [ ] Test like functionality
- [ ] Test newsletter subscription
- [ ] Test social sharing buttons
- [ ] Test admin dashboard access
- [ ] Test site customization panel
- [ ] Test file uploads (profile pics, backgrounds, logo, favicon)
- [ ] Test profile customization
- [ ] Test all feature toggles
- [ ] Test on multiple browsers (Chrome, Firefox, Safari, Edge)
- [ ] Test on mobile devices
- [ ] Test with slow internet connection
- [ ] Load test with multiple concurrent users

### Performance Optimization
- [ ] Enable gzip compression in web server
- [ ] Set up CDN for static assets (Cloudflare recommended)
- [ ] Configure browser caching headers
- [ ] Optimize database queries (add indexes)
- [ ] Consider Redis for session storage
- [ ] Minify CSS/JS in production
- [ ] Optimize images (compress uploads)
- [ ] Enable HTTP/2 in web server

### Backup Strategy
- [ ] Set up automated database backups (daily)
- [ ] Back up uploaded files to cloud storage
- [ ] Back up `.env` file securely
- [ ] Test backup restoration process
- [ ] Document backup locations and procedures

### Post-Deployment
- [ ] Monitor error logs for first 24 hours
- [ ] Check SSL certificate validity
- [ ] Verify all emails are being sent
- [ ] Test from different locations/networks
- [ ] Update DNS records if needed
- [ ] Submit sitemap to search engines
- [ ] Set up Google Analytics or alternative
- [ ] Update documentation with production URLs

### Maintenance
- [ ] Schedule regular dependency updates
- [ ] Schedule regular security audits
- [ ] Monitor disk space (uploads directory)
- [ ] Monitor database size
- [ ] Review and rotate logs regularly
- [ ] Keep SSL certificates up to date

## Quick Commands Reference

### Start Application (Development)
```bash
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
python run.py
```

### Start Application (Production with Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

### Start Celery Worker
```bash
celery -A celery_worker worker --loglevel=info
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Check for Vulnerabilities
```bash
safety check
bandit -r app/
```

### Update Dependencies
```bash
pip list --outdated
pip install --upgrade <package>
pip freeze > requirements.txt
```

### Generate Secret Key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Current Status

### ✅ Completed
- [x] `.gitignore` configured with comprehensive patterns
- [x] `requirements.txt` up to date with all dependencies
- [x] `.env.example` created as template
- [x] Upload directories have `.gitkeep` files
- [x] Site customization system fully functional
- [x] All migrations applied (6 total)
- [x] Documentation complete

### ⚠️ Review Before Production
- Admin panel custom CSS/JS (ensure no malicious code)
- Email credentials (currently using Gmail with visible app password)
- Default admin credentials (admin/password)
- SQLite database (consider PostgreSQL for production)

### 📝 Recommended Additions
- Rate limiting on login/registration endpoints
- CAPTCHA on registration form
- Email verification for new accounts
- Password strength requirements
- Two-factor authentication for admins
- API rate limiting

---

**Last Updated**: January 2025  
**Status**: Ready for staging deployment
