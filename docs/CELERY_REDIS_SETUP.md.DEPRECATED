# Celery + Redis Setup Guide

## Overview

Your Flask app now uses **Celery** with **Redis** for asynchronous background task processing. This means:
- ✅ Newsletter emails are sent in the background
- ✅ Publishing articles is instant (no waiting for emails)
- ✅ Better performance and scalability
- ✅ Failed emails don't block the app

## What You Need

### 1. Redis Server

**For Windows (Development):**

Download and install Redis for Windows:
```powershell
# Option 1: Using Chocolatey
choco install redis-64

# Option 2: Download from GitHub
# https://github.com/microsoftarchive/redis/releases
# Download Redis-x64-3.0.504.msi and install
```

Or use **Memurai** (Redis-compatible for Windows):
```powershell
# Download from https://www.memurai.com/
```

**For Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis
```

**Verify Redis is running:**
```powershell
redis-cli ping
# Should return: PONG
```

### 2. Running the Application

You need to run **three** processes:

#### Terminal 1: Flask App
```powershell
python run.py
```

#### Terminal 2: Celery Worker
```powershell
celery -A celery_worker worker --loglevel=info --pool=solo
```

**Note:** On Windows, use `--pool=solo` or `--pool=threads`

#### Terminal 3: Redis Server (if not running as service)
```powershell
redis-server
```

## How It Works

### Newsletter Signup Flow
1. User submits email → saved to database
2. Celery task queued: `send_welcome_email_task.delay(email)`
3. User sees instant confirmation
4. Celery worker picks up task and sends email in background

### Article Publishing Flow
1. Admin publishes article → saved to database
2. Celery task queued: `send_article_notification_task.delay(article_id)`
3. Admin sees instant success message
4. Celery worker sends emails to all subscribers in background

## Configuration

Redis and Celery settings in `config/default.py`:

```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

**For Production:** Use environment variables:
```bash
export CELERY_BROKER_URL=redis://your-redis-server:6379/0
export CELERY_RESULT_BACKEND=redis://your-redis-server:6379/0
```

## Monitoring Tasks

### View Celery Worker Logs
Watch the Celery worker terminal to see tasks being processed

### Check Redis Queue
```powershell
redis-cli
> KEYS *
> LLEN celery
```

## Production Deployment

### Using Supervisor (Linux)
```ini
[program:celery_worker]
command=/path/to/venv/bin/celery -A celery_worker worker --loglevel=info
directory=/path/to/Flaskstuff
user=www-data
autostart=true
autorestart=true
```

### Using systemd (Linux)
Create `/etc/systemd/system/celery.service`:
```ini
[Unit]
Description=Celery Worker
After=network.target

[Service]
Type=forking
User=www-data
WorkingDirectory=/path/to/Flaskstuff
ExecStart=/path/to/venv/bin/celery -A celery_worker worker --loglevel=info --detach

[Install]
WantedBy=multi-user.target
```

### Cloud Options
- **AWS:** Use ElastiCache (Redis) + ECS for Celery workers
- **Heroku:** Use Redis addon + worker dyno
- **DigitalOcean:** Use Managed Redis + Droplet for workers

## Troubleshooting

### Redis Connection Error
```
Error: ConnectionError: Error 10061 connecting to localhost:6379
```
**Solution:** Start Redis server

### Celery Worker Won't Start
**Windows:** Use `--pool=solo`:
```powershell
celery -A celery_worker worker --loglevel=info --pool=solo
```

### Tasks Not Processing
1. Check Celery worker is running
2. Check Redis is running
3. Check worker logs for errors
4. Verify Redis connection: `redis-cli ping`

### Email Still Not Sending
- Celery/Redis only handles **queuing** emails
- You still need SMTP configuration (see `NEWSLETTER_SETUP.md`)
- Tasks will succeed but emails won't send without SMTP

## Testing Without Redis

If you don't want to install Redis yet:
1. Comment out Celery imports in routes
2. Use sync functions from `app/core/utils.py`
3. Emails will block but still work

## Benefits

✅ **Instant response** - User doesn't wait for emails
✅ **Scalability** - Add more workers to handle load
✅ **Reliability** - Failed emails can retry automatically
✅ **Monitoring** - Track task success/failure
✅ **Production-ready** - Industry standard architecture
