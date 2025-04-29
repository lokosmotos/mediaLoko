import os
from flask import Flask, request, send_file, render_template_string
import pandas as pd
from io import BytesIO
import openpyxl
from openpyxl.utils import get_column_letter

app = Flask(__name__)

# HTML Template with full range selection
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Excel Filename Cleaner</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        /* [Previous CSS styles remain the same] */
        .range-selector {
            display: flex;
            gap: 1rem;
        }
        .range-selector > div {
            flex: 1;
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <h1><i class="fas fa-file-excel icon"></i> Excel Filename Cleaner</h1>
        
        <form method="post" enctype="multipart/form-data">
            <!-- File Upload -->
            <div class="form-group">
                <label for="file"><i class="fas fa-file-upload icon"></i> Upload Excel File</label>
                <input type="file" id="file" name="file" accept=".xlsx,.xls">
            </div>
            
            <!-- Excel Selectors -->
            <div id="excel-selectors" class="hidden">
                <div class="form-group">
                    <label for="sheet"><i class="fas fa-table icon"></i> Sheet</label>
                    <select id="sheet" name="sheet"></select>
                </div>
                
                <div class="form-group">
                    <label for="column"><i class="fas fa-columns icon"></i> Column (A-Z)</label>
                    <select id="column" name="column"></select>
                </div>
                
                <div class="range-selector">
                    <div class="form-group">
                        <label for="start_row"><i class="fas fa-arrow-down icon"></i> Start Row</label>
                        <input type="number" id="start_row" name="start_row" min="1" value="7">
                    </div>
                    <div class="form-group">
                        <label for="end_row"><i class="fas fa-arrow-up icon"></i> End Row</label>
                        <input type="number" id="end_row" name="end_row" min="1">
                    </div>
                </div>
            </div>
            
            <!-- [Rest of the form remains the same] -->
        </form>
    </div>

    <script>
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
                    
                    // Populate column selector (A-Z)
                    const columnSelect = document.getElementById('column');
                    columnSelect.innerHTML = '';
                    for (let i = 0; i < 26; i++) {
                        const option = document.createElement('option');
                        option.value = String.fromCharCode(65 + i);
                        option.textContent = `Column ${String.fromCharCode(65 + i)}`;
                        columnSelect.appendChild(option);
                    }
                    
                    // Set default end row to sheet's last row
                    const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
                    const range = XLSX.utils.decode_range(firstSheet['!ref']);
                    document.getElementById('end_row').value = range.e.r + 1;
                };
                
                reader.readAsArrayBuffer(file);
            }
        });
    </script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
</body>
</html>"""

def clean_filename(filename):
    invalid_chars = r'<>:"/\|?* \x00-\x1F'
    return ''.join('_' if char in invalid_chars else char for char in str(filename)).strip('_')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Process Excel file
        if 'file' in request.files:
            file = request.files['file']
            if file.filename:
                wb = openpyxl.load_workbook(file, read_only=True)
                sheet = wb[request.form.get('sheet')] if request.form.get('sheet') else wb.active
                
                # Get processing range
                col_letter = request.form.get('column', 'A')
                start_row = int(request.form.get('start_row', 7))
                end_row = int(request.form.get('end_row', sheet.max_row))
                
                # Read specified range
                filenames = []
                for row in sheet.iter_rows(
                    min_row=start_row,
                    max_row=end_row,
                    min_col=openpyxl.utils.column_index_from_string(col_letter),
                    max_col=openpyxl.utils.column_index_from_string(col_letter),
                    values_only=True
                ):
                    if row[0]:  # Only process non-empty cells
                        filenames.append(row[0])
                
                cleaned = [[name, clean_filename(name)] for name in filenames]
                df = pd.DataFrame(cleaned, columns=['Original', 'Cleaned'])
                
                # [Rest of the processing remains the same]
    
        
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
