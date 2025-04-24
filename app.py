import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Configuration
app.config['UPLOAD_FOLDER'] = 'tmp_uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure Tesseract (works for both local and Render)
try:
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    pytesseract.get_tesseract_version()  # Test installation
except:
    pytesseract.pytesseract.tesseract_cmd = 'tesseract'

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_receipt_data(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        
        # Extract total price
        prices = re.findall(r"\d+\.\d{2}", text)
        total_price = max(prices, key=lambda x: float(x)) if prices else "Not found"
        
        # Extract date
        date_match = re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", text)
        date_str = date_match.group() if date_match else "Not found"
        
        return {
            'text': text,
            'total_price': total_price,
            'date': date_str,
            'error': None
        }
    except Exception as e:
        return {
            'text': '',
            'total_price': 'Error',
            'date': 'Error',
            'error': str(e)
        }

@app.route('/', methods=['GET'])
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'receipt' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['receipt']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        data = extract_receipt_data(filepath)
        
        # Clean up file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return render_template('result.html', data=data)
    
    flash('Invalid file type. Allowed: PNG, JPG, JPEG, PDF')
    return redirect(url_for('index'))

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File too large (max 5MB)')
    return redirect(url_for('index')), 413

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
