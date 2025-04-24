from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import os
import re
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Helpers ---
def extract_receipt_data(image_path):
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
        "date": date_str
    }

# --- Routes ---
@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['receipt']
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        data = extract_receipt_data(file_path)

        return render_template('result.html', data=data, filename=filename)
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))
