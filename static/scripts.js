// Tab functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tabs
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab
            tab.classList.add('active');
            document.getElementById(tab.dataset.tab).classList.add('active');
        });
    });

    // Message modal
    document.querySelectorAll('.message-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const candidateId = btn.dataset.candidate;
            const candidateName = btn.closest('.candidate-card').querySelector('h3').textContent;
            
            document.getElementById('recipient').value = candidateName;
            document.getElementById('messageModal').style.display = 'flex';
        });
    });

    // Close modal
    document.querySelector('.close-modal').addEventListener('click', () => {
        document.getElementById('messageModal').style.display = 'none';
    });

    // Template selection
    document.getElementById('messageTemplate').addEventListener('change', (e) => {
        const templates = {
            'first_day_reminder': `Hi {{name}},\n\nThis is a friendly reminder that your first day with us is tomorrow. Please arrive by 9:00 AM at our main office.\n\nWe’re excited to welcome you and look forward to seeing you.\n\nBest regards,\nThe Hiring Team`,
            'no_show_followup': `Hi {{name}},\n\nWe noticed that you were unable to attend your first day yesterday. Please let us know if there were any issues or if you would like to reschedule.\n\nWe’re here to assist you.\n\nBest regards,\nThe Hiring Team`,
            'reschedule_request': `Hi {{name}},\n\nWe’d like to discuss rescheduling your start date. Kindly share your availability so we can make the necessary arrangements.\n\nLooking forward to your response.\n\nBest regards,\nThe Hiring Team`

        };
        
        if(e.target.value && templates[e.target.value]) {
            document.getElementById('messageContent').value = templates[e.target.value];
        }
    });

    // Rating stars
    document.querySelectorAll('.attitude-rating .fa-star').forEach(star => {
        star.addEventListener('click', function() {
            const rating = this.dataset.rating;
            const container = this.closest('.attitude-rating');
            
            container.querySelectorAll('.fa-star').forEach((s, index) => {
                if(index < rating) {
                    s.classList.add('filled');
                } else {
                    s.classList.remove('filled');
                }
            });
            
            // In a real app, you would save this to the server
            console.log(`Rated ${rating} stars`);
        });
    });
});

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    if(e.target === document.getElementById('messageModal')) {
        document.getElementById('messageModal').style.display = 'none';
    }
});
