// Voting and Live Count Scripts

document.addEventListener('DOMContentLoaded', function() {
    // Handle candidate selection
    const candidateCards = document.querySelectorAll('.candidate-card');
    candidateCards.forEach(card => {
        card.addEventListener('click', function() {
            // Remove previous selection
            candidateCards.forEach(c => c.classList.remove('selected'));
            // Add selection to clicked card
            this.classList.add('selected');
            
            // Store selected candidate ID
            const candidateId = this.dataset.candidateId;
            document.getElementById('selected-candidate').value = candidateId;
        });
    });

    // Handle vote submission
    const voteForm = document.getElementById('vote-form');
    if (voteForm) {
        voteForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const candidateId = document.getElementById('selected-candidate').value;
            if (!candidateId) {
                alert('Please select a candidate');
                return;
            }

            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';

            // Submit vote
            const formData = new FormData();
            formData.append('candidate_id', candidateId);

            fetch('/cast-vote', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message with receipt info
                    const message = 'Vote cast successfully!\n\nYou can download your receipt from the dashboard.';
                    alert(message);
                    // Redirect to dashboard where they can download receipt
                    window.location.href = '/dashboard';
                } else {
                    alert(data.message || 'Failed to cast vote');
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            });
        });
    }

    // Live vote count updates (for admin dashboard)
    if (document.getElementById('live-vote-counts')) {
        updateVoteCounts();
        setInterval(updateVoteCounts, 5000); // Update every 5 seconds
    }
});

function updateVoteCounts() {
    fetch('/api/vote-counts')
        .then(response => response.json())
        .then(data => {
            if (data.votes) {
                // Update vote counts in the UI
                Object.keys(data.votes).forEach(candidateId => {
                    const element = document.getElementById(`vote-count-${candidateId}`);
                    if (element) {
                        element.textContent = data.votes[candidateId];
                    }
                });
                
                // Update total votes
                const totalElement = document.getElementById('total-votes');
                if (totalElement) {
                    totalElement.textContent = data.total || 0;
                }
            }
        })
        .catch(error => {
            console.error('Error updating vote counts:', error);
        });
}

// Confirmation dialogs
function confirmDelete(candidateId, candidateName) {
    if (confirm(`Are you sure you want to delete ${candidateName}? This action cannot be undone.`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/delete-candidate/${candidateId}`;
        document.body.appendChild(form);
        form.submit();
    }
}

// Auto-hide flash messages
setTimeout(function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        alert.style.transition = 'opacity 0.5s';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 500);
    });
}, 5000);


