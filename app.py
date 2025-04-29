import os
import re
from flask import Flask, request, send_file, render_template_string, flash, redirect
import pandas as pd
from io import BytesIO
import openpyxl
from openpyxl.utils import column_index_from_string

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# HTML Template with all requested features
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Filename Cleaner</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary: #4361ee;
            --danger: #dc3545;
            --light-bg: #f8f9fa;
            --dark: #212529;
        }
        body {
            font-family: 'Poppins', sans-serif;
            background: var(--light-bg);
            padding: 2rem;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        .tabs {
            display: flex;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid #dee2e6;
        }
        .tab-btn {
            padding: 0.75rem 1.5rem;
            background: none;
            border: none;
            cursor: pointer;
            font-weight: 500;
            color: #6c757d;
            position: relative;
        }
        .tab-btn.active {
            color: var(--primary);
        }
        .tab-btn.active:after {
            content: '';
            position: absolute;
            bottom: -1px;
            left: 0;
            width: 100%;
            height: 2px;
            background: var(--primary);
        }
        .tab-content {
            display: none;
            padding: 1rem 0;
        }
        .tab-content.active {
            display: block;
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
            border: 1px solid #ced4da;
            border-radius: 0.25rem;
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
            padding: 0.75rem 1.5rem;
            border-radius: 0.25rem;
            font-size: 1rem;
            cursor: pointer;
            width: 100%;
            margin-top: 1rem;
            transition: all 0.2s;
        }
        button:hover {
            opacity: 0.9;
        }
        .hidden {
            display: none;
        }
        .icon {
            margin-right: 0.5rem;
        }
        .range-selector {
            display: flex;
            gap: 1rem;
        }
        .range-selector > div {
            flex: 1;
        }
        .error {
            color: var(--danger);
            margin-bottom: 1rem;
            padding: 0.75rem;
            background: #f8d7da;
            border-radius: 0.25rem;
        }
        .removed-chars {
            margin-top: 1rem;
            padding: 0.75rem;
            background: #e2e3e5;
            border-radius: 0.25rem;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1><i class="fas fa-file-excel icon"></i> Advanced Filename Cleaner</h1>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="error">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('upload')">
                <i class="fas fa-file-upload"></i> Upload Excel
            </button>
            <button class="tab-btn" onclick="switchTab('paste')">
                <i class="fas fa-paste"></i> Paste Text
            </button>
        </div>
        
        <form method="post" enctype="multipart/form-data">
            <!-- Excel Upload Tab -->
            <div id="upload-tab" class="tab-content active">
                <div class="form-group">
                    <label><i class="fas fa-file-excel"></i> Excel File</label>
                    <input type="file" name="file" accept=".xlsx,.xls">
                </div>
                
                <div id="excel-options" class="hidden">
                    <div class="form-group">
                        <label><i class="fas fa-table"></i> Sheet</label>
                        <select name="sheet"></select>
                    </div>
                    
                    <div class="form-group">
                        <label><i class="fas fa-columns"></i> Column (A-Z)</label>
                        <select name="column">
                            <option value="">-- Select Column --</option>
                        </select>
                    </div>
                    
                    <div class="range-selector">
                        <div class="form-group">
                            <label><i class="fas fa-arrow-down"></i> Start Row</label>
                            <input type="number" name="start_row" min="1" value="7">
                        </div>
                        <div class="form-group">
                            <label><i class="fas fa-arrow-up"></i> End Row</label>
                            <input type="number" name="end_row" min="1">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" name="convert_gsheets" checked>
                            <i class="fas fa-cloud"></i> Convert Google Sheets formulas
                        </label>
                    </div>
                </div>
            </div>
            
            <!-- Paste Text Tab -->
            <div id="paste-tab" class="tab-content">
                <div class="form-group">
                    <label><i class="fas fa-align-left"></i> Paste Filenames (one per line)</label>
                    <textarea name="text" placeholder="Original filename 1.txt&#10;File#2?.jpg&#10;Another*file.pdf"></textarea>
                </div>
            </div>
            
            <button type="submit"><i class="fas fa-magic"></i> Clean & Export</button>
        </form>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <script>
        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName + '-tab').classList.add('active');
            
            // Update active tab button
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.currentTarget.classList.add('active');
        }
        
        // Handle file upload changes
        document.querySelector('input[name="file"]').addEventListener('change', function(e) {
            const optionsDiv = document.getElementById('excel-options');
            if (this.files.length) {
                optionsDiv.classList.remove('hidden');
                
                const file = this.files[0];
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    try {
                        const data = new Uint8Array(e.target.result);
                        const workbook = XLSX.read(data, {type: 'array'});
                        
                        // Populate sheet selector
                        const sheetSelect = document.querySelector('select[name="sheet"]');
                        sheetSelect.innerHTML = '';
                        workbook.SheetNames.forEach(sheet => {
                            const option = document.createElement('option');
                            option.value = sheet;
                            option.textContent = sheet;
                            sheetSelect.appendChild(option);
                        });
                        
                        // Populate column selector (A-Z)
                        const columnSelect = document.querySelector('select[name="column"]');
                        columnSelect.innerHTML = '<option value="">-- Select Column --</option>';
                        for (let i = 0; i < 26; i++) {
                            const letter = String.fromCharCode(65 + i);
                            const option = document.createElement('option');
                            option.value = letter;
                            option.textContent = 'Column ' + letter;
                            columnSelect.appendChild(option);
                        }
                        
                        // Set default end row
                        const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
                        const range = XLSX.utils.decode_range(firstSheet['!ref']);
                        document.querySelector('input[name="end_row"]').value = range.e.r + 1;
                    } catch (error) {
                        alert('Error reading Excel file: ' + error.message);
                    }
                };
                
                reader.onerror = function() {
                    alert('Error reading file');
                };
                
                reader.readAsArrayBuffer(file);
            } else {
                optionsDiv.classList.add('hidden');
            }
        });
    </script>
</body>
</html>"""

def clean_filename(name, show_removed=False):
    if not name or pd.isna(name):
        return ('', set()) if show_removed else ''
    
    original = str(name)
    # Pattern for invalid Windows filename characters
    invalid_chars = r'<>:"/\|?*\x00-\x1F'
    pattern = f'[{invalid_chars}]'
    
    # Find all special characters that will be removed
    removed = set(re.findall(pattern, original))
    
    # Clean the filename
    cleaned = re.sub(pattern, '_', original)
    cleaned = cleaned.strip('_').strip()
    
    if show_removed:
        return cleaned, removed
    return cleaned

def convert_gsheets_formula(value):
    """Convert Google Sheets formula to plain value if needed"""
    if isinstance(value, str) and value.startswith('='):
        try:
            # Simple conversion - for complex formulas you might need a better approach
            return value.lstrip('=').split('"')[1] if '"' in value else value.lstrip('=')
        except:
            return value
    return value

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Initialize variables
        filenames = []
        all_removed_chars = set()
        input_method = 'file' if 'file' in request.files and request.files['file'].filename else 'paste'
        
        try:
            if input_method == 'file':
                file = request.files['file']
                
                # Verify file
                if not file.filename.lower().endswith(('.xlsx', '.xls')):
                    flash('Only Excel files (.xlsx, .xls) are allowed')
                    return redirect(request.url)
                
                # Load workbook
                wb = openpyxl.load_workbook(file, read_only=True, data_only=False)
                
                # Get sheet
                sheet_name = request.form.get('sheet')
                sheet = wb[sheet_name] if sheet_name else wb.active
                
                # Get column and row range
                col_letter = request.form.get('column', 'A')
                col_idx = column_index_from_string(col_letter)
                start_row = int(request.form.get('start_row', 7))
                end_row = int(request.form.get('end_row', sheet.max_row))
                convert_gsheets = request.form.get('convert_gsheets') == 'on'
                
                # Process each cell in the range
                for row in sheet.iter_rows(
                    min_row=start_row,
                    max_row=end_row,
                    min_col=col_idx,
                    max_col=col_idx,
                    values_only=True
                ):
                    if row[0]:
                        value = row[0]
                        if convert_gsheets:
                            value = convert_gsheets_formula(value)
                        cleaned, removed = clean_filename(value, show_removed=True)
                        if cleaned:  # Only include non-empty results
                            filenames.append((str(value), cleaned))
                            all_removed_chars.update(removed)
            
            else:  # Paste method
                text = request.form.get('text', '')
                for line in text.split('\n'):
                    line = line.strip()
                    if line:
                        cleaned, removed = clean_filename(line, show_removed=True)
                        filenames.append((line, cleaned))
                        all_removed_chars.update(removed)
            
            # Create DataFrame with original, cleaned, and removed characters
            df = pd.DataFrame(filenames, columns=['Original', 'Cleaned'])
            
            # Add removed characters information
            removed_chars_str = ', '.join(f'"{c}"' for c in sorted(all_removed_chars)) if all_removed_chars else 'None'
            df['Removed_Special_Chars'] = removed_chars_str
            
            # Create output Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Cleaned_Filenames')
                
                # Add summary sheet
                summary = pd.DataFrame({
                    'Info': ['Total filenames processed', 'Special characters removed'],
                    'Value': [len(filenames), removed_chars_str]
                })
                summary.to_excel(writer, index=False, sheet_name='Summary')
            
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='cleaned_filenames.xlsx'
            )
            
        except Exception as e:
            flash(f'Error: {str(e)}')
            return redirect(request.url)
    
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
