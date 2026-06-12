# End-to-End Logging Setup Guide

## 🎯 Overview

Comprehensive logging has been added to track every stage of the resume parsing pipeline. This guide explains how to use and interpret the logs to debug missing work experience issues.

## 📁 Files Created/Modified

### New Files:
1. **`ai-service/utils/logger.py`** - Centralized logging utility with JSON formatting
2. **`backend/src/middleware/requestLogger.ts`** - Request ID tracking middleware
3. **`ai-service/logs/resume_parser.log`** - Log file (auto-created)
4. **`backend/logs/resume_parser.log`** - Backend log file (auto-created)

### Modified Files:
1. **`ai-service/parsers/master_parser.py`** - Added comprehensive logging throughout pipeline

## 🚀 Setup Instructions

### 1. Initialize Logging (AI Service)

The logging is automatically initialized when the master parser is imported. Logs are written to:
- **File**: `ai-service/logs/resume_parser.log` (JSON format)
- **Console**: Human-readable format with colors

### 2. Enable Request ID Tracking (Backend)

Add the middleware to your Express app:

```typescript
// In backend/src/app.ts or server.ts
import { requestLogger, logFileUpload, errorLogger } from './middleware/requestLogger';

// Add before routes
app.use(requestLogger);

// Add after file upload middleware
app.post('/upload/resume', upload.single('resume'), logFileUpload, async (req, res) => {
  // Your upload handler
});

// Add error logger at the end
app.use(errorLogger);
```

### 3. Pass Request ID to AI Service

Update your AI service call to include the request ID:

```typescript
// In your upload handler
const requestId = req.requestId;

// Pass to AI service
const aiResponse = await axios.post('http://localhost:5000/parse', {
  text: extractedText,
  candidate_id: candidateId,
  request_id: requestId  // Add this
});
```

## 📊 Log Structure

### Log Levels:
- **INFO**: Normal operation milestones
- **DEBUG**: Detailed debugging information
- **WARNING**: Potential issues (missing sections, empty extractions)
- **ERROR**: Actual errors with stack traces

### Log Entry Format (JSON):
```json
{
  "timestamp": "2026-04-13T14:30:45.123Z",
  "level": "INFO",
  "logger": "resume_parser",
  "message": "🚀 PARSE REQUEST STARTED",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "candidate_id": "candidate_123",
  "text_length": 2500,
  "timestamp": 1713019845.123
}
```

## 🔍 Logging Stages

### Stage 1: Request Started
```
🚀 PARSE REQUEST STARTED
- candidate_id
- text_length
- timestamp
```

### Stage 2: Text Extraction
```
📄 TEXT EXTRACTION STAGE
- text_length
- text_preview (first 500 chars)
- word_count
- line_count
```

### Stage 3: Section Extraction
```
📑 SECTION EXTRACTION STAGE
- sections_detected: ["WORK EXPERIENCE", "EDUCATION", "SKILLS"]
- section_count
- has_work_experience: true/false
- has_education: true/false

⚠️ WORK EXPERIENCE SECTION NOT DETECTED (if missing)
- detected_sections
- text_preview
```

### Stage 4: Section Content (Debug)
```
📋 WORK EXPERIENCE SECTION CONTENT
- section_name
- content_length
- content_preview (first 500 chars)
```

### Stage 5: Model Inference
```
🤖 MODEL INFERENCE STAGE - Starting DeBERTa NER parsing

🔍 MODEL INPUT
- text_length
- text_preview

📤 MODEL RAW OUTPUT
- companies: ["Company A", "Company B"]
- job_titles: ["Software Engineer", "Developer"]
- institutions: ["University X"]
- degrees: ["B.Tech"]
- work_experience_count
- education_count

🎯 MODEL PARSED ENTITIES
- work_experience: [...]
- education: [...]

⚠️ MODEL DID NOT EXTRACT WORK EXPERIENCE (if empty)
- deberta_results
```

### Stage 6: Experience Extraction
```
💼 EXPERIENCE EXTRACTION STAGE

✅ Experience extraction completed
- experience_count
- experiences: [...]

⚠️ EXPERIENCE EXTRACTION RETURNED EMPTY (if failed)
- sections_available
- experience_results
```

### Stage 7: Education Extraction
```
🎓 EDUCATION EXTRACTION STAGE

✅ Education extraction completed
- education_count
- educations: [...]
```

### Stage 8: Final Response
```
✅ PARSE REQUEST COMPLETED
- candidate_id
- total_time_ms
- work_experience_count
- education_count
- skills_count
- metrics: {...}

📊 FINAL EXTRACTION RESULTS
- work_experience: [...]
- education: [...]
```

### Error Handling
```
❌ PARSE REQUEST FAILED
- candidate_id
- error
- error_type
- traceback
```

## 🧪 Testing the Logging

### Test 1: Upload a Resume
```bash
# Upload your test resume
curl -X POST http://localhost:3000/upload/resume \
  -F "resume=@resume1.txt"
```

### Test 2: View Logs
```bash
# View AI service logs
tail -f ai-service/logs/resume_parser.log | jq .

# View backend logs
tail -f backend/logs/resume_parser.log | jq .

# Search for specific request
grep "request_id_here" ai-service/logs/resume_parser.log | jq .
```

### Test 3: Filter by Log Level
```bash
# Show only warnings and errors
grep -E '"level":"(WARNING|ERROR)"' ai-service/logs/resume_parser.log | jq .

# Show work experience warnings
grep "WORK EXPERIENCE" ai-service/logs/resume_parser.log | jq .
```

## 🐛 Debugging Missing Work Experience

### Step-by-Step Debugging:

1. **Find the Request ID**
   - Look for the upload in backend logs
   - Note the `request_id`

2. **Check Text Extraction**
   ```bash
   grep "TEXT EXTRACTION STAGE" logs/resume_parser.log | grep "request_id_here"
   ```
   - Verify `text_length` > 0
   - Check `text_preview` contains resume content

3. **Check Section Detection**
   ```bash
   grep "SECTION EXTRACTION STAGE" logs/resume_parser.log | grep "request_id_here"
   ```
   - Look for `has_work_experience: true`
   - If false, check `detected_sections` array
   - Review `text_preview` to see why section wasn't detected

4. **Check Model Output**
   ```bash
   grep "MODEL RAW OUTPUT" logs/resume_parser.log | grep "request_id_here"
   ```
   - Verify `companies` array has values
   - Check `work_experience_count` > 0
   - If empty, check `MODEL INPUT` to see what text was sent

5. **Check Experience Extraction**
   ```bash
   grep "EXPERIENCE EXTRACTION" logs/resume_parser.log | grep "request_id_here"
   ```
   - Look for `experience_count`
   - If 0, check warning message for details

6. **Check Final Results**
   ```bash
   grep "FINAL EXTRACTION RESULTS" logs/resume_parser.log | grep "request_id_here"
   ```
   - Review complete `work_experience` array
   - Compare with expected output

## 📈 Log Analysis Examples

### Example 1: Successful Parsing
```json
{
  "timestamp": "2026-04-13T14:30:45.123Z",
  "level": "INFO",
  "message": "✅ PARSE REQUEST COMPLETED",
  "request_id": "abc123",
  "work_experience_count": 2,
  "education_count": 1,
  "total_time_ms": 1250
}
```

### Example 2: Missing Work Experience Section
```json
{
  "timestamp": "2026-04-13T14:30:46.456Z",
  "level": "WARNING",
  "message": "⚠️ WORK EXPERIENCE SECTION NOT DETECTED",
  "request_id": "abc123",
  "detected_sections": ["EDUCATION", "SKILLS"],
  "text_preview": "John Doe\nSoftware Engineer..."
}
```

### Example 3: Model Extraction Failed
```json
{
  "timestamp": "2026-04-13T14:30:47.789Z",
  "level": "WARNING",
  "message": "⚠️ MODEL DID NOT EXTRACT WORK EXPERIENCE",
  "request_id": "abc123",
  "deberta_results": {
    "companies": [],
    "job_titles": [],
    "work_experience": []
  }
}
```

## 🔧 Troubleshooting

### Issue: No logs appearing
**Solution**: Check if logs directory exists and has write permissions
```bash
mkdir -p ai-service/logs
chmod 755 ai-service/logs
```

### Issue: Logs too verbose
**Solution**: Change log level in `utils/logger.py`
```python
default_logger = setup_logging(level=logging.INFO)  # Change from DEBUG
```

### Issue: Can't find request ID
**Solution**: Search by candidate_id or timestamp
```bash
grep "candidate_123" logs/resume_parser.log | jq .
```

## 📝 Best Practices

1. **Always use request IDs** - Makes tracing issues much easier
2. **Monitor WARNING logs** - They indicate potential issues
3. **Review text_preview** - Helps understand what the parser sees
4. **Check section detection first** - Most issues start here
5. **Compare model input vs output** - Identifies model issues
6. **Keep logs for 7 days** - Rotate old logs to save space

## 🎯 Quick Reference

### Common Log Searches:
```bash
# All warnings for a request
grep "WARNING.*request_id_here" logs/resume_parser.log

# All work experience related logs
grep "WORK EXPERIENCE\|EXPERIENCE EXTRACTION" logs/resume_parser.log

# Failed parses
grep "PARSE REQUEST FAILED" logs/resume_parser.log

# Slow parses (>2 seconds)
grep "total_time_ms" logs/resume_parser.log | jq 'select(.total_time_ms > 2000)'

# Empty extractions
grep "experience_count.*0\|education_count.*0" logs/resume_parser.log
```

## ✅ Verification Checklist

- [ ] Logs directory created
- [ ] Request ID middleware added to backend
- [ ] Request ID passed to AI service
- [ ] Can see logs in console
- [ ] Can see logs in file
- [ ] Logs contain request_id
- [ ] Can trace a full request through pipeline
- [ ] Warnings appear for missing sections
- [ ] Error logs include stack traces

---

**Now you have complete visibility into your resume parsing pipeline!** 🎉

Use the logs to identify exactly where work experience extraction is failing and fix the root cause.
