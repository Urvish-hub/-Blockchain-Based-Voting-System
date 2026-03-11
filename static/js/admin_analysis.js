
// Poll API endpoints for live updates and render charts

const voteCountsUrl = '/api/vote-counts';
const turnoutUrl = '/api/turnout';
let votesChart = null;
let turnoutChart = null;

function buildVotesChart(labels, data) {
    const ctx = document.getElementById('votesChart').getContext('2d');
    if (votesChart) votesChart.destroy();
    votesChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Votes',
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.6)'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function buildTurnoutChart(voted, notVoted) {
    const ctx = document.getElementById('turnoutChart').getContext('2d');
    if (turnoutChart) turnoutChart.destroy();
    turnoutChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Voted', 'Not Voted'],
            datasets: [{
                data: [voted, notVoted],
                backgroundColor: ['rgba(75, 192, 192, 0.8)', 'rgba(201, 203, 207, 0.8)']
            }]
        },
        options: { responsive: true }
    });
}

async function fetchAndUpdate() {
    try {
        const [votesResp, turnoutResp] = await Promise.all([
            fetch(voteCountsUrl, { credentials: 'same-origin' }),
            fetch(turnoutUrl, { credentials: 'same-origin' })
        ]);

        if (!votesResp.ok || !turnoutResp.ok) {
            console.error('Failed to fetch APIs');
            return;
        }

        const votesJson = await votesResp.json();
        const turnoutJson = await turnoutResp.json();

        // Build labels and data using server-provided CANDIDATES mapping
        const candidates = window.CANDIDATES || [];
        let labels = [];
        let data = [];
        let idOrder = [];

        if (candidates.length) {
            candidates.forEach(c => {
                labels.push(c.name);
                idOrder.push(String(c.id));
                data.push(votesJson.votes[String(c.id)] || 0);
            });
        } else {
            idOrder = Object.keys(votesJson.votes);
            labels = idOrder.map(id => `Candidate ${id}`);
            data = idOrder.map(id => votesJson.votes[id] || 0);
        }

        buildVotesChart(labels, data);

        const voted = turnoutJson.voted_count || 0;
        const notVoted = turnoutJson.not_voted || 0;
        document.getElementById('totalVoters').textContent = turnoutJson.total_voters || 0;
        document.getElementById('votedCount').textContent = voted;
        buildTurnoutChart(voted, notVoted);

        // Update candidate progress bars and vote counts
        const totalVotes = votesJson.total || 0;
        idOrder.forEach((id, idx) => {
            const row = document.querySelector(`.candidate-row[data-candidate-id="${id}"]`);
            if (!row) return;
            const votes = votesJson.votes[id] || 0;
            const pct = totalVotes > 0 ? Math.round((votes / totalVotes) * 100) : 0;
            const countEl = row.querySelector('.votes-count');
            const fillEl = row.querySelector('.progress-fill');
            if (countEl) countEl.textContent = votes;
            if (fillEl) fillEl.style.width = pct + '%';
        });

    } catch (err) {
        console.error('Error updating charts', err);
    }
}

// On page load embed candidate labels as hidden elements so JS can map ids to names
function embedCandidateData() {
    const container = document.createElement('div');
    container.style.display = 'none';
    // If server rendered a global variable `window.CANDIDATES`, use it
    if (window.CANDIDATES && Array.isArray(window.CANDIDATES)) {
        window.CANDIDATES.forEach(c => {
            const span = document.createElement('span');
            span.setAttribute('data-candidate-id', String(c.id));
            span.textContent = c.name;
            container.appendChild(span);
        });
    }
    document.body.appendChild(container);
}

document.addEventListener('DOMContentLoaded', () => {
    embedCandidateData();
    fetchAndUpdate();
    // Poll every 5 seconds
    setInterval(fetchAndUpdate, 5000);
});
