"""Celery tasks for background processing."""

from flask import url_for, current_app
from flask_mail import Message
from app.core import mail
from app.models import Newsletter, Article
import logging
import threading

logger = logging.getLogger(__name__)

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


# Synchronous fallback functions (when Celery/Redis is not available)
def send_welcome_email_sync(subscriber_email):
    """Send welcome email synchronously (without Celery)."""
    subject = "🎉 Welcome to Sealy's Flask Blog!"
    
    try:
        unsubscribe_url = url_for('public.newsletter_unsubscribe', email=subscriber_email, _external=True)
        articles_url = url_for('public.articles', _external=True)
        home_url = url_for('public.index', _external=True)
    except:
        unsubscribe_url = f"https://yourblog.com/newsletter/unsubscribe?email={subscriber_email}"
        articles_url = "https://yourblog.com/articles/"
        home_url = "https://yourblog.com/"
    
    body = f"""
Welcome to Sealy's Flask Blog Newsletter!

Hi there! 👋

Thank you for subscribing to our newsletter. You'll now be the first to know whenever we publish new articles on development, technology, and programming.

What you can expect:
• Thoughtful articles on software development
• Tips and tutorials for Flask and Python
• Updates on new projects and experiments
• No spam, ever - just quality content

Browse our articles: {articles_url}
Visit our homepage: {home_url}

---
Best regards,
The Sealy's Flask Blog Team

If you wish to unsubscribe at any time: {unsubscribe_url}
© 2025 Sealy's Flask Blog
"""
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to Sealy's Flask Blog</title>
    <!--[if mso]>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            padding: 20px;
        }}
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        .header p {{
            font-size: 16px;
            opacity: 0.95;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .content h2 {{
            color: #1a1a1a;
            font-size: 22px;
            margin-bottom: 20px;
        }}
        .content p {{
            color: #4a4a4a;
            margin-bottom: 15px;
            font-size: 16px;
        }}
        .benefits {{
            background: #f8f9fa;
            border-left: 4px solid #7c3aed;
            padding: 20px;
            margin: 25px 0;
            border-radius: 6px;
        }}
        .benefits ul {{
            list-style: none;
            padding: 0;
        }}
        .benefits li {{
            padding: 8px 0;
            color: #333;
            font-size: 15px;
        }}
        .benefits li:before {{
            content: "✓ ";
            color: #06b6d4;
            font-weight: bold;
            margin-right: 8px;
        }}
        .button {{
            display: inline-block;
            padding: 14px 32px;
            background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%);
            color: white !important;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 16px;
            margin: 10px 8px;
            transition: transform 0.2s;
            text-align: center;
        }}
        .button:hover {{
            transform: translateY(-2px);
        }}
        .button-secondary {{
            background: #ffffff;
            color: #7c3aed !important;
            border: 2px solid #7c3aed;
        }}
        .cta-section {{
            text-align: center;
            margin: 30px 0;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
        .footer p {{
            margin: 8px 0;
        }}
        .social-links {{
            margin: 20px 0;
        }}
        .social-links a {{
            color: #7c3aed;
            text-decoration: none;
            margin: 0 10px;
            font-weight: 500;
        }}
        .unsubscribe {{
            font-size: 12px;
            color: #999;
            margin-top: 20px;
        }}
        .unsubscribe a {{
            color: #999;
            text-decoration: underline;
        }}
        @media only screen and (max-width: 600px) {{
            .email-container {{
                border-radius: 0;
            }}
            .header, .content, .footer {{
                padding: 25px 20px;
            }}
            .button {{
                display: block;
                margin: 10px 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>🎉 Welcome Aboard!</h1>
            <p>You're now part of the Sealy's Flask Blog community</p>
        </div>
        
        <div class="content">
            <h2>Hi there! 👋</h2>
            <p>Thank you for subscribing to our newsletter. We're thrilled to have you join our community of developers and tech enthusiasts!</p>
            
            <div class="benefits">
                <ul>
                    <li>Get notified about new articles on Flask, Python, and web development</li>
                    <li>Learn tips, tricks, and best practices from real projects</li>
                    <li>Stay updated on our latest experiments and tutorials</li>
                    <li>Join a community passionate about clean code and modern web development</li>
                </ul>
            </div>
            
            <p>We publish thoughtful, in-depth content regularly, and we promise to never spam your inbox. Every email we send will be worth your time.</p>
            
            <div class="cta-section">
                <a href="{articles_url}" class="button">Browse All Articles</a>
                <a href="{home_url}" class="button button-secondary">Visit Homepage</a>
            </div>
        </div>
        
        <div class="footer">
            <p style="font-weight: 600; color: #333; margin-bottom: 15px;">Sealy's Flask Blog</p>
            <p>Sharing knowledge, one article at a time.</p>
            
            <div class="social-links">
                <a href="{home_url}">Website</a> •
                <a href="{articles_url}">Articles</a> •
                <a href="{home_url}about/">About</a>
            </div>
            
            <p style="color: #999; margin-top: 20px;">© 2025 Sealy's Flask Blog. All rights reserved.</p>
            
            <div class="unsubscribe">
                <p>Don't want to receive these emails?<br>
                <a href="{unsubscribe_url}">Unsubscribe here</a></p>
            </div>
        </div>
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
        logger.info(f"Welcome email sent to {subscriber_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome email to {subscriber_email}: {e}")
        raise


def send_article_notification_sync(article_id):
    """Send article notification synchronously (without Celery)."""
    from app.models import db
    
    article = db.session.get(Article, article_id)
    if not article:
        raise Exception(f"Article with ID {article_id} not found")
    
    # Get all active subscribers
    subscribers = Newsletter.query.filter_by(is_active=1).all()
    if not subscribers:
        logger.info("No active subscribers to notify")
        return
    
    subject = f"📝 New Article: {article.title}"
    
    try:
        article_url = url_for('public.article_detail', slug=article.slug, _external=True)
        articles_url = url_for('public.articles', _external=True)
        home_url = url_for('public.index', _external=True)
    except:
        article_url = f"https://yourblog.com/articles/{article.slug}"
        articles_url = "https://yourblog.com/articles/"
        home_url = "https://yourblog.com/"
    
    sent_count = 0
    failed_count = 0
    
    with mail.connect() as conn:
        for subscriber in subscribers:
            try:
                unsubscribe_url = url_for('public.newsletter_unsubscribe', email=subscriber.email, _external=True)
            except:
                unsubscribe_url = f"https://yourblog.com/newsletter/unsubscribe?email={subscriber.email}"
            
            body = f"""
New Article Published on Sealy's Flask Blog!

{article.title}

{article.summary or 'Check out this new article!'}

Read the full article: {article_url}
Browse all articles: {articles_url}

---
Enjoying our content? Share it with your friends!

To unsubscribe from these notifications: {unsubscribe_url}
© 2025 Sealy's Flask Blog
"""
            
            html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article.title}</title>
    <!--[if mso]>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            padding: 20px;
        }}
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 24px;
            margin-bottom: 8px;
            font-weight: 700;
        }}
        .header p {{
            font-size: 14px;
            opacity: 0.95;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .article-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-left: 5px solid #7c3aed;
            padding: 30px;
            margin: 25px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }}
        .article-card h2 {{
            color: #1a1a1a;
            font-size: 24px;
            margin-bottom: 15px;
            line-height: 1.3;
        }}
        .article-card p {{
            color: #4a4a4a;
            font-size: 16px;
            margin-bottom: 20px;
            line-height: 1.7;
        }}
        .article-meta {{
            color: #7c3aed;
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
        }}
        .button {{
            display: inline-block;
            padding: 14px 32px;
            background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%);
            color: white !important;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 16px;
            margin: 10px 8px 10px 0;
            transition: transform 0.2s;
            text-align: center;
        }}
        .button:hover {{
            transform: translateY(-2px);
        }}
        .button-secondary {{
            background: #ffffff;
            color: #7c3aed !important;
            border: 2px solid #7c3aed;
        }}
        .cta-section {{
            text-align: center;
            margin: 30px 0;
        }}
        .divider {{
            height: 1px;
            background: linear-gradient(to right, transparent, #e0e0e0, transparent);
            margin: 30px 0;
        }}
        .info-box {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 25px 0;
            text-align: center;
        }}
        .info-box p {{
            color: #666;
            font-size: 14px;
            margin: 5px 0;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
        .footer p {{
            margin: 8px 0;
        }}
        .social-links {{
            margin: 20px 0;
        }}
        .social-links a {{
            color: #7c3aed;
            text-decoration: none;
            margin: 0 10px;
            font-weight: 500;
        }}
        .unsubscribe {{
            font-size: 12px;
            color: #999;
            margin-top: 20px;
        }}
        .unsubscribe a {{
            color: #999;
            text-decoration: underline;
        }}
        @media only screen and (max-width: 600px) {{
            .email-container {{
                border-radius: 0;
            }}
            .header, .content, .footer {{
                padding: 25px 20px;
            }}
            .article-card {{
                padding: 20px;
            }}
            .button {{
                display: block;
                margin: 10px 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>📝 New Article Published!</h1>
            <p>Fresh content just for you</p>
        </div>
        
        <div class="content">
            <div class="article-card">
                <div class="article-meta">✨ Latest Article</div>
                <h2>{article.title}</h2>
                <p>{article.summary or 'Check out this new article!'}</p>
            </div>
            
            <div class="cta-section">
                <a href="{article_url}" class="button">Read Full Article →</a>
            </div>
            
            <div class="divider"></div>
            
            <div class="info-box">
                <p style="font-weight: 600; color: #333; margin-bottom: 10px;">💡 Want More?</p>
                <p>Explore our complete collection of articles and tutorials.</p>
                <div style="margin-top: 15px;">
                    <a href="{articles_url}" class="button button-secondary">Browse All Articles</a>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p style="font-weight: 600; color: #333; margin-bottom: 15px;">Sealy's Flask Blog</p>
            <p>Thank you for being a valued subscriber!</p>
            
            <div class="social-links">
                <a href="{home_url}">Website</a> •
                <a href="{articles_url}">Articles</a> •
                <a href="{home_url}about/">About</a>
            </div>
            
            <p style="color: #999; margin-top: 20px;">© 2025 Sealy's Flask Blog. All rights reserved.</p>
            
            <div class="unsubscribe">
                <p>Don't want to receive these emails?<br>
                <a href="{unsubscribe_url}">Unsubscribe here</a></p>
            </div>
        </div>
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
                logger.error(f"Failed to send email to {subscriber.email}: {e}")
                failed_count += 1
    
    logger.info(f"Article notifications sent: {sent_count} successful, {failed_count} failed")
    return sent_count


# ========================================
# Threading-based Background Email Sending
# ========================================
# These functions send emails in background threads without requiring Redis/Celery

def send_welcome_email_async(app, subscriber_email):
    """Send welcome email in a background thread."""
    with app.app_context():
        try:
            send_welcome_email_sync(subscriber_email)
        except Exception as e:
            logger.error(f"Background thread error sending welcome email: {e}")


def send_article_notification_async(app, article_id):
    """Send article notifications in a background thread."""
    with app.app_context():
        try:
            send_article_notification_sync(article_id)
        except Exception as e:
            logger.error(f"Background thread error sending article notifications: {e}")


def send_welcome_email_background(subscriber_email):
    """
    Send welcome email in background thread (no Redis/Celery needed).
    This is perfect for free hosting tiers like Render.com.
    """
    from flask import current_app
    app = current_app._get_current_object()
    
    thread = threading.Thread(
        target=send_welcome_email_async,
        args=(app, subscriber_email),
        daemon=True
    )
    thread.start()
    logger.info(f"Started background thread to send welcome email to {subscriber_email}")


def send_article_notification_background(article_id):
    """
    Send article notifications in background thread (no Redis/Celery needed).
    This is perfect for free hosting tiers like Render.com.
    """
    from flask import current_app
    app = current_app._get_current_object()
    
    thread = threading.Thread(
        target=send_article_notification_async,
        args=(app, article_id),
        daemon=True
    )
    thread.start()
    logger.info(f"Started background thread to send article notifications for article {article_id}")
