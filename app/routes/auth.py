"""Authentication routes for login, logout, and password management."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db, User
from app.forms import LoginForm, ChangePasswordForm, RegistrationForm
from config import cfg

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Check user in database
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['logged_in'] = True
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = bool(user.is_admin)
            session['can_write_articles'] = bool(user.can_write_articles)
            
            # Check if password change is required
            if user.must_change_password:
                flash('Please change your password before continuing.', 'info')
                return redirect(url_for('auth.change_password'))
            
            flash('Successfully logged in!', 'success')
            next_page = request.args.get('next') or url_for('admin.dashboard')
            return redirect(next_page)
        
        flash('Invalid credentials.', 'error')
    elif request.method == 'POST':
        # Form validation failed - flash all errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'error')
    
    return render_template('auth/login.jinja', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    # Redirect if already logged in
    if session.get('logged_in'):
        return redirect(url_for('public.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken. Please choose another.', 'error')
        else:
            # Create new user (non-admin, no password change required)
            new_user = User(
                username=username,
                is_admin=0,
                must_change_password=0
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            # Auto-login after registration
            session['logged_in'] = True
            session['user_id'] = new_user.id
            session['username'] = new_user.username
            session['is_admin'] = False
            session['can_write_articles'] = False
            
            flash('Account created successfully! Welcome!', 'success')
            
            # Redirect to the page they came from, or articles page
            next_page = request.args.get('next') or url_for('public.articles')
            return redirect(next_page)
    elif request.method == 'POST':
        # Form validation failed - flash all errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'error')
    
    return render_template('auth/register.jinja', form=form)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    """Handle password change."""
    # Require login
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('auth.login'))
    
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        
        # Verify current password
        if not user.check_password(current_password):
            flash('Current password is incorrect.', 'error')
        else:
            # Update password
            user.set_password(new_password)
            user.must_change_password = 0
            db.session.commit()
            
            # Clear all cached objects to force fresh database queries
            db.session.expire_all()
            db.session.close()
            
            flash('Password changed successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
    elif request.method == 'POST':
        # Form validation failed - flash all errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'error')
    
    # Check if this is a forced password change
    is_required = user.must_change_password == 1
    return render_template('auth/change_password.jinja', form=form, is_required=is_required)


@auth_bp.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    flash('Successfully logged out.', 'info')
    return redirect(url_for('public.index'))
