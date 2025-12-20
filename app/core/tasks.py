"""Celery tasks for background processing."""

from flask import url_for
from flask_mail import Message
from app.core import mail
from app.models import Newsletter, Article


# Celery instance - will be initialized in init_celery
celery = None
send_welcome_email_task = None
send_article_notification_task = None


def init_celery(app):
    """Initialize Celery with Flask app."""
    from app.core.celery_app import make_celery
    global celery, send_welcome_email_task, send_article_notification_task
    
    celery = make_celery(app)
    
    # Define tasks after celery is initialized
    @celery.task(name='app.tasks.send_welcome_email_task')
    def _send_welcome_email(subscriber_email):
        """Background task to send welcome email to new subscriber."""
        subject = "Welcome to Sealy's Flask Blog Newsletter!"
        
        try:
            unsubscribe_url = url_for('public.newsletter_unsubscribe', email=subscriber_email, _external=True)
        except:
            unsubscribe_url = f"https://yourblog.com/newsletter/unsubscribe?email={subscriber_email}"
        
        body = f"""
Hello!

Thank you for subscribing to Sealy's Flask Blog newsletter!

You'll now receive email notifications whenever we publish new articles.

We're excited to have you as part of our community!

---
If you wish to unsubscribe at any time, click here:
{unsubscribe_url}

© 2025 Sealy's Flask Blog
"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #7c3aed, #06b6d4); color: white; padding: 30px; text-align: center; border-radius: 10px; }}
        .content {{ background: #f9f9f9; padding: 30px; margin: 20px 0; border-radius: 10px; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
        .unsubscribe {{ color: #999; font-size: 11px; margin-top: 20px; }}
        .unsubscribe a {{ color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 Welcome!</h1>
    </div>
    <div class="content">
        <h2>Thank you for subscribing!</h2>
        <p>You're now part of the Sealy's Flask Blog community.</p>
        <p>You'll receive email notifications whenever we publish new articles. We're excited to share our latest content with you!</p>
        <p style="color: #666; font-size: 14px; margin-top: 20px;">✨ Stay tuned for great content!</p>
    </div>
    <div class="footer">
        <p>© 2025 Sealy's Flask Blog</p>
        <p class="unsubscribe">
            Don't want to receive these emails?<br>
            <a href="{unsubscribe_url}">Unsubscribe</a>
        </p>
    </div>
</body>
</html>
"""
        
        msg = Message(
            subject=subject,
            recipients=[subscriber_email],
            body=body,
            html=html
        )
        
        try:
            mail.send(msg)
            return f"Welcome email sent to {subscriber_email}"
        except Exception as e:
            raise Exception(f"Failed to send welcome email to {subscriber_email}: {e}")
    
    
    @celery.task(name='app.tasks.send_article_notification_task')
    def _send_article_notification(article_id):
        """Background task to send article notification to all subscribers."""
        from app.models import db
        
        article = db.session.get(Article, article_id)
        if not article:
            return "Article not found"
        
        subscribers = Newsletter.query.filter_by(is_active=1).all()
        if not subscribers:
            return "No active subscribers"
        
        subject = f"New Article: {article.title}"
        
        try:
            article_url = url_for('public.article_detail', slug=article.slug, _external=True)
        except:
            article_url = f"https://yourblog.com/articles/{article.slug}/"
        
        sent_count = 0
        failed_count = 0
        
        with mail.connect() as conn:
            for subscriber in subscribers:
                try:
                    unsubscribe_url = url_for('public.newsletter_unsubscribe', email=subscriber.email, _external=True)
                except:
                    unsubscribe_url = f"https://yourblog.com/newsletter/unsubscribe?email={subscriber.email}"
                
                body = f"""
Hello!

We just published a new article on Sealy's Flask Blog:

{article.title}
{'-' * len(article.title)}

{article.summary or 'Check out this new article!'}

Read the full article here: {article_url}

---
To unsubscribe from these emails, click here: {unsubscribe_url}

© 2025 Sealy's Flask Blog
"""
                
                html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #7c3aed, #06b6d4); color: white; padding: 30px; text-align: center; border-radius: 10px; }}
        .content {{ background: #f9f9f9; padding: 30px; margin: 20px 0; border-radius: 10px; }}
        .button {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #7c3aed, #06b6d4); color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
        .unsubscribe {{ color: #999; font-size: 11px; margin-top: 20px; }}
        .unsubscribe a {{ color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📬 New Article Published!</h1>
    </div>
    <div class="content">
        <h2>{article.title}</h2>
        <p>{article.summary or 'Check out this new article!'}</p>
        <a href="{article_url}" class="button">Read Full Article</a>
    </div>
    <div class="footer">
        <p>© 2025 Sealy's Flask Blog</p>
        <p class="unsubscribe">
            Don't want to receive these emails?<br>
            <a href="{unsubscribe_url}">Unsubscribe</a>
        </p>
    </div>
</body>
</html>
"""
                
                msg = Message(
                    subject=subject,
                    recipients=[subscriber.email],
                    body=body,
                    html=html
                )
                
                try:
                    conn.send(msg)
                    sent_count += 1
                except Exception as e:
                    print(f"Failed to send email to {subscriber.email}: {e}")
                    failed_count += 1
                    continue
        
        return f"Article notifications sent: {sent_count} successful, {failed_count} failed"
    
    # Assign to module-level variables
    send_welcome_email_task = _send_welcome_email
    send_article_notification_task = _send_article_notification
    
    return celery
