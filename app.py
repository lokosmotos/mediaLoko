import os
from flask import Flask, request, send_file, render_template_string, flash, redirect
import pandas as pd
from io import BytesIO
import openpyxl
from openpyxl.utils import column_index_from_string

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

# HTML Template (improved with missing CSS and better UX)
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Excel Filename Cleaner</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            margin: 2rem;
            background: #f4f6f8;
        }
        .container {
            max-width: 700px;
            margin: auto;
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        label {
            font-weight: 500;
        }
        input, select {
            width: 100%;
            padding: 0.6rem;
            margin-top: 0.3rem;
            border: 1px solid #ccc;
            border-radius: 6px;
        }
        button {
            background-color: #28a745;
            color: white;
            padding: 0.7rem 1.2rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
        }
        button:hover {
            background-color: #218838;
        }
        .hidden {
            display: none;
        }
        .icon {
            margin-right: 8px;
        }
        .range-selector {
            display: flex;
            gap: 1rem;
        }
        .range-selector > div {
            flex: 1;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1><i class="fas fa-file-excel icon"></i> Excel Filename Cleaner</h1>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <ul style="color: red;">
              {% for message in messages %}
                <li>{{ message }}</li>
              {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}
        
        <form method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label for="file"><i class="fas fa-file-upload icon"></i> Upload Excel File</label>
                <input type="file" id="file" name="file" accept=".xlsx,.xls">
            </div>

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

            <button type="submit"><i class="fas fa-magic icon"></i> Clean Filenames</button>
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

                    const sheetSelect = document.getElementById('sheet');
                    sheetSelect.innerHTML = '';
                    workbook.SheetNames.forEach(sheet => {
                        const option = document.createElement('option');
                        option.value = sheet;
                        option.textContent = sheet;
                        sheetSelect.appendChild(option);
                    });

                    const columnSelect = document.getElementById('column');
                    columnSelect.innerHTML = '';
                    for (let i = 0; i < 26; i++) {
                        const option = document.createElement('option');
                        option.value = String.fromCharCode(65 + i);
                        option.textContent = `Column ${String.fromCharCode(65 + i)}`;
                        columnSelect.appendChild(option);
                    }

                    const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
                    const range = XLSX.utils.decode_range(firstSheet['!ref']);
                    document.getElementById('end_row').value = range.e.r + 1;
                };
                
                reader.readAsArrayBuffer(file);
            }
        });
    </script>
</body>
</html>"""

def clean_filename(name):
    if not name:
        return ''
    invalid_chars = r'<>:"/\|?*\x00-\x1F'
    cleaned = ''.join('_' if c in invalid_chars else c for c in str(name))
    return cleaned.strip('_')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files or not request.files['file']:
            flash("No file uploaded.")
            return redirect(request.url)

        file = request.files['file']

        try:
            wb = openpyxl.load_workbook(file)
        except Exception as e:
            flash(f"Failed to read Excel file: {e}")
            return redirect(request.url)

        sheet_name = request.form.get('sheet')
        try:
            sheet = wb[sheet_name] if sheet_name else wb.active
        except Exception as e:
            flash(f"Sheet not found: {e}")
            return redirect(request.url)

        try:
            col_letter = request.form.get('column', 'A')
            col_idx = column_index_from_string(col_letter)
            start_row = int(request.form.get('start_row', 1))
            end_row = int(request.form.get('end_row', sheet.max_row))

            filenames = []
            for row in sheet.iter_rows(min_row=start_row, max_row=end_row, min_col=col_idx, max_col=col_idx, values_only=True):
                if row[0]:
                    filenames.append(row[0])

            cleaned_data = [[original, clean_filename(original)] for original in filenames]
            df = pd.DataFrame(cleaned_data, columns=['Original', 'Cleaned'])

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Cleaned_Filenames')
            output.seek(0)

            return send_file(output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='cleaned_filenames.xlsx'
            )

        except Exception as e:
            flash(f"Processing error: {e}")
            return redirect(request.url)

    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
