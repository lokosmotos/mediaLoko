import os
import re
from flask import Flask, request, send_file, render_template_string, flash, redirect
import pandas as pd
from io import BytesIO
import openpyxl
from openpyxl.utils import get_column_letter

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Enhanced Netflix-style HTML template
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ultimate Filename Cleaner</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Netflix+Sans:wght@300;400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --netflix-red: #e50914;
            --netflix-dark: #141414;
            --netflix-light: #f3f3f3;
            --netflix-gray: #808080;
            --netflix-card: #181818;
        }
        body {
            margin: 0;
            padding: 0;
            font-family: 'Netflix Sans', sans-serif;
            background-color: var(--netflix-dark);
            color: var(--netflix-light);
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(to bottom, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0) 100%);
            padding: 2rem 0;
            text-align: center;
        }
        .logo {
            color: var(--netflix-red);
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }
        .tagline {
            color: var(--netflix-gray);
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }
        .container {
            max-width: 800px;
            margin: 0 auto 3rem;
            padding: 2rem;
            background: var(--netflix-card);
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        }
        .tabs {
            display: flex;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid #333;
        }
        .tab-btn {
            padding: 1rem 2rem;
            background: none;
            border: none;
            color: var(--netflix-gray);
            font-size: 1.1rem;
            font-weight: 500;
            cursor: pointer;
            position: relative;
            transition: all 0.3s;
        }
        .tab-btn.active {
            color: var(--netflix-light);
        }
        .tab-btn.active:after {
            content: '';
            position: absolute;
            bottom: -1px;
            left: 0;
            width: 100%;
            height: 3px;
            background: var(--netflix-red);
        }
        .tab-content {
            display: none;
            animation: fadeIn 0.5s;
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
            color: var(--netflix-gray);
        }
        input, select, textarea {
            width: 100%;
            padding: 0.8rem;
            background: #333;
            border: 1px solid #444;
            border-radius: 4px;
            color: var(--netflix-light);
            font-size: 1rem;
            transition: border 0.3s;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: var(--netflix-red);
        }
        textarea {
            min-height: 150px;
            resize: vertical;
        }
        .char-options {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 0.8rem;
            margin: 1.5rem 0;
            padding: 1.5rem;
            background: rgba(51,51,51,0.5);
            border-radius: 8px;
        }
        .char-options label {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            cursor: pointer;
            padding: 0.5rem;
            border-radius: 4px;
            transition: background 0.2s;
        }
        .char-options label:hover {
            background: rgba(255,255,255,0.1);
        }
        .btn {
            background: var(--netflix-red);
            color: white;
            border: none;
            padding: 1rem;
            border-radius: 4px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            margin-top: 1rem;
            transition: all 0.3s;
        }
        .btn:hover {
            background: #f6121d;
            transform: translateY(-2px);
        }
        .btn i {
            margin-right: 0.5rem;
        }
        .flash {
            padding: 1rem;
            margin-bottom: 1.5rem;
            background: rgba(229,9,20,0.2);
            border-left: 4px solid var(--netflix-red);
            border-radius: 0 4px 4px 0;
        }
        footer {
            text-align: center;
            padding: 2rem;
            color: var(--netflix-gray);
            font-size: 0.9rem;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .preview-box {
            margin-top: 2rem;
            padding: 1.5rem;
            background: rgba(51,51,51,0.3);
            border-radius: 8px;
            display: none;
        }
        .preview-title {
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--netflix-red);
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">FilenameCleaner</div>
        <div class="tagline">Make your filenames Windows-friendly with style</div>
    </div>
    
    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('upload')">
                <i class="fas fa-file-upload"></i> Upload File
            </button>
            <button class="tab-btn" onclick="switchTab('paste')">
                <i class="fas fa-paste"></i> Paste Text
            </button>
        </div>
        
        <form method="post" enctype="multipart/form-data">
            <!-- File Upload Tab -->
            <div id="upload-tab" class="tab-content active">
                <div class="form-group">
                    <label for="file"><i class="fas fa-file-excel"></i> Select Excel/CSV File</label>
                    <input type="file" id="file" name="file" accept=".csv,.xlsx,.xls">
                </div>
                
                <div id="excel-options" class="hidden">
                    <div class="form-group">
                        <label for="sheet"><i class="fas fa-table"></i> Worksheet</label>
                        <select id="sheet" name="sheet"></select>
                    </div>
                    
                    <div class="form-group">
                        <label for="column"><i class="fas fa-columns"></i> Column (A-Z)</label>
                        <select id="column" name="column"></select>
                    </div>
                    
                    <div style="display: flex; gap: 1rem;">
                        <div class="form-group" style="flex: 1;">
                            <label for="start_row"><i class="fas fa-arrow-down"></i> Start Row</label>
                            <input type="number" id="start_row" name="start_row" min="1" value="7">
                        </div>
                        <div class="form-group" style="flex: 1;">
                            <label for="end_row"><i class="fas fa-arrow-up"></i> End Row</label>
                            <input type="number" id="end_row" name="end_row" min="1">
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Paste Text Tab -->
            <div id="paste-tab" class="tab-content">
                <div class="form-group">
                    <label for="text"><i class="fas fa-align-left"></i> Paste Filenames (one per line)</label>
                    <textarea id="text" name="text" placeholder="Original filename 1.txt&#10;File#2?.jpg&#10;Another*file.pdf"></textarea>
                </div>
            </div>
            
            <div class="char-options">
                <h3 style="grid-column: 1 / -1; margin: 0 0 1rem; color: var(--netflix-light);">Special Character Handling</h3>
                <label>
                    <input type="checkbox" name="keep_slash" checked>
                    <i class="fas fa-slash"></i> Forward Slash (/)
                </label>
                <label>
                    <input type="checkbox" name="keep_backslash" checked>
                    <i class="fas fa-backslash"></i> Backslash (\\)
                </label>
                <label>
                    <input type="checkbox" name="keep_colon" checked>
                    <i class="fas fa-colon"></i> Colon (:)
                </label>
                <label>
                    <input type="checkbox" name="keep_asterisk" checked>
                    <i class="fas fa-asterisk"></i> Asterisk (*)
                </label>
                <label>
                    <input type="checkbox" name="keep_question" checked>
                    <i class="fas fa-question"></i> Question Mark (?)
                </label>
                <label>
                    <input type="checkbox" name="keep_dquote" checked>
                    <i class="fas fa-quote-right"></i> Double Quote (")
                </label>
                <label>
                    <input type="checkbox" name="keep_ltgt" checked>
                    <i class="fas fa-less-than"></i> Angle Brackets (<>)
                </label>
                <label>
                    <input type="checkbox" name="keep_pipe" checked>
                    <i class="fas fa-grip-lines-vertical"></i> Pipe (|)
                </label>
            </div>
            
            <button type="submit" class="btn">
                <i class="fas fa-magic"></i> Clean & Download Excel
            </button>
        </form>
    </div>
    
    <footer>
        &copy; 2023 FilenameCleaner Pro | Powered by Flask | Netflix-inspired design
    </footer>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <script>
        // Tab switching
        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(`${tabName}-tab`).classList.add('active');
            
            // Update active tab button
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.currentTarget.classList.add('active');
        }
        
        // File upload handling
        document.getElementById('file').addEventListener('change', function(e) {
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
                        const sheetSelect = document.getElementById('sheet');
                        sheetSelect.innerHTML = '';
                        workbook.SheetNames.forEach(sheet => {
                            const option = document.createElement('option');
                            option.value = sheet;
                            option.textContent = sheet;
                            sheetSelect.appendChild(option);
                        });

                        // Populate column selector (A-Z)
                        const columnSelect = document.getElementById('column');
                        columnSelect.innerHTML = '';
                        for (let i = 0; i < 26; i++) {
                            const option = document.createElement('option');
                            option.value = String.fromCharCode(65 + i);
                            option.textContent = `Column ${String.fromCharCode(65 + i)}`;
                            columnSelect.appendChild(option);
                        }

                        // Set default end row
                        const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
                        const range = XLSX.utils.decode_range(firstSheet['!ref']);
                        document.getElementById('end_row').value = range.e.r + 1;
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

def clean_filename(name, char_options=None, show_removed=False):
    """Clean filename with customizable character handling"""
    if not name or pd.isna(name):
        return ('', []) if show_removed else ''
    
    # Default character options
    if char_options is None:
        char_options = {
            'keep_slash': True,
            'keep_backslash': True,
            'keep_colon': True,
            'keep_asterisk': True,
            'keep_question': True,
            'keep_dquote': True,
            'keep_ltgt': True,
            'keep_pipe': True
        }
    
    original = str(name).strip()
    removed_chars = []
    
    # Build the pattern of characters to remove based on user options
    chars_to_remove = []
    
    # Special characters to potentially remove
    special_chars = [
        ('/', 'keep_slash'),
        ('\\\\', 'keep_backslash'),
        (':', 'keep_colon'),
        ('\\*', 'keep_asterisk'),
        ('\\?', 'keep_question'),
        ('"', 'keep_dquote'),
        ('<', 'keep_ltgt'),
        ('>', 'keep_ltgt'),
        ('\\|', 'keep_pipe')
    ]
    
    for char, option in special_chars:
        if not char_options.get(option, True):
            chars_to_remove.append(char)
    
    # Always remove control characters and spaces
    chars_to_remove.extend(['\\x00-\\x1F', ' '])
    
    # Create regex pattern
    pattern = f'[{"".join(chars_to_remove)}]' if chars_to_remove else None
    
    # Find and remove characters
    cleaned = original
    if pattern:
        # First find all characters that will be removed
        removed_chars = list(set(re.findall(pattern, cleaned)))
        # Then remove them completely (no replacement)
        cleaned = re.sub(pattern, '', cleaned)
    
    cleaned = cleaned.strip()
    
    if show_removed:
        return cleaned, removed_chars
    return cleaned

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Get character options from form
            char_options = {
                'keep_slash': request.form.get('keep_slash') == 'on',
                'keep_backslash': request.form.get('keep_backslash') == 'on',
                'keep_colon': request.form.get('keep_colon') == 'on',
                'keep_asterisk': request.form.get('keep_asterisk') == 'on',
                'keep_question': request.form.get('keep_question') == 'on',
                'keep_dquote': request.form.get('keep_dquote') == 'on',
                'keep_ltgt': request.form.get('keep_ltgt') == 'on',
                'keep_pipe': request.form.get('keep_pipe') == 'on'
            }
            
            filenames = []
            removed_info = []
            
            # Handle file upload
            if 'file' in request.files and request.files['file'].filename:
                file = request.files['file']
                
                if file.filename.endswith(('.xlsx', '.xls')):
                    # Excel file processing
                    wb = openpyxl.load_workbook(file, read_only=True)
                    
                    # Get selected sheet or active sheet
                    sheet_name = request.form.get('sheet')
                    sheet = wb[sheet_name] if sheet_name else wb.active
                    
                    # Get column and row range
                    col_letter = request.form.get('column', 'A')
                    col_idx = column_index_from_string(col_letter)
                    start_row = int(request.form.get('start_row', 7))
                    end_row = int(request.form.get('end_row', sheet.max_row))
                    
                    # Process each cell in the range
                    for row in sheet.iter_rows(
                        min_row=start_row,
                        max_row=end_row,
                        min_col=col_idx,
                        max_col=col_idx,
                        values_only=True
                    ):
                        if row[0] is not None and str(row[0]).strip():
                            original = str(row[0]).strip()
                            cleaned, removed = clean_filename(original, char_options, show_removed=True)
                            filenames.append(original)
                            removed_info.append(", ".join(removed) if removed else "")
                
                elif file.filename.endswith('.csv'):
                    # CSV file processing
                    df = pd.read_csv(file)
                    if not df.empty:
                        first_col = df.columns[0]
                        for original in df[first_col].astype(str):
                            if original.strip():
                                cleaned, removed = clean_filename(original, char_options, show_removed=True)
                                filenames.append(original.strip())
                                removed_info.append(", ".join(removed) if removed else "")
                else:
                    flash("Unsupported file format. Please upload Excel (.xlsx, .xls) or CSV.")
                    return redirect(request.url)
            
            # Handle paste text
            elif 'text' in request.form and request.form['text'].strip():
                text = request.form['text']
                for line in text.split('\n'):
                    line = line.strip()
                    if line:
                        cleaned, removed = clean_filename(line, char_options, show_removed=True)
                        filenames.append(line)
                        removed_info.append(", ".join(removed) if removed else "")
            
            else:
                flash("No input provided. Please upload a file or paste text.")
                return redirect(request.url)
            
            if not filenames:
                flash("No valid filenames found to process.")
                return redirect(request.url)
            
            # Create output DataFrame
            output_df = pd.DataFrame({
                'Original Filename': filenames,
                'Cleaned Filename': [clean_filename(f, char_options) for f in filenames],
                'Removed Characters': removed_info
            })
            
            # Generate Excel file
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                output_df.to_excel(writer, index=False, sheet_name='Cleaned_Filenames')
                
                # Add summary sheet
                summary_data = {
                    'Total Filenames Processed': [len(filenames)],
                    'Character Removal Settings': [
                        f"Slash: {'Kept' if char_options['keep_slash'] else 'Removed'}, "
                        f"Backslash: {'Kept' if char_options['keep_backslash'] else 'Removed'}, "
                        f"Colon: {'Kept' if char_options['keep_colon'] else 'Removed'}, "
                        f"Asterisk: {'Kept' if char_options['keep_asterisk'] else 'Removed'}, "
                        f"Question Mark: {'Kept' if char_options['keep_question'] else 'Removed'}, "
                        f"Double Quote: {'Kept' if char_options['keep_dquote'] else 'Removed'}, "
                        f"Angle Brackets: {'Kept' if char_options['keep_ltgt'] else 'Removed'}, "
                        f"Pipe: {'Kept' if char_options['keep_pipe'] else 'Removed'}"
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, index=False, sheet_name='Summary')
            
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='cleaned_filenames.xlsx'
            )
        
        except Exception as e:
            flash(f"An error occurred: {str(e)}")
            return redirect(request.url)
    
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
