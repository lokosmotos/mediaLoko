HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Windows Filename Cleaner</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #4361ee;
            --secondary: #3f37c9;
            --light: #f8f9fa;
            --dark: #212529;
            --success: #4cc9f0;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Poppins', sans-serif;
        }
        
        body {
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
            transition: all 0.3s ease;
        }
        
        h1 {
            color: var(--primary);
            text-align: center;
            margin-bottom: 1.5rem;
            font-weight: 600;
        }
        
        .description {
            color: var(--dark);
            text-align: center;
            margin-bottom: 2rem;
            opacity: 0.8;
            line-height: 1.6;
        }
        
        .tabs {
            display: flex;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid #eee;
        }
        
        .tab-btn {
            padding: 0.75rem 1.5rem;
            background: none;
            border: none;
            cursor: pointer;
            font-weight: 500;
            color: #666;
            position: relative;
            transition: all 0.3s ease;
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
            height: 3px;
            background: var(--primary);
            border-radius: 3px 3px 0 0;
        }
        
        .tab-content {
            display: none;
            animation: fadeIn 0.5s ease;
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
            color: var(--dark);
        }
        
        input[type="file"], select, textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 1rem;
            transition: border 0.3s ease;
        }
        
        input[type="file"]:focus, select:focus, textarea:focus {
            border-color: var(--primary);
            outline: none;
        }
        
        textarea {
            min-height: 120px;
            resize: vertical;
        }
        
        .btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        
        .btn:hover {
            background: var(--secondary);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(67, 97, 238, 0.3);
        }
        
        .btn i {
            font-size: 1.2rem;
        }
        
        .preview-box {
            margin-top: 2rem;
            border: 1px dashed #ddd;
            border-radius: 8px;
            padding: 1rem;
            display: none;
        }
        
        .preview-title {
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: var(--dark);
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .container {
                padding: 1.5rem;
            }
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <h1>Windows Filename Cleaner</h1>
        <p class="description">Clean invalid characters from filenames for Windows compatibility</p>
        
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('upload')">
                <i class="fas fa-file-excel"></i> Upload Excel
            </button>
            <button class="tab-btn" onclick="switchTab('text')">
                <i class="fas fa-font"></i> Text Input
            </button>
        </div>
        
        <form method="post" enctype="multipart/form-data">
            <!-- Excel Upload Tab -->
            <div id="upload-tab" class="tab-content active">
                <div class="form-group">
                    <label for="file"><i class="fas fa-file-upload"></i> Select Excel File</label>
                    <input type="file" id="file" name="file" accept=".xlsx,.xls" required>
                </div>
                <div class="form-group" id="column-selector">
                    <label for="column"><i class="fas fa-columns"></i> Select Column to Clean</label>
                    <select id="column" name="column" required>
                        <option value="">-- Select Column --</option>
                    </select>
                </div>
            </div>
            
            <!-- Text Input Tab -->
            <div id="text-tab" class="tab-content">
                <div class="form-group">
                    <label for="text"><i class="fas fa-align-left"></i> Enter Filenames (one per line)</label>
                    <textarea id="text" name="text" placeholder="file1.txt&#10;file2.jpg&#10;document with spaces.pdf"></textarea>
                </div>
            </div>
            
            <button type="submit" class="btn">
                <i class="fas fa-magic"></i> Clean & Download Excel
            </button>
        </form>
    </div>

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
        
        // Dynamic column selection for Excel files
        document.getElementById('file').addEventListener('change', function(e) {
            if (this.files.length > 0) {
                const file = this.files[0];
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    const data = new Uint8Array(e.target.result);
                    const workbook = XLSX.read(data, { type: 'array' });
                    const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
                    const jsonData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 });
                    
                    const columnSelect = document.getElementById('column');
                    columnSelect.innerHTML = '<option value="">-- Select Column --</option>';
                    
                    if (jsonData.length > 0) {
                        jsonData[0].forEach((col, index) => {
                            if (col) {
                                const option = document.createElement('option');
                                option.value = index;
                                option.textContent = col;
                                columnSelect.appendChild(option);
                            }
                        });
                    }
                };
                
                reader.readAsArrayBuffer(file);
            }
        });
        
        // Show file name when selected
        document.getElementById('file').addEventListener('change', function() {
            if (this.files.length > 0) {
                const fileName = this.files[0].name;
                this.nextElementSibling.textContent = fileName;
            }
        });
    </script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
</body>
</html>
