import os
import re
from flask import Flask, request, send_file, render_template, flash, redirect
import pandas as pd
from io import BytesIO
import openpyxl
from openpyxl.utils import get_column_letter

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'your_secret_key_here'

def clean_filename(name, char_options=None, show_removed=False):
    """Clean filename with customizable character handling"""
    if not name or pd.isna(name):
        return ('', []) if show_removed else ''
    
    char_options = char_options or {
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
    chars_to_remove = []
    
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
    
    chars_to_remove.extend(['\\x00-\\x1F', ' '])
    pattern = f'[{"".join(chars_to_remove)}]' if chars_to_remove else None
    
    cleaned = original
    if pattern:
        removed_chars = list(set(re.findall(pattern, cleaned)))
        cleaned = re.sub(pattern, '', cleaned).strip()
    
    return (cleaned, removed_chars) if show_removed else cleaned

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
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
            
            if 'file' in request.files and request.files['file'].filename:
                file = request.files['file']
                
                if file.filename.endswith(('.xlsx', '.xls')):
                    wb = openpyxl.load_workbook(file, read_only=True)
                    sheet_name = request.form.get('sheet')
                    sheet = wb[sheet_name] if sheet_name else wb.active
                    col_letter = request.form.get('column', 'A')
                    col_idx = column_index_from_string(col_letter)
                    start_row = int(request.form.get('start_row', 7))
                    end_row = int(request.form.get('end_row', sheet.max_row))
                    
                    for row in sheet.iter_rows(
                        min_row=start_row,
                        max_row=end_row,
                        min_col=col_idx,
                        max_col=col_idx,
                        values_only=True
                    ):
                        if row[0] and str(row[0]).strip():
                            original = str(row[0]).strip()
                            cleaned, removed = clean_filename(original, char_options, True)
                            filenames.append(original)
                            removed_info.append(", ".join(removed) if removed else "")
                
                elif file.filename.endswith('.csv'):
                    df = pd.read_csv(file)
                    if not df.empty:
                        for original in df.iloc[:, 0].astype(str):
                            if original.strip():
                                cleaned, removed = clean_filename(original, char_options, True)
                                filenames.append(original.strip())
                                removed_info.append(", ".join(removed) if removed else "")
                else:
                    flash("Unsupported file format. Please upload Excel or CSV.")
                    return redirect('/')
            
            elif 'text' in request.form and request.form['text'].strip():
                for line in request.form['text'].split('\n'):
                    if line.strip():
                        cleaned, removed = clean_filename(line.strip(), char_options, True)
                        filenames.append(line.strip())
                        removed_info.append(", ".join(removed) if removed else "")
            
            if not filenames:
                flash("No valid filenames found to process.")
                return redirect('/')
            
            output_df = pd.DataFrame({
                'Original Filename': filenames,
                'Cleaned Filename': [clean_filename(f, char_options) for f in filenames],
                'Removed Characters': removed_info
            })
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                output_df.to_excel(writer, index=False, sheet_name='Cleaned_Filenames')
                pd.DataFrame({
                    'Total Filenames Processed': [len(filenames)],
                    'Character Settings': [str(char_options)]
                }).to_excel(writer, index=False, sheet_name='Summary')
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='cleaned_filenames.xlsx'
            )
        
        except Exception as e:
            flash(f"Error: {str(e)}")
            return redirect('/')
    
    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
