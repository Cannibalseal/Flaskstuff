"""Profile management routes."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from app.models import db, User
from app.forms import ProfileForm, PageCustomizationForm
from app.utils import extract_colors_from_image
import os
from pathlib import Path

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def require_login():
    """Check if user is logged in."""
    if not session.get('logged_in'):
        return redirect(url_for('auth.login', next=request.url))
    return None


@profile_bp.route('/')
@profile_bp.route('/<username>')
def view_profile(username=None):
    """View user profile."""
    # If no username provided, show logged-in user's profile
    if not username:
        if not session.get('logged_in'):
            return redirect(url_for('auth.login'))
        user_id = session.get('user_id')
        user = db.session.get(User, user_id)
    else:
        user = User.query.filter_by(username=username).first()
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('public.index'))
    
    # Check if viewing own profile
    is_own_profile = session.get('user_id') == user.id
    
    # Check if user can customize page
    can_customize = (user.can_write_articles or user.is_admin) and is_own_profile
    
    return render_template('profile/view.jinja', user=user.to_dict(), is_own_profile=is_own_profile, can_customize=can_customize, user_obj=user)


@profile_bp.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    """Edit user profile."""
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('auth.login'))
    
    form = ProfileForm()
    
    if form.validate_on_submit():
        user.display_name = form.display_name.data or None
        user.email = form.email.data or None
        user.bio = form.bio.data or None
        user.location = form.location.data or None
        user.website = form.website.data or None
        user.twitter = form.twitter.data or None
        user.github = form.github.data or None
        user.youtube = form.youtube.data or None
        user.twitch = form.twitch.data or None
        user.linkedin = form.linkedin.data or None
        user.instagram = form.instagram.data or None
        user.discord = form.discord.data or None
        user.tiktok = form.tiktok.data or None
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{user.username}_{file.filename}")
                upload_folder = Path(__file__).resolve().parent.parent / 'static' / 'uploads' / 'profiles'
                upload_folder.mkdir(parents=True, exist_ok=True)
                file.save(upload_folder / filename)
                user.profile_picture = f"uploads/profiles/{filename}"
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.view_profile'))
    
    elif request.method == 'GET':
        # Populate form with existing data
        form.display_name.data = user.display_name
        form.email.data = user.email
        form.bio.data = user.bio
        form.location.data = user.location
        form.website.data = user.website
        form.twitter.data = user.twitter
        form.github.data = user.github
        form.youtube.data = user.youtube
        form.twitch.data = user.twitch
        form.linkedin.data = user.linkedin
        form.instagram.data = user.instagram
        form.discord.data = user.discord
        form.tiktok.data = user.tiktok
    
    return render_template('profile/edit.jinja', form=form, user=user.to_dict())

@profile_bp.route('/customize', methods=['GET', 'POST'])
def customize_page():
    """Customize user's page appearance (for article writers only)."""
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('auth.login'))
    
    # Check if user has permission to write articles
    if not user.can_write_articles and not user.is_admin:
        flash('You do not have permission to customize your page. Contact an admin for article writing access.', 'error')
        return redirect(url_for('profile.view_profile'))
    
    form = PageCustomizationForm()
    
    if form.validate_on_submit():
        # Handle background image upload
        if 'bg_image' in request.files:
            bg_image = request.files['bg_image']
            if bg_image and bg_image.filename:
                filename = secure_filename(bg_image.filename)
                # Create unique filename with timestamp
                timestamp = os.urandom(8).hex()
                file_ext = os.path.splitext(filename)[1]
                unique_filename = f'bg_{user.username}_{timestamp}{file_ext}'
                
                # Save to static/uploads/backgrounds/
                upload_folder = Path('app/static/uploads/backgrounds')
                upload_folder.mkdir(parents=True, exist_ok=True)
                filepath = upload_folder / unique_filename
                bg_image.save(filepath)
                
                # Extract colors from the image
                try:
                    colors = extract_colors_from_image(str(filepath))
                    user.custom_bg_color = colors['bg_color']
                    user.custom_text_color = colors['text_color']
                    user.custom_accent_color = colors['accent_color']
                    
                    # Update form data to show extracted colors
                    form.custom_bg_color.data = colors['bg_color']
                    form.custom_text_color.data = colors['text_color']
                    form.custom_accent_color.data = colors['accent_color']
                    
                    flash('Background image uploaded! Colors automatically extracted. You can still adjust them below.', 'success')
                except Exception as e:
                    flash(f'Image uploaded but color extraction failed: {str(e)}. Using default colors.', 'warning')
                
                # Delete old background image if exists
                if user.custom_bg_image:
                    old_path = Path('app/static') / user.custom_bg_image.lstrip('/')
                    if old_path.exists():
                        old_path.unlink()
                
                # Save relative path for URL generation
                user.custom_bg_image = f'uploads/backgrounds/{unique_filename}'
        
        # Save color preferences (either extracted or manually set)
        user.custom_bg_color = form.custom_bg_color.data or '#0a0e27'
        user.custom_text_color = form.custom_text_color.data or '#e2e8f0'
        user.custom_accent_color = form.custom_accent_color.data or '#06b6d4'
        user.custom_font_size = form.custom_font_size.data or '16px'
        user.custom_font_family = form.custom_font_family.data or 'system-ui'
        
        db.session.commit()
        flash('Page customization saved successfully!', 'success')
        return redirect(url_for('profile.view_profile'))
    
    elif request.method == 'GET':
        # Populate form with existing data
        form.custom_bg_color.data = user.custom_bg_color or '#0a0e27'
        form.custom_text_color.data = user.custom_text_color or '#e2e8f0'
        form.custom_accent_color.data = user.custom_accent_color or '#06b6d4'
        form.custom_font_size.data = user.custom_font_size or '16px'
        form.custom_font_family.data = user.custom_font_family or 'system-ui'
    
    return render_template('profile/customize.jinja', form=form, user=user.to_dict())