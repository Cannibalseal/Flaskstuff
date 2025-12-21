"""WTForms definitions for the Flask blog application."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Optional, EqualTo, Email


class LoginForm(FlaskForm):
    """Login form for admin authentication."""
    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username is required'),
            Length(min=3, max=80, message='Username must be between 3 and 80 characters')
        ],
        render_kw={'placeholder': 'yourname', 'autocomplete': 'username'}
    )
    
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required'),
            Length(min=4, message='Password must be at least 4 characters')
        ],
        render_kw={'placeholder': '••••••', 'autocomplete': 'current-password'}
    )
    
    submit = SubmitField('Sign in')


class RegistrationForm(FlaskForm):
    """Registration form for new user signup."""
    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username is required'),
            Length(min=3, max=80, message='Username must be between 3 and 80 characters')
        ],
        render_kw={'placeholder': 'Choose a username', 'autocomplete': 'username'}
    )
    
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required'),
            Length(min=4, message='Password must be at least 4 characters')
        ],
        render_kw={'placeholder': 'Choose a password', 'autocomplete': 'new-password'}
    )
    
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password'),
            EqualTo('password', message='Passwords must match')
        ],
        render_kw={'placeholder': 'Confirm your password', 'autocomplete': 'new-password'}
    )
    
    submit = SubmitField('Create Account')


class ArticleForm(FlaskForm):
    """Form for creating and editing articles."""
    title = StringField(
        'Title',
        validators=[
            DataRequired(message='Title is required'),
            Length(min=3, max=200, message='Title must be between 3 and 200 characters')
        ],
        render_kw={'placeholder': 'Enter article title'}
    )
    
    summary = TextAreaField(
        'Summary',
        validators=[
            Optional(),
            Length(max=500, message='Summary must not exceed 500 characters')
        ],
        render_kw={'placeholder': 'Brief summary of the article', 'rows': 3}
    )
    
    content = TextAreaField(
        'Content',
        validators=[
            DataRequired(message='Content is required'),
            Length(min=10, message='Content must be at least 10 characters')
        ],
        render_kw={'placeholder': 'Article content (HTML allowed)', 'rows': 12}
    )
    
    published = BooleanField(
        'Published',
        default=True,
        description='Check to make article visible on the site'
    )
    
    submit = SubmitField('Save Article')


class ChangePasswordForm(FlaskForm):
    """Form for changing user password."""
    current_password = PasswordField(
        'Current Password',
        validators=[
            DataRequired(message='Current password is required')
        ],
        render_kw={'placeholder': '••••••', 'autocomplete': 'current-password'}
    )
    
    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired(message='New password is required'),
            Length(min=8, message='Password must be at least 8 characters')
        ],
        render_kw={'placeholder': '••••••', 'autocomplete': 'new-password'}
    )
    
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(message='Please confirm your password'),
            EqualTo('new_password', message='Passwords must match')
        ],
        render_kw={'placeholder': '••••••', 'autocomplete': 'new-password'}
    )
    
    submit = SubmitField('Change Password')


class NewsletterForm(FlaskForm):
    """Form for newsletter subscription."""
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Please enter a valid email address')
        ],
        render_kw={'placeholder': 'your.email@example.com', 'type': 'email'}
    )
    
    submit = SubmitField('Subscribe')


class ProfileForm(FlaskForm):
    """Form for editing user profile."""
    display_name = StringField(
        'Display Name',
        validators=[
            Optional(),
            Length(max=100, message='Display name must not exceed 100 characters')
        ],
        render_kw={'placeholder': 'Your display name'}
    )
    
    email = StringField(
        'Email',
        validators=[
            Optional(),
            Email(message='Please enter a valid email address'),
            Length(max=120, message='Email must not exceed 120 characters')
        ],
        render_kw={'placeholder': 'your.email@example.com', 'type': 'email'}
    )
    
    bio = TextAreaField(
        'Bio',
        validators=[
            Optional(),
            Length(max=500, message='Bio must not exceed 500 characters')
        ],
        render_kw={'placeholder': 'Tell us about yourself', 'rows': 4}
    )
    
    location = StringField(
        'Location',
        validators=[
            Optional(),
            Length(max=100, message='Location must not exceed 100 characters')
        ],
        render_kw={'placeholder': 'City, Country'}
    )
    
    website = StringField(
        'Website',
        validators=[
            Optional(),
            Length(max=200, message='Website URL must not exceed 200 characters')
        ],
        render_kw={'placeholder': 'https://yourwebsite.com'}
    )
    
    twitter = StringField(
        'Twitter',
        validators=[
            Optional(),
            Length(max=100, message='Twitter handle must not exceed 100 characters')
        ],
        render_kw={'placeholder': '@yourusername'}
    )
    
    github = StringField(
        'GitHub',
        validators=[
            Optional(),
            Length(max=100, message='GitHub username must not exceed 100 characters')
        ],
        render_kw={'placeholder': 'yourusername'}
    )
    
    youtube = StringField(
        'YouTube',
        validators=[
            Optional(),
            Length(max=100, message='YouTube channel/handle must not exceed 100 characters')
        ],
        render_kw={'placeholder': '@yourchannel or channel ID'}
    )
    
    twitch = StringField(
        'Twitch',
        validators=[
            Optional(),
            Length(max=100, message='Twitch username must not exceed 100 characters')
        ],
        render_kw={'placeholder': 'yourusername'}
    )
    
    linkedin = StringField(
        'LinkedIn',
        validators=[
            Optional(),
            Length(max=100, message='LinkedIn profile must not exceed 100 characters')
        ],
        render_kw={'placeholder': 'your-profile-name'}
    )
    
    instagram = StringField(
        'Instagram',
        validators=[
            Optional(),
            Length(max=100, message='Instagram handle must not exceed 100 characters')
        ],
        render_kw={'placeholder': '@yourusername'}
    )
    
    discord = StringField(
        'Discord',
        validators=[
            Optional(),
            Length(max=100, message='Discord username must not exceed 100 characters')
        ],
        render_kw={'placeholder': 'username#1234'}
    )
    
    tiktok = StringField(
        'TikTok',
        validators=[
            Optional(),
            Length(max=100, message='TikTok handle must not exceed 100 characters')
        ],
        render_kw={'placeholder': '@yourusername'}
    )
    
    submit = SubmitField('Update Profile')

class PageCustomizationForm(FlaskForm):
    """Form for customizing user's page appearance (for article writers)."""
    custom_bg_color = StringField(
        'Background Color',
        validators=[
            Optional(),
            Length(max=20, message='Color code must not exceed 20 characters')
        ],
        render_kw={'type': 'color', 'value': '#0a0e27'}
    )
    
    custom_text_color = StringField(
        'Text Color',
        validators=[
            Optional(),
            Length(max=20, message='Color code must not exceed 20 characters')
        ],
        render_kw={'type': 'color', 'value': '#e2e8f0'}
    )
    
    custom_accent_color = StringField(
        'Accent Color',
        validators=[
            Optional(),
            Length(max=20, message='Color code must not exceed 20 characters')
        ],
        render_kw={'type': 'color', 'value': '#06b6d4'}
    )
    
    custom_font_size = SelectField(
        'Font Size',
        choices=[
            ('12px', 'Extra Small (12px)'),
            ('14px', 'Small (14px)'),
            ('16px', 'Normal (16px)'),
            ('18px', 'Large (18px)'),
            ('20px', 'Extra Large (20px)'),
            ('22px', 'Huge (22px)'),
            ('1rem', '1rem (Responsive)'),
            ('1.1rem', '1.1rem (Responsive)'),
            ('1.2rem', '1.2rem (Responsive)'),
        ],
        validators=[Optional()],
        default='16px'
    )
    
    custom_font_family = SelectField(
        'Font Family',
        choices=[
            ('system-ui', 'System Default'),
            ('Arial, sans-serif', 'Arial'),
            ('Helvetica, sans-serif', 'Helvetica'),
            ('Georgia, serif', 'Georgia (Serif)'),
            ('Times New Roman, serif', 'Times New Roman'),
            ('Courier New, monospace', 'Courier New (Mono)'),
            ('Verdana, sans-serif', 'Verdana'),
            ('Trebuchet MS, sans-serif', 'Trebuchet MS'),
            ('Comic Sans MS, cursive', 'Comic Sans'),
            ('Impact, sans-serif', 'Impact'),
            ('Palatino, serif', 'Palatino'),
            ('Garamond, serif', 'Garamond'),
            ('Consolas, monospace', 'Consolas (Code)'),
            ('Monaco, monospace', 'Monaco (Code)'),
        ],
        validators=[Optional()],
        default='system-ui'
    )
    
    # Note: bg_image field will be handled in the route via request.files, not as a form field
    # This is because FileField doesn't play well with the color picker fields
    
    submit = SubmitField('Save Customization')