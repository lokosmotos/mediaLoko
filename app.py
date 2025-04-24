import os
import re
from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Tesseract configuration - works for both local and Render
try:
    # Try Render path first
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    pytesseract.get_tesseract_version()  # Test the installation
except:
    try:
        # Fallback to local path
        pytesseract.pytesseract.tesseract_cmd = 'tesseract'
        pytesseract.get_tesseract_version()
    except:
        print("Warning: Tesseract not found. OCR functionality will not work.")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_receipt_data(image_path):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))

        # Extract price (most likely the largest value with decimals)
        prices = re.findall(r"\d+\.\d{2}", text)
        total_price = max(prices, key=lambda x: float(x)) if prices else "Not found"

        # Extract date (basic format detection)
        date_match = re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", text)
        date_str = date_match.group() if date_match else "Not found"

        return {
            "text": text,
            "total_price": total_price,
            "date": date_str,
            "error": None
        }
    except Exception as e:
        return {
            "text": "",
            "total_price": "Error",
            "date": "Error",
            "error": str(e)
        }

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'receipt' not in request.files:
        return redirect(request.url)
    
    file = request.files['receipt']
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        data = extract_receipt_data(file_path)
        
        # Clean up file after processing
        if os.path.exists(file_path):
            os.remove(file_path)

        return render_template('result.html', data=data, filename=filename)
    
    return redirect(url_for('index'))

@app.errorhandler(413)
def request_entity_too_large(error):
    return render_template('upload.html', error="File too large (max 5MB)"), 413

@app.route('/healthcheck')
def healthcheck():
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
