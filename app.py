import os
from flask import Flask, request, send_file, render_template_string
import pandas as pd
from io import BytesIO
import openpyxl
from openpyxl.utils import get_column_letter

app = Flask(__name__)

# HTML Template with row 7 start and A-Z column selection
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
            
            <!-- Column Selector (hidden initially) -->
            <div id="column-selector" class="hidden">
                <div class="form-group">
                    <label for="column"><i class="fas fa-columns icon"></i> Select Column (A-Z)</label>
                    <select id="column" name="column">
                        <option value="">-- Select Column --</option>
                        <!-- Columns A-Z will be added by JavaScript -->
                    </select>
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
        // Show column selector when file is selected
        document.getElementById('file').addEventListener('change', function(e) {
            const selector = document.getElementById('column-selector');
            if (this.files.length) {
                selector.classList.remove('hidden');
                
                // Populate column selector with A-Z
                const columnSelect = document.getElementById('column');
                columnSelect.innerHTML = '<option value="">-- Select Column --</option>';
                
                for (let i = 0; i < 26; i++) {
                    const letter = String.fromCharCode(65 + i); // A-Z
                    const option = document.createElement('option');
                    option.value = letter;
                    option.textContent = `Column ${letter}`;
                    columnSelect.appendChild(option);
                }
            } else {
                selector.classList.add('hidden');
            }
        });
    </script>
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
                # Read the Excel file starting from row 7
                wb = openpyxl.load_workbook(file, read_only=True)
                sheet = wb.active
                
                # Get selected column letter (A-Z)
                col_letter = request.form.get('column', 'A')
                col_index = openpyxl.utils.column_index_from_string(col_letter) - 1
                
                # Read data from column starting at row 7
                filenames = []
                for row in sheet.iter_rows(min_row=7, values_only=True):
                    if len(row) > col_index and row[col_index]:
                        filenames.append(row[col_index])
                
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
