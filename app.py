import os
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import openpyxl
from io import BytesIO
import pandas as pd

app = Flask(__name__)

# Configure upload folder (for temporary storage)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_filename(filename):
    """Replace invalid Windows characters and remove spaces."""
    invalid_chars = r'<>:"/\|?* \x00-\x1F'
    cleaned = ''.join('_' if char in invalid_chars else char for char in filename)
    return cleaned.strip('_')

@app.route('/')
def home():
    return "Windows Filename Cleaner - Upload Excel or enter names"

@app.route('/clean', methods=['POST'])
def clean_filenames():
    # Handle direct text input (one filename per line)
    if 'text' in request.form:
        filenames = request.form['text'].split('\n')
        cleaned = [{"Original": name, "Cleaned": clean_filename(name)} for name in filenames if name.strip()]
        
        # Create Excel in memory
        output = BytesIO()
        df = pd.DataFrame(cleaned)
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='cleaned_filenames.xlsx'
        )

    # Handle Excel file upload
    elif 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Read Excel (assuming filenames are in column A)
            wb = openpyxl.load_workbook(filepath)
            sheet = wb.active
            filenames = [cell.value for cell in sheet['A'] if cell.value]
            
            # Clean and generate output
            cleaned = [{"Original": name, "Cleaned": clean_filename(str(name))} for name in filenames]
            
            # Create new Excel
            output = BytesIO()
            df = pd.DataFrame(cleaned)
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            
            # Clean up
            os.remove(filepath)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='cleaned_filenames.xlsx'
            )
    
    return jsonify({"error": "Invalid request"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
