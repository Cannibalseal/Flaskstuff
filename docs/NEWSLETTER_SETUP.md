# Newsletter Email Configuration

The newsletter feature is now set up! Here's what you need to configure to send actual emails:

## Email Configuration Options

### Option 1: Gmail (Recommended for Testing)

Set these environment variables or update `config/default.py`:

```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=your.email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=your.email@gmail.com
```

**Important for Gmail:**
- Use an "App Password" instead of your regular password
- Go to: Google Account → Security → 2-Step Verification → App Passwords
- Generate an app password for "Mail"

### Option 2: Other Email Providers

**SendGrid, Mailgun, AWS SES, etc.:**
Update the MAIL_* settings in `config/default.py` with your provider's SMTP settings.

### Option 3: Development/Testing (No Real Emails)

For development, emails will fail silently. To see email content during testing, you can:

1. Use a service like **Mailtrap.io** (fake SMTP for testing)
2. Print emails to console instead of sending (modify `utils.py`)

## How It Works

1. **Newsletter Signup**: Users can subscribe via the form in the footer
2. **Email Database**: Subscribers are stored in the `newsletter` table
3. **Auto-Send**: When you publish a new article (checked "Published"), an email is automatically sent to all subscribers
4. **View Subscribers**: Admin can view all subscribers at `/admin/newsletter/subscribers`

## Testing Without Email

If you don't configure email settings:
- Newsletter signups will still work and be saved to database
- Publishing articles will show a warning that email failed to send
- Everything else works normally

## Current Status

✅ Newsletter signup form (in footer)
✅ Database model for subscribers
✅ Admin page to view subscribers
✅ Auto-send emails when publishing articles
⚠️ Email sending requires SMTP configuration (see above)
