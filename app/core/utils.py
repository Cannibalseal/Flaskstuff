"""Utility functions for the Flask application."""

from flask import url_for
from flask_mail import Message
from app.core import mail
from app.models import Newsletter
import secrets


def send_welcome_email(subscriber):
    """Send welcome email to new newsletter subscriber.
    
    Args:
        subscriber: Newsletter object for the new subscriber
    """
    subject = "Welcome to Sealy's Flask Blog Newsletter!"
    
    # Generate unsubscribe URL
    try:
        unsubscribe_url = url_for('public.newsletter_unsubscribe', email=subscriber.email, _external=True)
    except:
        unsubscribe_url = f"https://yourblog.com/newsletter/unsubscribe?email={subscriber.email}"
    
    # Plain text body
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
    
    # HTML version
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
    
    # Send email
    msg = Message(
        subject=subject,
        recipients=[subscriber.email],
        body=body,
        html=html
    )
    
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send welcome email to {subscriber.email}: {e}")


def send_new_article_notification(article):
    """Send email notification to all newsletter subscribers about a new article.
    
    Args:
        article: Article object that was just published
    """
    # Get all active subscribers
    subscribers = Newsletter.query.filter_by(is_active=1).all()
    
    if not subscribers:
        return
    
    # Create email
    subject = f"New Article: {article.title}"
    
    # Get article URL (this assumes the function is called within app context)
    try:
        article_url = url_for('public.article_detail', slug=article.slug, _external=True)
    except:
        article_url = f"https://yourblog.com/articles/{article.slug}/"
    
    # Email body with unsubscribe template
    def get_email_body(subscriber_email):
        try:
            unsubscribe_url = url_for('public.newsletter_unsubscribe', email=subscriber_email, _external=True)
        except:
            unsubscribe_url = f"https://yourblog.com/newsletter/unsubscribe?email={subscriber_email}"
        
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
        return body, html
    
    # Send to all subscribers
    with mail.connect() as conn:
        for subscriber in subscribers:
            body, html = get_email_body(subscriber.email)
            msg = Message(
                subject=subject,
                recipients=[subscriber.email],
                body=body,
                html=html
            )
            try:
                conn.send(msg)
            except Exception as e:
                print(f"Failed to send email to {subscriber.email}: {e}")
                # Continue sending to other subscribers even if one fails
                continue
