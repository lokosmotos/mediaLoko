// Theme toggle
const themeToggle = document.getElementById('theme-toggle');
const darkModeCSS = document.getElementById('dark-mode-css');

// Check for saved theme preference or use system preference
const savedTheme = localStorage.getItem('theme') || 
                   (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

// Apply the saved theme
document.documentElement.setAttribute('data-theme', savedTheme);
darkModeCSS.disabled = savedTheme !== 'dark';

// Update button text
updateThemeButton(savedTheme);

themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    darkModeCSS.disabled = newTheme !== 'dark';
    localStorage.setItem('theme', newTheme);
    
    updateThemeButton(newTheme);
});

function updateThemeButton(theme) {
    const icon = themeToggle.querySelector('i');
    const text = themeToggle.querySelector('span');
    
    if (theme === 'dark') {
        icon.className = 'fas fa-sun';
        text.textContent = 'Light Mode';
    } else {
        icon.className = 'fas fa-moon';
        text.textContent = 'Dark Mode';
    }
}

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabId = btn.getAttribute('data-tab');
        
        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Show selected tab content
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        document.getElementById(`${tabId}-tab`).classList.add('active');
    });
});

// Accordion functionality
document.querySelectorAll('.accordion-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const item = btn.parentElement;
        item.classList.toggle('active');
    });
});

// File drop zone functionality
const setupDropZone = (dropZone, input) => {
    dropZone.addEventListener('click', () => input.click());
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });
    
    dropZone.addEventListener('drop', handleDrop, false);
};

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight() {
    this.classList.add('highlight');
}

function unhighlight() {
    this.classList.remove('highlight');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

function handleFiles(files) {
    const fileList = document.getElementById('file-list');
    fileList.innerHTML = '';
    
    if (files.length > 0) {
        document.getElementById('process-btn').disabled = false;
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div>
                    <i class="fas fa-file"></i>
                    ${file.name} (${formatFileSize(file.size)})
                </div>
                <button class="remove-file" data-index="${i}">
                    <i class="fas fa-times"></i>
                </button>
            `;
            fileList.appendChild(fileItem);
        }
    } else {
        document.getElementById('process-btn').disabled = true;
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Initialize drop zones
setupDropZone(
    document.getElementById('drop-zone'),
    document.getElementById('file-input')
);

setupDropZone(
    document.getElementById('batch-drop-zone'),
    document.getElementById('batch-file-input')
);

// Live preview with debounce
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

const preview = debounce((text) => {
    if (!text.trim()) {
        document.getElementById('live-preview').innerHTML = '<p>Start typing or upload files to see results</p>';
        return;
    }
    
    const options = getOptions();
    fetch('/preview', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text, options })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('live-preview').innerHTML = `
            <div class="preview-result">
                <p><strong>Original:</strong> ${data.original}</p>
                <p><strong>Cleaned:</strong> ${data.cleaned}</p>
                ${data.removed.length ? `<p><strong>Removed:</strong> ${data.removed.join(', ')}</p>` : ''}
            </div>
        `;
    });
}, 300);

document.getElementById('text-input').addEventListener('input', (e) => preview(e.target.value));

// Get current options from form
function getOptions() {
    return {
        space_replacement: document.getElementById('space-option').value,
        text_case: document.getElementById('case-option').value,
        keep_slash: document.querySelector('[name="keep_slash"]').checked,
        keep_backslash: document.querySelector('[name="keep_backslash"]').checked,
        keep_colon: document.querySelector('[name="keep_colon"]').checked,
        keep_asterisk: document.querySelector('[name="keep_asterisk"]').checked,
        keep_question: document.querySelector('[name="keep_question"]').checked,
        keep_dquote: document.querySelector('[name="keep_dquote"]').checked,
        keep_ltgt: document.querySelector('[name="keep_ltgt"]').checked,
        keep_pipe: document.querySelector('[name="keep_pipe"]').checked,
        remove_repeats: document.getElementById('remove-repeats').checked
    };
}

// Preset buttons
const presets = {
    windows: {
        space_replacement: 'underscore',
        text_case: 'lower',
        keep_slash: false,
        keep_backslash: false,
        keep_colon: false,
        keep_asterisk: false,
        keep_question: false,
        keep_dquote: false,
        keep_ltgt: false,
        keep_pipe: false,
        remove_repeats: true
    },
    unix: {
        space_replacement: 'hyphen',
        text_case: 'original',
        keep_slash: true,
        keep_backslash: false,
        keep_colon: true,
        keep_asterisk: true,
        keep_question: true,
        keep_dquote: true,
        keep_ltgt: true,
        keep_pipe: true,
        remove_repeats: true
    },
    strict: {
        space_replacement: 'remove',
        text_case: 'lower',
        keep_slash: false,
        keep_backslash: false,
        keep_colon: false,
        keep_asterisk: false,
        keep_question: false,
        keep_dquote: false,
        keep_ltgt: false,
        keep_pipe: false,
        remove_repeats: true
    },
    keepall: {
        space_replacement: 'original',
        text_case: 'original',
        keep_slash: true,
        keep_backslash: true,
        keep_colon: true,
        keep_asterisk: true,
        keep_question: true,
        keep_dquote: true,
        keep_ltgt: true,
        keep_pipe: true,
        remove_repeats: false
    }
};

document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const preset = presets[btn.dataset.preset];
        
        // Apply preset to form
        document.getElementById('space-option').value = preset.space_replacement;
        document.getElementById('case-option').value = preset.text_case;
        document.querySelector('[name="keep_slash"]').checked = preset.keep_slash;
        document.querySelector('[name="keep_backslash"]').checked = preset.keep_backslash;
        document.querySelector('[name="keep_colon"]').checked = preset.keep_colon;
        document.querySelector('[name="keep_asterisk"]').checked = preset.keep_asterisk;
        document.querySelector('[name="keep_question"]').checked = preset.keep_question;
        document.querySelector('[name="keep_dquote"]').checked = preset.keep_dquote;
        document.querySelector('[name="keep_ltgt"]').checked = preset.keep_ltgt;
        document.querySelector('[name="keep_pipe"]').checked = preset.keep_pipe;
        document.getElementById('remove-repeats').checked = preset.remove_repeats;
        
        // Trigger preview update if there's text
        const textInput = document.getElementById('text-input');
        if (textInput.value.trim()) {
            preview(textInput.value);
        }
    });
});

// Process files button
document.getElementById('process-btn').addEventListener('click', () => {
    const files = document.getElementById('batch-file-input').files;
    if (files.length === 0) return;
    
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files[]', files[i]);
    }
    
    // Add options to form data
    const options = getOptions();
    for (const key in options) {
        formData.append(key, options[key]);
    }
    
    fetch('/process', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            return response.json();
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

// Export button
document.getElementById('export-btn').addEventListener('click', () => {
    const format = document.getElementById('export-format').value;
    const results = []; // This would be populated with your results
    
    fetch('/export', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            format: format,
            results: results
        })
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cleaned_filenames.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    });
});

// Enable export button when there are results
// This would be connected to your actual results handling
function enableExportButton() {
    document.getElementById('export-btn').disabled = false;
}
