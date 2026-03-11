from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from models.vote_model import VoteModel
from models.user_model import UserModel
from models.admin_model import AdminModel
from utils.pdf_generator import generate_vote_receipt
import io

vote_bp = Blueprint('vote', __name__)

@vote_bp.route('/vote')
def vote_page():
    """Voting page"""
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.login'))
    
    user = UserModel.get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        flash('User not found', 'error')
        return redirect(url_for('user.login'))
    
    if user['has_voted']:
        flash('You have already voted', 'info')
        return redirect(url_for('vote.results'))
    
    candidates = AdminModel.get_all_candidates()
    return render_template('vote.html', candidates=candidates)

@vote_bp.route('/cast-vote', methods=['POST'])
def cast_vote():
    """Cast a vote"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    user_id = session['user_id']
    candidate_id = request.form.get('candidate_id')
    
    if not candidate_id:
        return jsonify({'success': False, 'message': 'Please select a candidate'}), 400
    
    try:
        candidate_id = int(candidate_id)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid candidate ID'}), 400
    
    # Check if user has already voted
    if UserModel.has_user_voted(user_id):
        return jsonify({'success': False, 'message': 'You have already voted'}), 400
    
    success, message = VoteModel.cast_vote(user_id, candidate_id)
    if success:
        # Update session
        user = UserModel.get_user_by_id(user_id)
        if user:
            session['full_name'] = user['full_name']
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message}), 400

@vote_bp.route('/results')
def results():
    """Election results page"""
    results_data = VoteModel.get_results()
    total_votes = VoteModel.get_total_votes()
    
    # Group candidates by position
    results_by_position = {}
    for result in results_data:
        position = result['position']
        if position not in results_by_position:
            results_by_position[position] = []
        results_by_position[position].append(result)
    
    return render_template('result.html', 
                         results_by_position=results_by_position,
                         total_votes=total_votes)

@vote_bp.route('/api/vote-counts')
def vote_counts_api():
    """API endpoint for live vote counts"""
    if 'admin_id' not in session and 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    votes = VoteModel.get_votes_by_candidate()
    total = VoteModel.get_total_votes()
    
    return jsonify({
        'votes': votes,
        'total': total
    })


@vote_bp.route('/api/turnout')
def turnout_api():
    """API endpoint for voter turnout statistics"""
    if 'admin_id' not in session and 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    voters = UserModel.get_all_voters()
    total_voters = len(voters)
    voted_count = sum(1 for v in voters if v.get('has_voted'))
    not_voted = total_voters - voted_count

    return jsonify({
        'total_voters': total_voters,
        'voted_count': voted_count,
        'not_voted': not_voted
    })

@vote_bp.route('/download-receipt')
def download_receipt():
    """Download vote receipt as PDF"""
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.login'))
    
    user_id = session['user_id']
    receipt_data = VoteModel.get_vote_receipt(user_id)
    
    if not receipt_data:
        flash('No vote receipt found. You may not have voted yet.', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Generate PDF
    pdf_buffer = generate_vote_receipt(receipt_data)
    
    # Create filename
    filename = f"Vote_Receipt_{receipt_data['vote_id']:06d}.pdf"
    
    # Return PDF as download
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

