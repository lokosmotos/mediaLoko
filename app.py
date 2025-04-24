import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Folder to store uploaded files
app.config['UPLOAD_FOLDER'] = 'uploads'
# Allowed file extensions (e.g., png, jpg, jpeg, pdf)
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'pdf'}
app.secret_key = 'your_secret_key_here'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# --- Helper Function to Check Allowed Extensions ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_receipt():
    if request.method == 'POST':
        # Check if the 'file' part is in the request
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        
        # Check if the user selected a file
        if file.filename == '':
            return 'No selected file'
        
        # Check if the file is allowed
        if file and allowed_file(file.filename):
            # Secure the filename (to avoid directory traversal attacks)
            filename = secure_filename(file.filename)
            # Save the file to the upload folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Render the uploaded file page, show download link
    return render_template('uploaded_file.html', filename=filename)

@app.route('/download/<filename>')
def download_file(filename):
    # This will send the file from the upload folder to the user for download
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/dashboard')
def dashboard():
    # Simple dashboard for now
    return render_template('dashboard.html')

# --- Running the App ---
if __name__ == '__main__':
    app.run(debug=True)
