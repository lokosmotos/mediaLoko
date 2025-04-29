import os
from flask import Flask, request, send_file, render_template_string
import pandas as pd
from io import BytesIO

app = Flask(__name__)

# HTML Template - properly terminated with all content
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Windows Filename Cleaner</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 2rem;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 600px;
            padding: 2.5rem;
        }
        h1 {
            color: #4361ee;
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        input[type="file"], textarea, select {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 6px;
        }
        textarea {
            min-height: 120px;
        }
        button {
            background: #4361ee;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            width: 100%;
            cursor: pointer;
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <h1><i class="fas fa-file-excel"></i> Filename Cleaner</h1>
        <form method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label><i class="fas fa-file-upload"></i> Upload Excel File</label>
                <input type="file" name="file" accept=".xlsx,.xls">
            </div>
            <div class="form-group" id="column-selector" style="display:none;">
                <label><i class="fas fa-columns"></i> Select Column</label>
                <select name="column"></select>
            </div>
            <div class="form-group">
                <label><i class="fas fa-align-left"></i> Or Enter Filenames</label>
                <textarea name="text" placeholder="One filename per line"></textarea>
            </div>
            <button type="submit"><i class="fas fa-magic"></i> Clean & Download</button>
        </form>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <script>
        document.querySelector('input[name="file"]').addEventListener('change', function(e) {
            const selector = document.getElementById('column-selector');
            selector.style.display = e.target.files.length ? 'block' : 'none';
            
            if (e.target.files.length) {
                const file = e.target.files[0];
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    const data = new Uint8Array(e.target.result);
                    const workbook = XLSX.read(data, {type: 'array'});
                    const sheet = workbook.Sheets[workbook.SheetNames[0]];
                    const json = XLSX.utils.sheet_to_json(sheet, {header: 1});
                    
                    const select = document.querySelector('select[name="column"]');
                    select.innerHTML = '';
                    
                    if (json.length > 0) {
                        json[0].forEach((col, i) => {
                            const option = document.createElement('option');
                            option.value = i;
                            option.textContent = col || `Column ${i+1}`;
                            select.appendChild(option);
                        });
                    }
                };
                
                reader.readAsArrayBuffer(file);
            }
        });
    </script>
</body>
</html>"""

def clean_filename(filename):
    invalid_chars = r'<>:"/\|?* \x00-\x1F'
    return ''.join('_' if char in invalid_chars else char for char in str(filename)).strip('_')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'text' in request.form and request.form['text'].strip():
            filenames = [line.strip() for line in request.form['text'].split('\n') if line.strip()]
            cleaned = [[name, clean_filename(name)] for name in filenames]
            df = pd.DataFrame(cleaned, columns=['Original', 'Cleaned'])
        elif 'file' in request.files:
            file = request.files['file']
            if file.filename:
                df = pd.read_excel(file)
                if 'column' in request.form:
                    col_idx = int(request.form['column'])
                    col_name = df.columns[col_idx]
                    df['Cleaned'] = df.iloc[:, col_idx].apply(clean_filename)
        
        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='cleaned_filenames.xlsx'
        )
    
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
