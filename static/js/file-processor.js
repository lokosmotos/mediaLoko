// Web Worker for processing large files
self.onmessage = function(e) {
    const { files, options } = e.data;
    const results = [];
    const totalFiles = files.length;
    
    files.forEach((file, fileIndex) => {
        const reader = new FileReader();
        
        reader.onload = function(event) {
            try {
                let data;
                if (file.name.endsWith('.csv')) {
                    // Process CSV in chunks
                    const text = event.target.result;
                    const lines = text.split('\n');
                    
                    for (let i = 0; i < lines.length; i++) {
                        const line = lines[i].trim();
                        if (line) {
                            const value = line.split(',')[0]; // Get first column
                            const result = cleanFilename(value, options);
                            results.push(result);
                        }
                        
                        // Update progress every 100 lines
                        if (i % 100 === 0) {
                            const progress = {
                                fileProgress: (i / lines.length) * 100,
                                fileIndex,
                                totalFiles
                            };
                            self.postMessage({ type: 'progress', progress });
                        }
                    }
                } else if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
                    // Process Excel files
                    const data = new Uint8Array(event.target.result);
                    const workbook = XLSX.read(data, { type: 'array' });
                    const sheet = workbook.Sheets[workbook.SheetNames[0]];
                    const jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 });
                    
                    for (let i = 0; i < jsonData.length; i++) {
                        if (jsonData[i] && jsonData[i][0]) {
                            const result = cleanFilename(jsonData[i][0], options);
                            results.push(result);
                        }
                        
                        // Update progress every 100 rows
                        if (i % 100 === 0) {
                            const progress = {
                                fileProgress: (i / jsonData.length) * 100,
                                fileIndex,
                                totalFiles
                            };
                            self.postMessage({ type: 'progress', progress });
                        }
                    }
                }
                
                // File processing complete
                self.postMessage({ 
                    type: 'complete', 
                    fileIndex,
                    totalFiles,
                    results 
                });
                
            } catch (error) {
                self.postMessage({ 
                    type: 'error', 
                    error: error.message,
                    fileIndex,
                    totalFiles
                });
            }
        };
        
        reader.onerror = function() {
            self.postMessage({ 
                type: 'error', 
                error: 'Failed to read file',
                fileIndex,
                totalFiles
            });
        };
        
        if (file.name.endsWith('.csv')) {
            reader.readAsText(file);
        } else {
            reader.readAsArrayBuffer(file);
        }
    });
};

function cleanFilename(name, options) {
    if (!name || typeof name !== 'string') {
        return {
            original: '',
            cleaned: '',
            removed: []
        };
    }
    
    let original = name.trim();
    let cleaned = original;
    const removed = [];
    
    // Space handling
    if (options.space_replacement === 'underscore') {
        cleaned = cleaned.replace(/ /g, '_');
    } else if (options.space_replacement === 'hyphen') {
        cleaned = cleaned.replace(/ /g, '-');
    } else if (options.space_replacement === 'remove') {
        cleaned = cleaned.replace(/ /g, '');
    }
    
    // Case handling
    if (options.text_case === 'lower') {
        cleaned = cleaned.toLowerCase();
    } else if (options.text_case === 'upper') {
        cleaned = cleaned.toUpperCase();
    } else if (options.text_case === 'title') {
        cleaned = cleaned.replace(/\w\S*/g, (txt) => {
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        });
    }
    
    // Character removal
    const charsToRemove = [];
    if (!options.keep_slash) charsToRemove.push('/');
    if (!options.keep_backslash) charsToRemove.push('\\\\');
    if (!options.keep_colon) charsToRemove.push(':');
    if (!options.keep_asterisk) charsToRemove.push('\\*');
    if (!options.keep_question) charsToRemove.push('\\?');
    if (!options.keep_dquote) charsToRemove.push('"');
    if (!options.keep_ltgt) charsToRemove.push('<', '>');
    if (!options.keep_pipe) charsToRemove.push('\\|');
    
    // Always remove control characters
    charsToRemove.push('\\x00-\\x1F');
    
    if (charsToRemove.length > 0) {
        const pattern = new RegExp(`[${charsToRemove.join('')}]`, 'g');
        const matches = cleaned.match(pattern) || [];
        removed.push(...new Set(matches));
        cleaned = cleaned.replace(pattern, '');
    }
    
    // Remove duplicate symbols if enabled
    if (options.remove_repeats) {
        cleaned = cleaned.replace(/([-_.])\1+/g, '$1');
    }
    
    return {
        original,
        cleaned: cleaned.trim(),
        removed
    };
}
