const express = require('express');
const multer = require('multer');
const xlsx = require('xlsx');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// Configure multer for file uploads
const upload = multer({ dest: 'uploads/' });

// Function to clean filenames
function cleanFilename(filename) {
  // List of invalid characters in Windows
  const invalidChars = /[<>:"/\\|?*\x00-\x1F]/g;
  
  // Replace invalid characters with underscore
  let cleaned = filename.replace(invalidChars, '_');
  
  // Remove spaces
  cleaned = cleaned.replace(/\s+/g, '');
  
  return cleaned;
}

// Route for direct filename input
app.post('/api/clean-names', (req, res) => {
  try {
    const { names } = req.body;
    if (!names || !Array.isArray(names)) {
      return res.status(400).json({ error: 'Invalid input' });
    }

    const cleanedNames = names.map(name => ({
      original: name,
      cleaned: cleanFilename(name)
    }));

    // Create Excel file
    const wb = xlsx.utils.book_new();
    const ws = xlsx.utils.json_to_sheet(cleanedNames);
    xlsx.utils.book_append_sheet(wb, ws, 'Cleaned Names');

    // Send the Excel file
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    res.setHeader('Content-Disposition', 'attachment; filename=cleaned_names.xlsx');
    xlsx.write(wb, { type: 'buffer', bookType: 'xlsx' }).then(buffer => {
      res.end(buffer);
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Route for Excel file upload
app.post('/api/upload-excel', upload.single('file'), (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const workbook = xlsx.readFile(req.file.path);
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];
    const data = xlsx.utils.sheet_to_json(worksheet);

    // Assuming the column with filenames is named 'filename'
    const cleanedNames = data.map(row => ({
      original: row.filename || row.name || Object.values(row)[0],
      cleaned: cleanFilename(row.filename || row.name || Object.values(row)[0])
    }));

    // Create new Excel file
    const newWb = xlsx.utils.book_new();
    const newWs = xlsx.utils.json_to_sheet(cleanedNames);
    xlsx.utils.book_append_sheet(newWb, newWs, 'Cleaned Names');

    // Send the Excel file
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    res.setHeader('Content-Disposition', 'attachment; filename=cleaned_names.xlsx');
    xlsx.write(newWb, { type: 'buffer', bookType: 'xlsx' }).then(buffer => {
      res.end(buffer);
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Server error' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
