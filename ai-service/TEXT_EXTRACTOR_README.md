# Text Extractor Module Documentation

## Overview
The `TextExtractor` class provides comprehensive text extraction capabilities for resume files, supporting PDF, DOCX, and TXT formats with OCR fallback for scanned documents.

## Features

### Supported File Formats
- **PDF** (`.pdf`) - Text extraction with OCR fallback
- **DOCX** (`.docx`) - Paragraphs and table extraction
- **TXT** (`.txt`) - Encoding detection and cleanup

### Advanced Capabilities
- **OCR Fallback**: Tesseract OCR for scanned PDFs
- **Text Cleaning**: Privacy protection and normalization
- **Quality Assessment**: Automatic quality scoring
- **Error Handling**: Graceful fallbacks and detailed logging

## Installation

### Python Dependencies
```bash
pip install -r requirements.txt
```

### System Dependencies (for OCR)
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

## Usage

### Basic Usage
```python
from parsers.text_extractor import TextExtractor

extractor = TextExtractor()
result = extractor.extract("resume.pdf")

print(f"Text: {result['text']}")
print(f"Method: {result['method']}")
print(f"Word count: {result['word_count']}")
print(f"Quality score: {result['quality_score']}")
```

### Individual File Type Methods
```python
# PDF extraction
text = extractor.extract_from_pdf("resume.pdf")

# DOCX extraction
text = extractor.extract_from_docx("resume.docx")

# TXT extraction
text = extractor.extract_from_txt("resume.txt")
```

### Text Cleaning
```python
raw_text = "John Doe john@example.com (555) 123-4567"
clean_text = extractor.clean_text(raw_text)
# Result: "John Doe [EMAIL_REMOVED] [PHONE_REMOVED]"
```

## API Reference

### TextExtractor Class

#### Methods

##### `extract(file_path: str) -> Dict`
Main extraction method with automatic type detection.

**Parameters:**
- `file_path`: Path to the file to extract text from

**Returns:**
```python
{
    'text': str,           # Extracted and cleaned text
    'method': str,         # Extraction method used
    'word_count': int,     # Number of words extracted
    'quality_score': float # Quality score (0-1)
}
```

##### `extract_from_pdf(file_path: str) -> str`
Extract text from PDF files using PyMuPDF with OCR fallback.

##### `extract_from_docx(file_path: str) -> str`
Extract text from DOCX files including paragraphs and tables.

##### `extract_from_txt(file_path: str) -> str`
Extract text from TXT files with encoding detection.

##### `clean_text(text: str) -> str`
Clean and normalize extracted text.

**Features:**
- Remove email addresses and phone numbers
- Normalize whitespace
- Remove non-printable characters
- Preserve document structure

##### `_calculate_quality_score(text: str, word_count: int) -> float`
Calculate quality score based on text characteristics.

**Scoring factors:**
- Text length (0-0.4 points)
- Readability/word length (0-0.2 points)
- Document structure (0-0.2 points)
- Vocabulary diversity (0-0.2 points)

#### Utility Methods

##### `get_supported_formats() -> list`
Returns list of supported file extensions.

##### `is_supported(file_path: str) -> bool`
Check if file format is supported.

## Quality Assessment

The quality score ranges from 0 to 1 and indicates the likely quality of text extraction:

- **0.8-1.0**: Excellent - Clean, well-structured text
- **0.6-0.8**: Good - Usable text with minor issues
- **0.4-0.6**: Fair - Some extraction problems
- **0.0-0.4**: Poor - Significant extraction issues

### Quality Factors

1. **Text Length**: Longer documents generally have better extraction
2. **Readability**: Average word length indicates text quality
3. **Structure**: Presence of paragraphs and proper formatting
4. **Diversity**: Unique word ratio indicates content richness

## Text Cleaning

### Privacy Protection
- **Email addresses**: Replaced with `[EMAIL_REMOVED]`
- **Phone numbers**: Replaced with `[PHONE_REMOVED]`

### Normalization
- **Whitespace**: Multiple spaces converted to single space
- **Newlines**: Excessive newlines normalized
- **Unicode**: Characters normalized to consistent form
- **Punctuation**: Excessive special characters removed

### Structure Preservation
- **Paragraph breaks**: Maintained with double newlines
- **Lists and sections**: Preserved through spacing
- **Tables**: Maintained in DOCX extraction

## Error Handling

### Graceful Degradation
1. **PDF extraction fails** → Falls back to OCR
2. **OCR fails** → Raises descriptive error
3. **Encoding issues** → Tries multiple encodings
4. **File not found** → Clear error message

### Logging
All operations include detailed logging:
```python
import logging
logging.basicConfig(level=logging.INFO)

# Logs include:
# - Extraction method used
# - Word count and quality score
# - Errors and fallbacks
# - OCR usage
```

## Performance Considerations

### OCR Processing
- **CPU intensive**: OCR can be slow for large documents
- **Memory usage**: Image processing requires additional memory
- **Quality vs speed**: Higher resolution images improve OCR but slow processing

### Optimization Tips
1. **Batch processing**: Process multiple files in sequence
2. **Caching**: Cache results for repeated processing
3. **Resolution**: Use appropriate image resolution for OCR
4. **Resource limits**: Set memory/time limits for large files

## Testing

### Run Test Suite
```bash
python test_text_extractor.py
```

### Test Files
Create a `test_files` directory with sample documents:
- `sample_resume.pdf`
- `sample_resume.docx`
- `sample_resume.txt`

### Expected Output
```
🔍 Text Extractor Test Suite
==================================================
Supported formats: ['.pdf', '.docx', '.txt']

📄 Processing: sample_resume.pdf
------------------------------
✅ Extraction successful!
   Method: pymupdf
   Word count: 150
   Quality score: 0.85/1.00
   🟢 Quality: Excellent
```

## Integration with AI Service

### FastAPI Integration
```python
from fastapi import FastAPI, UploadFile
from parsers.text_extractor import TextExtractor

app = FastAPI()
extractor = TextExtractor()

@app.post("/extract")
async def extract_text(file: UploadFile):
    # Save uploaded file
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Extract text
    result = extractor.extract(file_path)
    
    # Clean up
    os.remove(file_path)
    
    return result
```

### Error Handling in API
```python
try:
    result = extractor.extract(file_path)
    return {"success": True, "data": result}
except FileNotFoundError:
    return {"success": False, "error": "File not found"}
except ValueError as e:
    return {"success": False, "error": str(e)}
except Exception as e:
    return {"success": False, "error": "Extraction failed"}
```

## Troubleshooting

### Common Issues

#### PyMuPDF Import Error
```bash
pip install PyMuPDF
```

#### Tesseract Not Found
```bash
# Ensure Tesseract is installed and in PATH
which tesseract
# Should return path to tesseract executable
```

#### DOCX Extraction Issues
```bash
pip install python-docx
```

#### Poor OCR Quality
- Check image resolution in PDF
- Ensure Tesseract language packs are installed
- Try preprocessing images for better contrast

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Production Deployment

### Environment Variables
```bash
# Optional: Set Tesseract path if not in PATH
export TESSERACT_CMD="/usr/local/bin/tesseract"

# Optional: Set logging level
export LOG_LEVEL="INFO"
```

### Resource Limits
```python
# Set memory limits for large files
import resource
resource.setrlimit(resource.RLIMIT_AS, (2**30, 2**30))  # 1GB limit
```

### Monitoring
- Monitor extraction success rates
- Track quality score distributions
- Log OCR usage and performance
- Set up alerts for extraction failures

## License and Dependencies

This module uses the following open-source libraries:
- **PyMuPDF**: AGPL License
- **python-docx**: MIT License
- **Tesseract**: Apache License 2.0
- **Pillow**: PIL License

Ensure compliance with all licenses when using in production.
