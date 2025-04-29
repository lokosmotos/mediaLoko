import os
from flask import Flask, request, send_file, render_template_string
import pandas as pd
from io import BytesIO

app = Flask(__name__)

# HTML Form with Column Selection
HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Excel Filename Cleaner</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        select, textarea { width: 100%; padding: 8px; }
        button { background: #4CAF50; color: white; padding: 10px 15px; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Windows Filename Cleaner</h1>
    <form method="post" enctype="multipart/form-data">
        <div class="form-group">
            <label>Upload Excel File:</label>
            <input type="file" name="file" accept=".xlsx,.xls">
        </div>
        <div class="form-group">
            <label>Or paste filenames (one per line):</label>
            <textarea name="text" rows="5" placeholder="file1.txt\nfile2.jpg"></textarea>
        </div>
        <div class="form-group" id="column-selector" style="display:none;">
            <label>Select column to clean:</label>
            <select name="column"></select>
        </div>
        <button type="submit">Clean & Download</button>
    </form>

    <script>
        document.querySelector('input[name="file"]').addEventListener('change', function(e) {
            const columnSelector = document.getElementById('column-selector');
            columnSelector.style.display = e.target.files.length ? 'block' : 'none';
        });
    </script>
</body>
</html>
"""

def clean_filename(filename):
    """Replace invalid Windows characters and remove spaces."""
    invalid_chars = r'<>:"/\|?* \x00-\x1F'
    return ''.join('_' if char in invalid_chars else char for char in str(filename)).strip('_')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle text input
        if 'text' in request.form and request.form['text'].strip():
            filenames = [line.strip() for line in request.form['text'].split('\n') if line.strip()]
            cleaned = [[name, clean_filename(name)] for name in filenames]
            df = pd.DataFrame(cleaned, columns=['Original', 'Cleaned'])
            
        # Handle file upload
        elif 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return "No file selected", 400
                
            # Read Excel and get column names
            df = pd.read_excel(file)
            columns = df.columns.tolist()
            
            # If column not specified in form, return column selection
            if 'column' not in request.form or not request.form['column']:
                return render_template_string(HTML_FORM + f"""
                    <script>
                        const select = document.querySelector('select[name="column"]');
                        {columns}.forEach(col => {
                            const option = document.createElement('option');
                            option.value = col;
                            option.textContent = col;
                            select.appendChild(option);
                        });
                        document.getElementById('column-selector').style.display = 'block';
                    </script>
                """)
                
            # Clean specified column
            column = request.form['column']
            cleaned_col = df[column].apply(clean_filename)
            df['Cleaned'] = cleaned_col
            
        # Generate Excel output
        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='cleaned_filenames.xlsx'
        )
    
    return render_template_string(HTML_FORM)

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
