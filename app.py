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
        /* [Previous CSS styles remain the same] */
        .char-options {
            margin-top: 1rem;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 0.25rem;
        }
        .char-options label {
            display: inline-block;
            margin-right: 1rem;
            margin-bottom: 0.5rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- [Previous HTML structure remains the same until the form] -->
        
        <form method="post" enctype="multipart/form-data">
            <!-- [Previous form elements remain the same] -->
            
            <div class="char-options">
                <h4><i class="fas fa-sliders-h"></i> Special Character Options</h4>
                <label>
                    <input type="checkbox" name="keep_slash" checked>
                    Keep /
                </label>
                <label>
                    <input type="checkbox" name="keep_backslash" checked>
                    Keep \\
                </label>
                <label>
                    <input type="checkbox" name="keep_colon" checked>
                    Keep :
                </label>
                <label>
                    <input type="checkbox" name="keep_asterisk" checked>
                    Keep *
                </label>
                <label>
                    <input type="checkbox" name="keep_question" checked>
                    Keep ?
                </label>
                <label>
                    <input type="checkbox" name="keep_dquote" checked>
                    Keep "
                </label>
                <label>
                    <input type="checkbox" name="keep_ltgt" checked>
                    Keep <>
                </label>
                <label>
                    <input type="checkbox" name="keep_pipe" checked>
                    Keep |
                </label>
            </div>
            
            <button type="submit"><i class="fas fa-magic"></i> Clean & Export</button>
        </form>
    </div>

    <!-- [Previous JavaScript remains the same] -->
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
    
    # Build the pattern based on user options
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
    
    # Always remove control characters and spaces
    pattern_parts = [f'[{re.escape("".join(base_chars))}]'] if base_chars else []
    pattern_parts.append(r'[\x00-\x1F ]')  # Control chars and spaces
    
    pattern = '|'.join(pattern_parts)
    
    # Find all special characters that will be removed
    removed = set()
    if pattern:
        removed = set(re.findall(pattern, original))
    
    # Clean the filename - remove characters completely (don't replace with _)
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
            
            # [Rest of your processing logic remains similar, but use char_options]
            # For each filename:
            cleaned, removed = clean_filename(filename, char_options, show_removed=True)
            
            # Create DataFrame with Original, Cleaned, and Removed_Chars columns
            # Removed_Chars will be blank if nothing was removed
            
        except Exception as e:
            flash(f'Error: {str(e)}')
            return redirect(request.url)
    
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
