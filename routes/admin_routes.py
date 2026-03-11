from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.admin_model import AdminModel
from models.user_model import UserModel
from models.vote_model import VoteModel

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if 'admin_id' in session:
        return redirect(url_for('admin.admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('admin_login.html')
        
        admin, message = AdminModel.authenticate_admin(username, password)
        if admin:
            session['admin_id'] = admin['id']
            session['admin_username'] = admin['username']
            flash(message, 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash(message, 'error')
    
    return render_template('admin_login.html')

@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if 'admin_id' not in session:
        flash('Please login as admin first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    candidates = AdminModel.get_all_candidates()
    voters = UserModel.get_all_voters()
    total_voters = len(voters)
    voted_count = sum(1 for v in voters if v['has_voted'])
    
    return render_template('admin_dashboard.html', 
                         candidates=candidates, 
                         voters=voters,
                         total_voters=total_voters,
                         voted_count=voted_count)

@admin_bp.route('/admin/add-candidate', methods=['GET', 'POST'])
def add_candidate():
    """Add a new candidate"""
    if 'admin_id' not in session:
        flash('Please login as admin first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        party = request.form.get('party')
        position = request.form.get('position')
        bio = request.form.get('bio')
        
        if not all([name, party, position]):
            flash('Name, Party, and Position are required', 'error')
            return render_template('add_candidate.html')
        
        success, message = AdminModel.add_candidate(name, party, position, bio)
        if success:
            flash(message, 'success')
            return redirect(url_for('admin.manage_candidates'))
        else:
            flash(message, 'error')
    
    return render_template('add_candidate.html')

@admin_bp.route('/admin/manage-candidates')
def manage_candidates():
    """Manage candidates (view/edit/delete)"""
    if 'admin_id' not in session:
        flash('Please login as admin first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    candidates = AdminModel.get_all_candidates()
    return render_template('manage_candidates.html', candidates=candidates)

@admin_bp.route('/admin/edit-candidate/<int:candidate_id>', methods=['GET', 'POST'])
def edit_candidate(candidate_id):
    """Edit a candidate"""
    if 'admin_id' not in session:
        flash('Please login as admin first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    candidate = AdminModel.get_candidate_by_id(candidate_id)
    if not candidate:
        flash('Candidate not found', 'error')
        return redirect(url_for('admin.manage_candidates'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        party = request.form.get('party')
        position = request.form.get('position')
        bio = request.form.get('bio')
        
        if not all([name, party, position]):
            flash('Name, Party, and Position are required', 'error')
            return render_template('edit_candidate.html', candidate=candidate)
        
        success, message = AdminModel.update_candidate(candidate_id, name, party, position, bio)
        if success:
            flash(message, 'success')
            return redirect(url_for('admin.manage_candidates'))
        else:
            flash(message, 'error')
    
    return render_template('edit_candidate.html', candidate=candidate)

@admin_bp.route('/admin/delete-candidate/<int:candidate_id>', methods=['POST'])
def delete_candidate(candidate_id):
    """Delete a candidate"""
    if 'admin_id' not in session:
        flash('Please login as admin first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    success, message = AdminModel.delete_candidate(candidate_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin.manage_candidates'))



@admin_bp.route('/admin/voters-list')
def voters_list():
    """View all registered voters"""
    if 'admin_id' not in session:
        flash('Please login as admin first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    voters = UserModel.get_all_voters()
    total_voters = len(voters)
    voted_count = sum(1 for v in voters if v['has_voted'])
    not_voted_count = total_voters - voted_count
    
    return render_template('voters_list.html', 
                         voters=voters,
                         total_voters=total_voters,
                         voted_count=voted_count,
                         not_voted_count=not_voted_count)

@admin_bp.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin.admin_login'))


@admin_bp.route('/admin/analysis')
def admin_analysis():
    """Admin analysis page with charts and turnout stats"""
    if 'admin_id' not in session:
        flash('Please login as admin first', 'error')
        return redirect(url_for('admin.admin_login'))

    candidates = AdminModel.get_all_candidates()
    voters = UserModel.get_all_voters()
    total_voters = len(voters)
    voted_count = sum(1 for v in voters if v['has_voted'])
    total_votes = VoteModel.get_total_votes()

    return render_template('admin_analysis.html',
                           candidates=candidates,
                           total_voters=total_voters,
                           voted_count=voted_count,
                           total_votes=total_votes)


