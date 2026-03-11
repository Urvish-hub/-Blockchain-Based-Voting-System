from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user_model import UserModel
from models.vote_model import VoteModel

user_bp = Blueprint('user', __name__)

@user_bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        if not all([username, email, password, full_name]):
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        success, message = UserModel.register_user(username, email, password, full_name)
        if success:
            flash(message, 'success')
            return redirect(url_for('user.login'))
        else:
            flash(message, 'error')
    
    return render_template('register.html')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if 'user_id' in session:
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html')
        
        user, message = UserModel.authenticate_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            flash(message, 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash(message, 'error')
    
    return render_template('login.html')

@user_bp.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.login'))
    
    user = UserModel.get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        flash('User not found', 'error')
        return redirect(url_for('user.login'))
    
    # Get user statistics
    stats = UserModel.get_user_statistics(session['user_id'])
    
    # Get vote history (latest vote)
    vote_history = UserModel.get_vote_history(session['user_id'])
    latest_vote = vote_history[0] if vote_history else None
    
    return render_template('dashboard.html', user=user, stats=stats, latest_vote=latest_vote)

@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """User profile management"""
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.login'))
    
    user = UserModel.get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        flash('User not found', 'error')
        return redirect(url_for('user.login'))
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        
        if not all([full_name, email]):
            flash('All fields are required', 'error')
            return render_template('profile.html', user=user)
        
        success, message = UserModel.update_profile(session['user_id'], full_name, email)
        if success:
            flash(message, 'success')
            # Update session
            user = UserModel.get_user_by_id(session['user_id'])
            if user:
                session['full_name'] = user['full_name']
            return redirect(url_for('user.profile'))
        else:
            flash(message, 'error')
    
    return render_template('profile.html', user=user)

@user_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    """User account settings"""
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.login'))
    
    user = UserModel.get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        flash('User not found', 'error')
        return redirect(url_for('user.login'))
    
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([old_password, new_password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('settings.html', user=user)
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('settings.html', user=user)
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('settings.html', user=user)
        
        success, message = UserModel.change_password(session['user_id'], old_password, new_password)
        if success:
            flash(message, 'success')
            return redirect(url_for('user.settings'))
        else:
            flash(message, 'error')
    
    return render_template('settings.html', user=user)

@user_bp.route('/vote-history')
def vote_history():
    """User vote history"""
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.login'))
    
    user = UserModel.get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        flash('User not found', 'error')
        return redirect(url_for('user.login'))
    
    vote_history = UserModel.get_vote_history(session['user_id'])
    stats = UserModel.get_user_statistics(session['user_id'])
    
    return render_template('vote_history.html', user=user, vote_history=vote_history, stats=stats)

@user_bp.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('user.index'))

