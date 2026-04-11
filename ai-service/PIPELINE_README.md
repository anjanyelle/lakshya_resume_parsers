# Production-Ready Resume Parsing Pipeline

A scalable, efficient resume parsing system using DeBERTa NER model with smart section extraction and chunking fallback.

## 🎯 Features

- **Smart Section Extraction**: Automatically detects EXPERIENCE and EDUCATION sections
- **Chunking Fallback**: Falls back to intelligent chunking when sections aren't detected
- **Token Optimization**: Processes only relevant text (400-450 token chunks with 50 token overlap)
- **Post-Processing**: Removes person names from COMPANY and skills from DEGREE predictions
- **Production-Ready**: Clean, modular, FastAPI-compatible code
- **Scalable**: Handles various resume formats and structures

## 📋 Requirements

```bash
transformers>=4.44.0
torch
fastapi
uvicorn
pydantic
```

## 🚀 Quick Start

### Basic Usage

```python
from resume_parser_pipeline import parse_resume

resume_text = """
WORK EXPERIENCE:
Software Developer at Google
Jan 2020 - Present
Mountain View, CA

EDUCATION:
Bachelor of Technology in Computer Science
MIT
2016 - 2020
"""

result = parse_resume(resume_text)
print(result)
```

### Output Format

```json
{
  "experience": [
    {
      "company": "Google",
      "role": "Software Developer",
      "start_date": "Jan 2020",
      "end_date": "Present",
      "location": "Mountain View, CA"
    }
  ],
  "education": [
    {
      "degree": "Bachelor of Technology in Computer Science",
      "institution": "MIT",
      "start_date": "2016",
      "end_date": "2020"
    }
  ]
}
```

## 🏗️ Architecture

### 1. Section Extraction (`SectionExtractor`)

Detects and extracts EXPERIENCE and EDUCATION sections using keywords:

**EXPERIENCE Keywords:**
- experience, work history, employment, professional experience, work experience, career history

**EDUCATION Keywords:**
- education, academic, qualification, academic background, educational background

### 2. Chunking Fallback (`TextChunker`)

If section detection fails:
- Chunks text into 400-450 token segments
- 50 token overlap between chunks
- Filters chunks containing relevant keywords (worked, developer, bachelor, degree, etc.)

### 3. Model Inference (`ModelInference`)

- Loads DeBERTa model from `./models/resume-ner-deberta`
- Processes text with 512 token limit
- Extracts entities: COMPANY, ROLE, LOCATION, START_DATE, END_DATE, DEGREE, EDUCATION

### 4. Post-Processing (`PostProcessor`)

**Removes:**
- Person names from COMPANY predictions (e.g., "John Doe")
- Skills/technologies from DEGREE predictions (e.g., "React", "Python", "Node.js")

**Detection Rules:**
- Person names: Capitalized 2-3 word patterns
- Skills: Matches against common tech keywords

### 5. Output Structuring (`ResumeParser`)

Combines entities into structured experience and education entries.

## 📁 File Structure

```
ai-service/
├── resume_parser_pipeline.py       # Main pipeline
├── test_pipeline.py                # Test script
├── fastapi_integration_example.py  # FastAPI integration
├── PIPELINE_README.md              # This file
└── models/
    └── resume-ner-deberta/         # Trained model
```

## 🧪 Testing

### Run Test Cases

```bash
cd ai-service
source venv/bin/activate
python3 test_pipeline.py
```

### Test Cases Include:
1. Well-structured resume with clear sections
2. Resume without section headers (chunking fallback)
3. Multiple experience and education entries

## 🔌 FastAPI Integration

### Start the API Server

```bash
python3 fastapi_integration_example.py
```

### API Endpoint

```bash
POST /api/parse-resume
Content-Type: application/json

{
  "resume_text": "Your resume text here...",
  "model_path": "./models/resume-ner-deberta"
}
```

### Response

```json
{
  "experience": [...],
  "education": [...],
  "success": true,
  "message": "Successfully extracted 2 experience entries and 1 education entries"
}
```

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## 🎛️ Configuration

### Customize Chunk Size

```python
from resume_parser_pipeline import ResumeParser, TextChunker

parser = ResumeParser(model_path="./models/resume-ner-deberta")
parser.chunker = TextChunker(
    parser.model.tokenizer,
    chunk_size=400,  # Adjust chunk size
    overlap=50       # Adjust overlap
)
```

### Add Custom Keywords

```python
from resume_parser_pipeline import SectionExtractor

# Add custom experience keywords
SectionExtractor.EXPERIENCE_KEYWORDS.append("professional background")

# Add custom education keywords
SectionExtractor.EDUCATION_KEYWORDS.append("certifications")
```

### Customize Post-Processing

```python
from resume_parser_pipeline import PostProcessor

# Add custom skills to filter
PostProcessor.SKILL_KEYWORDS.extend(['tensorflow', 'pytorch', 'keras'])
```

## 📊 Performance

- **Model Accuracy**: 92.86% on test cases
- **Token Limit**: 512 tokens per inference
- **Chunk Size**: 400-450 tokens (optimal for context)
- **Overlap**: 50 tokens (prevents entity splitting)

## 🔍 How It Works

### Step-by-Step Process

1. **Input**: Receive full resume text (plain text from PDF/DOC)

2. **Section Detection**: 
   - Try to detect EXPERIENCE and EDUCATION sections
   - Extract section content

3. **Fallback (if needed)**:
   - Chunk text into 400-450 token segments
   - Filter chunks with relevant keywords
   - Combine relevant chunks

4. **Model Inference**:
   - Pass filtered text to DeBERTa model
   - Extract entities (COMPANY, ROLE, dates, etc.)

5. **Post-Processing**:
   - Remove person names from COMPANY
   - Remove skills from DEGREE
   - Clean and validate entities

6. **Structuring**:
   - Group entities into experience entries
   - Group entities into education entries
   - Return structured JSON

## 🛠️ Troubleshooting

### Issue: Model not loading

```bash
# Verify model path
ls -la ./models/resume-ner-deberta/

# Should contain:
# - config.json
# - pytorch_model.bin
# - tokenizer files
# - label_mappings.json
```

### Issue: Low accuracy

- Check if resume has clear section headers
- Verify text extraction quality from PDF/DOC
- Ensure resume is in English
- Check for special characters or encoding issues

### Issue: Missing entities

- Resume might be too long (>512 tokens per section)
- Chunking should handle this automatically
- Check if relevant keywords are present

## 🚀 Production Deployment

### Docker Example

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ai-service/ .

CMD ["uvicorn", "fastapi_integration_example:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

```bash
MODEL_PATH=./models/resume-ner-deberta
CHUNK_SIZE=450
OVERLAP=50
LOG_LEVEL=INFO
```

## 📈 Scaling Considerations

- **Caching**: Cache model in memory (singleton pattern)
- **Batch Processing**: Process multiple resumes in parallel
- **GPU**: Use GPU for faster inference (if available)
- **Load Balancing**: Deploy multiple instances behind load balancer

## 🤝 Integration with Existing System

The pipeline is designed to integrate seamlessly with your existing FastAPI application:

```python
from resume_parser_pipeline import parse_resume

@app.post("/upload-resume")
async def upload_resume(file: UploadFile):
    # Extract text from PDF/DOC
    text = extract_text_from_file(file)
    
    # Parse with pipeline
    result = parse_resume(text)
    
    # Save to database
    save_to_database(result)
    
    return result
```

## 📝 License

This pipeline is part of the Lakshya Resume Parser project.

## 🙏 Support

For issues or questions, please refer to the main project documentation.
