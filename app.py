from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import uuid
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'syida-secret-key'
DATA_FILE = 'data/candidates.csv'
os.makedirs('data', exist_ok=True)

# Ensure CSV file exists with headers
def init_csv():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'id', 'name', 'contact', 'position', 'branch', 'interview_date',
                'interview_status', 'outcome', 'willing', 'start_date', 'no_show',
                'no_show_reason', 'message_status', 'status', 'notes', 'available_from'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

# Load all candidates
def load_candidates():
    candidates = []
    try:
        with open(DATA_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            candidates = list(reader)
    except FileNotFoundError:
        pass
    return candidates

# Save all candidates
def save_all_candidates(candidates):
    fieldnames = [
        'id', 'name', 'contact', 'position', 'branch', 'interview_date',
        'interview_status', 'outcome', 'willing', 'start_date', 'no_show',
        'no_show_reason', 'message_status', 'status', 'notes', 'available_from'
    ]
    with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(candidates)

# Format date for display
def format_date(date_str):
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d %b %Y')
        except:
            return date_str
    return ""

app.jinja_env.filters['format_date'] = format_date

@app.route('/')
def index():
    candidates = load_candidates()
    return render_template('index.html', candidates=candidates)

@app.route('/candidate/<id>')
def view_candidate(id):
    candidates = load_candidates()
    candidate = next((c for c in candidates if c['id'] == id), None)
    if not candidate:
        flash('Candidate not found!', 'danger')
        return redirect(url_for('index'))
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
            'available_from': request.form.get('available_from', '')
        }
        
        candidates = load_candidates()
        candidates.append(candidate)
        save_all_candidates(candidates)
        
        flash('Candidate added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_candidate.html')

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_candidate(id):
    candidates = load_candidates()
    candidate = next((c for c in candidates if c['id'] == id), None)
    
    if not candidate:
        flash('Candidate not found!', 'danger')
        return redirect(url_for('index'))
    
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
            'available_from': request.form.get('available_from', '')
        })
        
        save_all_candidates(candidates)
        flash('Candidate updated successfully!', 'success')
        return redirect(url_for('view_candidate', id=id))
    
    return render_template('edit_candidate.html', candidate=candidate)

@app.route('/delete/<id>', methods=['GET', 'POST'])
def delete_candidate(id):
    candidates = load_candidates()
    candidate = next((c for c in candidates if c['id'] == id), None)
    
    if not candidate:
        flash('Candidate not found!', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        candidates = [c for c in candidates if c['id'] != id]
        save_all_candidates(candidates)
        flash('Candidate deleted successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('delete_candidate.html', candidate=candidate)

if __name__ == '__main__':
    init_csv()
    app.run(debug=True)
