# Security & Configuration Guide

## 🔐 Sensitive Information Protection

This project uses environment variables to protect sensitive information. **All sensitive data is stored in the `.env` file which is NOT committed to GitHub.**

### What is Protected?

✅ **Email credentials** - Gmail username and app password  
✅ **Flask secret key** - Used for session security  
✅ **Admin credentials** - Default admin username and password  
✅ **Database files** - SQLite database in `instance/` folder  
✅ **Redis URLs** - Connection strings for Celery

### Files That Are Ignored by Git:

- `.env` - Contains all sensitive environment variables
- `instance/` - Contains the SQLite database with user data
- `__pycache__/` - Python bytecode
- `.venv/` - Virtual environment

## 🚀 Setup Instructions for New Users

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd Flaskstuff
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example file and fill in your own credentials:
```bash
copy .env.example .env  # Windows
# or
cp .env.example .env  # Linux/Mac
```

**Edit `.env` with your own values:**
```env
FLASK_SECRET=generate-random-string-here
ADMIN_USER=youradmin
ADMIN_PASS=yoursecurepassword
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
```

### 5. Get Gmail App Password
1. Go to your Google Account: https://myaccount.google.com/
2. Enable 2-Step Verification (if not already enabled)
3. Go to https://myaccount.google.com/apppasswords
4. Generate a new app password for "Mail"
5. Copy the 16-character password (spaces don't matter)
6. Add it to your `.env` file as `MAIL_PASSWORD`

### 6. Initialize Database
```bash
python run.py
```
The database will be created automatically on first run.

## ⚠️ Important Security Notes

### For Developers:

1. **NEVER commit `.env` file** - It's already in `.gitignore`
2. **NEVER hardcode credentials** - Always use environment variables
3. **Change default passwords** - Don't use "admin"/"password" in production
4. **Generate strong secret keys** - Use random strings for `FLASK_SECRET`
5. **Use Gmail app passwords** - Not your actual Gmail password
6. **Review commits** - Make sure no sensitive data slips through

### For Production Deployment:

1. **Set strong passwords** - Use password managers to generate them
2. **Use environment variables** - Set them in your hosting platform
3. **Enable HTTPS** - Always use SSL/TLS in production
4. **Use PostgreSQL** - SQLite is for development only
5. **Secure your Redis** - Add authentication if using Celery
6. **Regular updates** - Keep dependencies up to date

## 🔍 Verify Security

Check if sensitive files are properly ignored:
```bash
git check-ignore .env instance/
```

Check if `.env` was never committed:
```bash
git ls-files .env
# Should return nothing
```

## 📝 What Gets Committed to GitHub?

✅ Source code (`.py` files)  
✅ Templates (`.jinja` files)  
✅ Static assets (CSS, JS)  
✅ Configuration templates (`.env.example`)  
✅ Documentation (`.md` files)  
✅ Requirements list (`requirements.txt`)  

❌ Environment variables (`.env`)  
❌ Database files (`instance/*.db`)  
❌ Virtual environment (`.venv/`)  
❌ Python bytecode (`__pycache__/`)  
❌ User uploads or logs  

## 🆘 If You Accidentally Committed Secrets

If you accidentally committed sensitive data:

1. **Immediately revoke credentials** - Change passwords, rotate keys
2. **Remove from git history**:
   ```bash
   # WARNING: This rewrites history
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push** (if already pushed to GitHub):
   ```bash
   git push origin --force --all
   ```
4. **Notify your team** - Let them know credentials were compromised

## 📧 Email Configuration Providers

This project is configured for Gmail, but you can use other providers:

### Gmail (Current Setup)
- Server: `smtp.gmail.com`
- Port: `587`
- TLS: `True`
- Requires app password

### SendGrid
- Server: `smtp.sendgrid.net`
- Port: `587`
- Username: `apikey`
- Password: Your SendGrid API key

### Mailgun
- Server: `smtp.mailgun.org`
- Port: `587`
- Username: Your Mailgun SMTP username
- Password: Your Mailgun SMTP password

Just update the values in your `.env` file!

---

**Remember: When in doubt, don't commit it. Secrets belong in `.env`, not in git!** 🔒
