from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import uuid
import os
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
DATA_FILE = 'data/candidates.csv'
os.makedirs('data', exist_ok=True)

# Initialize CSV with headers if not exists
def init_csv():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'id', 'name', 'contact', 'position', 'branch', 'interview_date',
                'interview_status', 'outcome', 'willing', 'start_date', 'no_show',
                'no_show_reason', 'message_status', 'status', 'notes', 'available_from',
                'attitude_rating', 'last_contact'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

# Load all candidates from CSV
def load_candidates():
    candidates = []
    try:
        with open(DATA_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            candidates = list(reader)
    except FileNotFoundError:
        pass
    return candidates

# Save all candidates to CSV
def save_all_candidates(candidates):
    fieldnames = [
        'id', 'name', 'contact', 'position', 'branch', 'interview_date',
        'interview_status', 'outcome', 'willing', 'start_date', 'no_show',
        'no_show_reason', 'message_status', 'status', 'notes', 'available_from',
        'attitude_rating', 'last_contact'
    ]
    with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(candidates)

# Get dashboard statistics
def get_dashboard_stats(candidates):
    stats = {
        'total_candidates': len(candidates),
        'upcoming_interviews': 0,
        'hired': 0,
        'interviewed': 0,
        'pending': 0,
        'recent_activities': []
    }
    
    today = datetime.today().date()
    
    for candidate in candidates:
        # Count statuses
        if candidate.get('status', '').lower() == 'hired':
            stats['hired'] += 1
        elif candidate.get('interview_status', '').lower() == 'completed':
            stats['interviewed'] += 1
        else:
            stats['pending'] += 1
            
        # Count upcoming interviews
        if candidate.get('interview_date'):
            try:
                interview_date = datetime.strptime(candidate['interview_date'], '%Y-%m-%d').date()
                if today <= interview_date <= datetime.fromordinal((today.toordinal() + 7)).date():
                    stats['upcoming_interviews'] += 1
            except ValueError:
                pass
    
    # Generate recent activities (last 5)
    for candidate in candidates[-5:][::-1]:  # Get last 5 and reverse order
        activity = {
            'icon': 'user-check' if candidate.get('status', '').lower() == 'hired' else 'calendar-alt',
            'description': f"{candidate['name']} - {candidate['position']}",
            'time': "Today" if candidate.get('last_contact') == datetime.today().strftime('%Y-%m-%d') else "Recently",
            'type': 'hire' if candidate.get('status', '').lower() == 'hired' else 'interview'
        }
        stats['recent_activities'].append(activity)
    
    return stats

# Format date for display
def format_date(date_str):
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d %b %Y')
        except:
            return date_str
    return ""

app.jinja_env.filters['format_date'] = format_date

# Routes
@app.route('/')
def index():
    candidates = load_candidates()
    stats = get_dashboard_stats(candidates)
    return render_template('index.html', 
                         candidates=candidates,
                         stats=stats,
                         recent_candidates=candidates[-3:])

@app.route('/candidates')
def candidate_list():
    candidates = load_candidates()
    return render_template('candidate_list.html', candidates=candidates)

@app.route('/candidate/<id>')
def view_candidate(id):
    candidates = load_candidates()
    candidate = next((c for c in candidates if c['id'] == id), None)
    if not candidate:
        flash('Candidate not found!', 'danger')
        return redirect(url_for('candidate_list'))
    return render_template('view_candidate.html', candidate=candidate)

@app.route('/add', methods=['GET', 'POST'])
def add_candidate():
    if request.method == 'POST':
        candidate = {
            'id': str(uuid.uuid4()),
            'name': request.form.get('name', '').strip(),
            'contact': request.form.get('contact', '').strip(),
            'position': request.form.get('position', '').strip(),
            'branch': request.form.get('branch', '').strip(),
            'interview_date': request.form.get('interview_date', ''),
            'interview_status': request.form.get('interview_status', 'Pending'),
            'outcome': request.form.get('outcome', ''),
            'willing': request.form.get('willing', ''),
            'start_date': request.form.get('start_date', ''),
            'no_show': request.form.get('no_show', 'No'),
            'no_show_reason': request.form.get('no_show_reason', '').strip(),
            'message_status': request.form.get('message_status', 'Not Sent'),
            'status': request.form.get('status', 'Active'),
            'notes': request.form.get('notes', '').strip(),
            'available_from': request.form.get('available_from', ''),
            'attitude_rating': request.form.get('attitude_rating', '3'),
            'last_contact': datetime.today().strftime('%Y-%m-%d')
        }
        
        candidates = load_candidates()
        candidates.append(candidate)
        save_all_candidates(candidates)
        
        flash(f"{candidate['name']} added successfully!", 'success')
        return redirect(url_for('candidate_list'))
    
    return render_template('add_candidate.html')

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_candidate(id):
    candidates = load_candidates()
    candidate = next((c for c in candidates if c['id'] == id), None)
    
    if not candidate:
        flash('Candidate not found!', 'danger')
        return redirect(url_for('candidate_list'))
    
    if request.method == 'POST':
        candidate.update({
            'name': request.form.get('name', '').strip(),
            'contact': request.form.get('contact', '').strip(),
            'position': request.form.get('position', '').strip(),
            'branch': request.form.get('branch', '').strip(),
            'interview_date': request.form.get('interview_date', ''),
            'interview_status': request.form.get('interview_status', 'Pending'),
            'outcome': request.form.get('outcome', ''),
            'willing': request.form.get('willing', ''),
            'start_date': request.form.get('start_date', ''),
            'no_show': request.form.get('no_show', 'No'),
            'no_show_reason': request.form.get('no_show_reason', '').strip(),
            'message_status': request.form.get('message_status', 'Not Sent'),
            'status': request.form.get('status', 'Active'),
            'notes': request.form.get('notes', '').strip(),
            'available_from': request.form.get('available_from', ''),
            'attitude_rating': request.form.get('attitude_rating', '3'),
            'last_contact': datetime.today().strftime('%Y-%m-%d')
        })
        
        save_all_candidates(candidates)
        flash(f"{candidate['name']} updated successfully!", 'success')
        return redirect(url_for('view_candidate', id=id))
    
    return render_template('edit_candidate.html', candidate=candidate)

@app.route('/delete/<id>', methods=['POST'])
def delete_candidate(id):
    candidates = load_candidates()
    candidate = next((c for c in candidates if c['id'] == id), None)
    
    if not candidate:
        flash('Candidate not found!', 'danger')
    else:
        candidates = [c for c in candidates if c['id'] != id]
        save_all_candidates(candidates)
        flash(f"{candidate['name']} deleted successfully!", 'success')
    
    return redirect(url_for('candidate_list'))

if __name__ == '__main__':
    init_csv()
    app.run(debug=True)
