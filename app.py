import os
from flask import Flask, request, send_file, render_template_string
import pandas as pd
from io import BytesIO
import openpyxl

app = Flask(__name__)

# HTML Template with sheet and column selection
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Windows Filename Cleaner</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #4361ee;
            --light-bg: #f5f7fa;
            --card-bg: #ffffff;
            --text: #2b2d42;
        }
        body {
            font-family: 'Poppins', sans-serif;
            background: var(--light-bg);
            min-height: 100vh;
            padding: 2rem;
            color: var(--text);
        }
        .container {
            background: var(--card-bg);
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }
        h1 {
            color: var(--primary);
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
        input, select, textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 1rem;
        }
        textarea {
            min-height: 150px;
            resize: vertical;
        }
        button {
            background: var(--primary);
            color: white;
            border: none;
            padding: 1rem;
            border-radius: 6px;
            font-size: 1rem;
            cursor: pointer;
            width: 100%;
            margin-top: 1rem;
            transition: all 0.2s;
        }
        button:hover {
            opacity: 0.9;
            transform: translateY(-2px);
        }
        .selectors {
            display: flex;
            gap: 1rem;
        }
        .selectors > div {
            flex: 1;
        }
        .hidden {
            display: none;
        }
        .icon {
            margin-right: 8px;
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <h1><i class="fas fa-file-excel icon"></i> Windows Filename Cleaner</h1>
        
        <form method="post" enctype="multipart/form-data">
            <!-- File Upload Section -->
            <div class="form-group">
                <label for="file"><i class="fas fa-file-upload icon"></i> Upload Excel File</label>
                <input type="file" id="file" name="file" accept=".xlsx,.xls">
            </div>
            
            <!-- Sheet and Column Selectors (hidden initially) -->
            <div id="excel-selectors" class="hidden">
                <div class="selectors">
                    <div class="form-group">
                        <label for="sheet"><i class="fas fa-table icon"></i> Select Sheet</label>
                        <select id="sheet" name="sheet"></select>
                    </div>
                    <div class="form-group">
                        <label for="column"><i class="fas fa-columns icon"></i> Select Column</label>
                        <select id="column" name="column"></select>
                    </div>
                </div>
            </div>
            
            <!-- Text Input Fallback -->
            <div class="form-group">
                <label for="text"><i class="fas fa-font icon"></i> Or Enter Filenames (one per line)</label>
                <textarea id="text" name="text" placeholder="my file.txt&#10;document 1.pdf&#10;image:1.jpg"></textarea>
            </div>
            
            <button type="submit"><i class="fas fa-magic icon"></i> Clean & Download</button>
        </form>
    </div>

    <script>
        // Show sheet/column selectors when file is selected
        document.getElementById('file').addEventListener('change', function(e) {
            const selectors = document.getElementById('excel-selectors');
            if (this.files.length) {
                selectors.classList.remove('hidden');
                
                const file = this.files[0];
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    const data = new Uint8Array(e.target.result);
                    const workbook = XLSX.read(data, {type: 'array'});
                    
                    // Populate sheet selector
                    const sheetSelect = document.getElementById('sheet');
                    sheetSelect.innerHTML = '';
                    workbook.SheetNames.forEach(sheet => {
                        const option = document.createElement('option');
                        option.value = sheet;
                        option.textContent = sheet;
                        sheetSelect.appendChild(option);
                    });
                    
                    // Populate column selector for first sheet
                    updateColumnSelector(workbook.Sheets[workbook.SheetNames[0]]);
                };
                
                reader.readAsArrayBuffer(file);
            } else {
                selectors.classList.add('hidden');
            }
        });
        
        // Update columns when sheet changes
        document.getElementById('sheet').addEventListener('change', function() {
            const fileInput = document.getElementById('file');
            if (fileInput.files.length) {
                const file = fileInput.files[0];
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    const data = new Uint8Array(e.target.result);
                    const workbook = XLSX.read(data, {type: 'array'});
                    const sheet = workbook.Sheets[document.getElementById('sheet').value];
                    updateColumnSelector(sheet);
                };
                
                reader.readAsArrayBuffer(file);
            }
        });
        
        function updateColumnSelector(sheet) {
            const json = XLSX.utils.sheet_to_json(sheet, {header: 1});
            const columnSelect = document.getElementById('column');
            columnSelect.innerHTML = '';
            
            if (json.length > 0) {
                json[0].forEach((col, index) => {
                    const option = document.createElement('option');
                    option.value = index;
                    option.textContent = col || `Column ${index + 1}`;
                    columnSelect.appendChild(option);
                });
            }
        }
    </script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
</body>
</html>"""

def clean_filename(filename):
    """Clean filename for Windows compatibility"""
    invalid_chars = r'<>:"/\|?* \x00-\x1F'
    return ''.join('_' if char in invalid_chars else char for char in str(filename)).strip('_')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Process text input
        if 'text' in request.form and request.form['text'].strip():
            filenames = [line.strip() for line in request.form['text'].split('\n') if line.strip()]
            cleaned = [[name, clean_filename(name)] for name in filenames]
            df = pd.DataFrame(cleaned, columns=['Original', 'Cleaned'])
        
        # Process Excel file
        elif 'file' in request.files:
            file = request.files['file']
            if file.filename:
                # Read the Excel file
                wb = openpyxl.load_workbook(file)
                
                # Get selected sheet and column
                sheet_name = request.form.get('sheet')
                col_index = int(request.form.get('column', 0))
                
                # Get data from selected sheet
                sheet = wb[sheet_name] if sheet_name else wb.active
                data = sheet.values
                cols = next(data)
                filenames = [row[col_index] for row in data]
                
                # Clean filenames
                cleaned = [[name, clean_filename(name)] for name in filenames if name]
                df = pd.DataFrame(cleaned, columns=['Original', 'Cleaned'])
        
        # Create output Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
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
