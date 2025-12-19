"""WTForms definitions for the Flask blog application."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, Optional


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
