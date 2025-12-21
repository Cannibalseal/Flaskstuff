"""Profile management routes."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from app.models import db, User
from app.forms import ProfileForm
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
    
    return render_template('profile/view.jinja', user=user.to_dict(), is_own_profile=is_own_profile)


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
    
    return render_template('profile/edit.jinja', form=form, user=user.to_dict())
