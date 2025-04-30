from flask import Flask, render_template, request, redirect, url_for
import csv
import uuid

app = Flask(__name__)
DATA_FILE = 'data/candidates.csv'

# Load candidates from the CSV file
def load_candidates():
    candidates = []
    try:
        with open(DATA_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                candidates.append(row)
    except FileNotFoundError:
        pass
    return candidates

# Save a candidate to the CSV file
def save_candidate(candidate):
    fieldnames = [
        'id', 'name', 'contact', 'position', 'branch', 'interview_date',
        'interview_status', 'outcome', 'willing', 'start_date', 'no_show',
        'no_show_reason', 'message_status', 'status', 'notes', 'available_from'
    ]
    with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if f.tell() == 0:  # If the file is empty, write the header row
            writer.writeheader()
        writer.writerow(candidate)

# Route for the home page, listing all candidates
@app.route('/')
def index():
    candidates = load_candidates()
    return render_template('index.html', candidates=candidates)

# Route for viewing individual candidate details
@app.route('/candidate/<id>')
def view_candidate(id):
    candidates = load_candidates()
    candidate = next((c for c in candidates if c['id'] == id), None)
    return render_template('candidate.html', candidate=candidate)

# Route for adding a new candidate
@app.route('/add', methods=['GET', 'POST'])
def add_candidate():
    if request.method == 'POST':
        candidate = {
            'id': str(uuid.uuid4()),  # Generate a unique ID
            'name': request.form['name'],
            'contact': request.form['contact'],
            'position': request.form['position'],
            'branch': request.form['branch'],
            'interview_date': request.form['interview_date'],
            'interview_status': request.form.get('interview_status', ''),
            'outcome': request.form.get('outcome', ''),
            'willing': request.form.get('willing', ''),
            'start_date': request.form.get('start_date', ''),
            'no_show': request.form.get('no_show', ''),
            'no_show_reason': request.form.get('no_show_reason', ''),
            'message_status': request.form.get('message_status', ''),
            'status': request.form.get('status', 'Active'),
            'notes': request.form.get('notes', ''),
            'available_from': request.form.get('available_from', '')
        }
        save_candidate(candidate)
        return redirect(url_for('index'))
    return render_template('add_candidate.html')

if __name__ == '__main__':
    app.run(debug=True)
