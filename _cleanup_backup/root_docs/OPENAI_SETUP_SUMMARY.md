# OpenAI GPT-4o-mini Integration - Setup Summary

## ✅ Completed Changes

### 1. **New Files Created**

#### `backend/src/services/openai-parser.service.ts`
- OpenAI client initialization with API key validation
- Resume parsing using GPT-4o-mini model
- Prompt engineering for work experience and education extraction
- Response normalization to match DeBERTa schema
- Token usage and processing time tracking
- Comprehensive error handling

#### `backend/src/OPENAI_INTEGRATION.md`
- Complete documentation for the integration
- Installation instructions
- API usage examples
- Cost estimation
- Testing guidelines
- Security best practices

#### `backend/src/setup-openai.sh`
- Automated setup script
- OpenAI SDK installation
- Environment variable configuration
- Setup validation

### 2. **Modified Files**

#### `backend/src/controllers/upload.controller.ts`
**Changes:**
- Added import for `OpenAIParserService`
- Modified `parseSections` function to support model selection
- Implemented OpenAI parsing logic for `gpt-4o-mini` model
- Added automatic fallback to DeBERTa parser on OpenAI failure
- Enhanced logging with model selection and token usage
- Maintained backward compatibility with existing DeBERTa parser

**Key Features:**
- Model selection via `model` parameter in request body
- Extracts only experience and education sections (not full resume)
- Returns identical schema as DeBERTa parser
- Automatic fallback mechanism
- Detailed console logging

#### `backend/src/.env.example`
**Added:**
```env
# OpenAI API Configuration (required for gpt-4o-mini model)
OPENAI_API_KEY=your_openai_api_key_here

# AI Service URL (for DeBERTa NER parser)
AI_SERVICE_URL=http://localhost:8000
```

### 3. **Dependencies Installed**

```json
{
  "openai": "^4.x.x"
}
```

## 🎯 How It Works

### Request Flow

1. **Frontend** sends request to `/api/upload/parse-sections` with:
   ```json
   {
     "model": "gpt-4o-mini",
     "sections": {
       "experience": { "text": "..." },
       "education": { "text": "..." }
     }
   }
   ```

2. **Backend** checks the `model` parameter:
   - If `gpt-4o-mini`: Uses OpenAI parser
   - If `own-model` or missing: Uses DeBERTa parser

3. **OpenAI Parser**:
   - Reads `OPENAI_API_KEY` from environment
   - Sends only experience and education text to GPT-4o-mini
   - Parses structured JSON response
   - Normalizes to match DeBERTa schema
   - Returns with metadata (tokens, processing time)

4. **Fallback**:
   - If OpenAI fails → Automatically uses DeBERTa parser
   - Logs fallback attempt
   - Returns same schema to frontend

### Response Format

```json
{
  "work_experience": [
    {
      "company": "Company Name",
      "company_name": "Company Name",
      "role": "Software Engineer",
      "job_title": "Software Engineer",
      "location": "Location",
      "start_date": "2020-01",
      "end_date": "2023-12",
      "is_current": false,
      "client": null,
      "clients": [],
      "description": "Description..."
    }
  ],
  "education": [
    {
      "institution": "University",
      "degree": "Bachelor of Science",
      "field_of_study": "Computer Science",
      "start_year": 2016,
      "end_year": 2020,
      "grade": "3.8"
    }
  ],
  "metadata": {
    "model": "gpt-4o-mini",
    "token_usage": {
      "prompt_tokens": 450,
      "completion_tokens": 320,
      "total_tokens": 770
    },
    "processing_time_ms": 1250
  }
}
```

## 🚀 Setup Instructions

### Step 1: Install Dependencies (Already Done ✅)

```bash
cd backend/src
npm install openai
```

### Step 2: Configure Environment Variables

Add your OpenAI API key to `backend/src/.env`:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Get your API key from:** https://platform.openai.com/api-keys

### Step 3: Restart Backend Server

```bash
cd backend/src
npm run dev
```

### Step 4: Test the Integration

The frontend already has the model dropdown configured. Simply:

1. Upload a resume
2. Select **"GPT-4o Mini"** from the dropdown
3. Click parse
4. View results (same UI, different parsing engine)

## 🔍 Testing

### Test with cURL

**Using GPT-4o-mini:**
```bash
curl -X POST http://localhost:3001/api/upload/parse-sections \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "sections": {
      "experience": {
        "text": "Software Engineer at Google\nJan 2020 - Present\nDeveloped scalable systems"
      },
      "education": {
        "text": "Stanford University\nBS Computer Science\n2016-2020\nGPA: 3.8"
      }
    }
  }'
```

**Using DeBERTa (own-model):**
```bash
curl -X POST http://localhost:3001/api/upload/parse-sections \
  -H "Content-Type: application/json" \
  -d '{
    "model": "own-model",
    "sections": {
      "experience": {"text": "..."},
      "education": {"text": "..."}
    }
  }'
```

## 📊 Features

### ✅ Model Selection
- `own-model`: DeBERTa NER parser (existing)
- `gpt-4o-mini`: OpenAI GPT-4o-mini

### ✅ Automatic Fallback
- OpenAI fails → DeBERTa parser
- Seamless error recovery
- No frontend changes needed

### ✅ Token Usage Tracking
- Prompt tokens
- Completion tokens
- Total tokens
- Cost estimation

### ✅ Processing Time Logging
- Millisecond precision
- Console logs
- Response metadata

### ✅ Schema Compatibility
- Identical response format
- Frontend works without changes
- Backward compatible

### ✅ Security
- API key in environment variables
- Not exposed in logs or responses
- Secure OpenAI SDK communication

## 💰 Cost Estimation

**GPT-4o-mini Pricing:**
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens

**Typical Resume:**
- Input tokens: ~400-600
- Output tokens: ~200-400
- **Cost per resume: ~$0.0003-0.0005**

**Example:**
- 1,000 resumes/month
- Average 500 input + 300 output tokens
- Cost: ~$0.40/month

## 🎯 Prompt Engineering

The OpenAI prompt is optimized to:

1. **Extract Work Experience:**
   - Detect employer vs client companies
   - Normalize incomplete job titles
   - Identify current employment
   - Parse dates to YYYY-MM format

2. **Extract Education:**
   - Parse institution, degree, field
   - Extract years and GPA
   - Handle missing data gracefully

3. **Follow Strict Rules:**
   - Never invent data
   - Return null for missing values
   - Output valid JSON only
   - No markdown or explanations

## 📝 Logging

Console logs include:
- 🎯 Selected model
- 🤖 OpenAI parser status
- 📝 Input text lengths
- ✅ Success with counts
- 📊 Token usage
- ⏱️ Processing time
- ❌ Errors with fallback
- 🔄 Fallback attempts

## 🔒 Security Checklist

- ✅ API key in `.env` (not committed)
- ✅ API key validated on initialization
- ✅ No API key in logs
- ✅ No API key in responses
- ✅ Secure SDK communication
- ✅ Error messages don't leak sensitive data

## 🐛 Troubleshooting

### Issue: "Cannot find module 'openai'"
**Solution:** Run `npm install openai` in `backend/src`

### Issue: "OPENAI_API_KEY is not set"
**Solution:** Add `OPENAI_API_KEY=sk-...` to `backend/src/.env`

### Issue: OpenAI parsing fails
**Check:**
1. API key is valid
2. OpenAI API is accessible
3. Request format is correct
4. Check console logs for details

**Note:** System automatically falls back to DeBERTa on failure

### Issue: High token usage
**Solution:**
- Review input text lengths
- Consider truncating very long sections
- Monitor usage via metadata

## 📚 Documentation

- **Full Documentation:** `backend/src/OPENAI_INTEGRATION.md`
- **Setup Script:** `backend/src/setup-openai.sh`
- **Environment Example:** `backend/src/.env.example`

## 🎉 Summary

**What Changed:**
- ✅ Added OpenAI GPT-4o-mini as parsing option
- ✅ Maintained DeBERTa parser (no breaking changes)
- ✅ Automatic fallback mechanism
- ✅ Token usage tracking
- ✅ Processing time logging
- ✅ Identical response schema
- ✅ No frontend changes required

**What Didn't Change:**
- ❌ Frontend code (works as-is)
- ❌ DeBERTa parser behavior
- ❌ API response schema
- ❌ Database structure
- ❌ Authentication flow

**Next Steps:**
1. Add your OpenAI API key to `.env`
2. Restart backend server
3. Test with frontend dropdown
4. Monitor token usage and costs
5. Enjoy improved parsing accuracy! 🚀
