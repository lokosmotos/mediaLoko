import os
import re
from flask import Flask, request, send_file, render_template_string, flash, redirect
import pandas as pd
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# HTML template with Netflix-style theme
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Filename Cleaner | Powered by Flask</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {
            margin: 0;
            font-family: 'Poppins', sans-serif;
            background-color: #141414;
            color: #fff;
        }
        .container {
            max-width: 800px;
            margin: 3rem auto;
            padding: 2rem;
            background: #1f1f1f;
            border-radius: 12px;
            box-shadow: 0 0 20px rgba(255,255,255,0.1);
        }
        h1 {
            text-align: center;
            margin-bottom: 2rem;
            font-size: 2.5rem;
            color: #e50914;
        }
        form {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }
        input[type="file"] {
            padding: 0.8rem;
            background: #333;
            border: none;
            color: #fff;
            border-radius: 8px;
        }
        .char-options {
            background: #333;
            padding: 1rem;
            border-radius: 8px;
        }
        .char-options label {
            display: block;
            margin-bottom: 0.5rem;
        }
        button {
            padding: 1rem;
            background: #e50914;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 1.1rem;
            color: white;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #f6121d;
        }
        .flash {
            background: #e50914;
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
        }
        footer {
            text-align: center;
            margin-top: 3rem;
            font-size: 0.9rem;
            color: #777;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Filename Cleaner</h1>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <div class="flash">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}
        
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file" required accept=".csv,.xlsx,.xls">
            
            <div class="char-options">
                <h3>Special Character Options</h3>
                <label><input type="checkbox" name="keep_slash" checked> Keep /</label>
                <label><input type="checkbox" name="keep_backslash" checked> Keep \\</label>
                <label><input type="checkbox" name="keep_colon" checked> Keep :</label>
                <label><input type="checkbox" name="keep_asterisk" checked> Keep *</label>
                <label><input type="checkbox" name="keep_question" checked> Keep ?</label>
                <label><input type="checkbox" name="keep_dquote" checked> Keep "</label>
                <label><input type="checkbox" name="keep_ltgt" checked> Keep <></label>
                <label><input type="checkbox" name="keep_pipe" checked> Keep |</label>
            </div>

            <button type="submit">Clean & Download</button>
        </form>

        <footer>© 2025 Filename Cleaner. Inspired by Netflix design.</footer>
    </div>
</body>
</html>"""

def clean_filename(name, char_options=None, show_removed=False):
    if not name or pd.isna(name):
        return ('', set()) if show_removed else ''
    
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
    
    original = str(name)

    base_chars = []
    if not char_options.get('keep_slash', True):
        base_chars.append('/')
    if not char_options.get('keep_backslash', True):
        base_chars.append('\\\\')
    if not char_options.get('keep_colon', True):
        base_chars.append(':')
    if not char_options.get('keep_asterisk', True):
        base_chars.append('\\*')
    if not char_options.get('keep_question', True):
        base_chars.append('\\?')
    if not char_options.get('keep_dquote', True):
        base_chars.append('"')
    if not char_options.get('keep_ltgt', True):
        base_chars.append('<>')
    if not char_options.get('keep_pipe', True):
        base_chars.append('\\|')

    pattern_parts = [f'[{re.escape("".join(base_chars))}]'] if base_chars else []
    pattern_parts.append(r'[\x00-\x1F ]')
    pattern = '|'.join(pattern_parts)

    removed = set()
    if pattern:
        removed = set(re.findall(pattern, original))

    cleaned = original
    if pattern:
        cleaned = re.sub(pattern, '', cleaned)
    cleaned = cleaned.strip()

    if show_removed:
        return cleaned, removed
    return cleaned

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

            if 'file' not in request.files:
                flash('No file uploaded')
                return redirect(request.url)

            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if file.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
            elif file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                flash('Unsupported file format. Please upload Excel or CSV.')
                return redirect(request.url)

            if df.empty:
                flash('Uploaded file is empty')
                return redirect(request.url)

            first_column = df.columns[0]
            original_filenames = df[first_column].astype(str)

            cleaned_list = []
            removed_list = []

            for name in original_filenames:
                cleaned, removed = clean_filename(name, char_options, show_removed=True)
                cleaned_list.append(cleaned)
                removed_list.append(', '.join(removed) if removed else '')

            output_df = pd.DataFrame({
                'Original Filename': original_filenames,
                'Cleaned Filename': cleaned_list,
                'Removed Characters': removed_list
            })

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                output_df.to_excel(writer, index=False, sheet_name='Cleaned_Filenames')
            output.seek(0)

            return send_file(
                output,
                download_name='cleaned_filenames.xlsx',
                as_attachment=True,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        except Exception as e:
            flash(f'Error: {str(e)}')
            return redirect(request.url)

    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
