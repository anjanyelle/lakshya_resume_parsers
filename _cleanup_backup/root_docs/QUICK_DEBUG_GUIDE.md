# Quick Debugging Guide - Resume Parser

## 🚀 Quick Start: Debug Your Resume

### Step 1: Run the Debug Tool

```bash
cd ai-service
source venv/bin/activate
python3 debug_extraction_quality.py
```

This will show you:
- ✅ What text was extracted
- ✅ Which fields were found (name, email, phone, skills)
- ❌ What's missing (experience, education)
- 📊 Extraction quality metrics
- 💡 Specific recommendations

---

## 🔍 Understanding Your JSON Output

### Your Current Results (Rohan Shah Resume)

```json
{
  "name": "Rohan Shah",           // ✅ CORRECT
  "email": "rohan.shah...",       // ✅ CORRECT
  "phone": "1 (646) 555-2345",    // ✅ CORRECT
  "skills": [50+ skills],         // ✅ EXCELLENT
  "work_experience": [],          // ❌ EMPTY - Why?
  "education": [],                // ❌ EMPTY - Why?
  
  "extraction_quality": {
    "text_loss_percentage": 77.2  // ❌ 77% TEXT LOST!
  }
}
```

---

## ❓ Why Is Experience & Education Empty?

### Reason 1: High Text Loss (77%)

**What it means**: Only 23% of your resume text was extracted.

**Original DOCX**: 7,566 characters  
**Extracted**: 1,623 characters  
**LOST**: 5,943 characters (77%)

**Why this happens**:
- Resume uses **tables** for layout → Tables ARE extracted, but quality analyzer may be comparing wrong
- Resume has **text boxes** → Some text boxes may be skipped
- Resume has **headers/footers** → Contact info in header may be missed

### Reason 2: No LLM API Key

**What it means**: Experience extraction requires AI (Gemini/OpenAI) to understand complex job descriptions.

**Without LLM**:
```
❌ Can't parse: "Led cross-functional team of 5 analysts..."
❌ Can't extract: Job titles, companies, date ranges
```

**With LLM**:
```
✅ Extracts: Company, title, dates, description
✅ Understands: Context and relationships
```

---

## 🛠️ How to Fix

### Fix 1: Add LLM API Key (5 minutes)

```bash
# Get free API key from Google AI Studio
# https://makersuite.google.com/app/apikey

# Add to backend/.env
cd backend
echo "GEMINI_API_KEY=your_key_here" >> .env

# Restart backend
cd src
npm run dev
```

**Result**: Experience and education will be extracted ✅

---

### Fix 2: Test Extraction Quality (2 minutes)

```bash
cd ai-service
source venv/bin/activate
python3 debug_extraction_quality.py
```

Look for:
```
### EXTRACTION RESULTS ###
Total characters: 7,566    ← Should be close to original
Total words: 911           ← Should match resume
```

If numbers are low → Text extraction issue  
If numbers are high → Parsing/section detection issue

---

### Fix 3: Verify Sections Are Detected (1 minute)

In debug output, look for:

```
### SECTION DETECTION ###

EXPERIENCE: 3,245 chars     ← Should have content
Preview: Insight Analytics Corp | Data Analyst...

EDUCATION: 456 chars        ← Should have content
Preview: Bachelor of Science in Statistics...
```

If sections are empty → Section headers not detected  
If sections have content but parsing fails → Need LLM API key

---

## 📊 Understanding Extraction Quality Metrics

### What Each Metric Means

```json
"extraction_quality": {
  // How well text was extracted (0-100%)
  "extraction_quality_percentage": 0,
  
  // How similar extracted text is to original (0-100%)
  "text_similarity_percentage": 22.8,
  
  // How much text was lost (0-100%)
  "text_loss_percentage": 77.2,
  
  // Specific issues found
  "missing_sections": ["education", "professional experience"],
  "structure_loss": ["Bullet points lost: 12"],
  
  // Detailed comparison
  "metrics": {
    "original_text_length": 7566,      // From DOCX file
    "reconstructed_text_length": 1623, // What we extracted
    "missing_word_count": 191          // Words we couldn't find
  }
}
```

### Quality Levels

| Text Loss | Quality | What It Means |
|-----------|---------|---------------|
| 0-10% | ✅ Excellent | Perfect extraction |
| 10-30% | ✅ Good | Minor formatting loss |
| 30-50% | ⚠️ Fair | Some structure lost |
| 50-80% | ❌ Poor | Major text loss |
| 80-100% | ❌ Critical | Extraction failed |

**Your resume**: 77% loss = **Poor quality** ❌

---

## 🔧 Troubleshooting Steps

### Step 1: Check What Was Extracted

```bash
cd ai-service
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from parsers.text_extractor import TextExtractor

extractor = TextExtractor()
result = extractor.extract('../resumes/your_resume.docx')

print(f"Extracted {len(result['text'])} characters")
print("\nFirst 500 characters:")
print(result['text'][:500])
EOF
```

**Expected**: Should see your name, contact info, and start of experience section  
**If not**: Text extraction is failing

---

### Step 2: Check Section Detection

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from parsers.text_extractor import TextExtractor
from parsers.section_splitter import SectionSplitter

extractor = TextExtractor()
result = extractor.extract('../resumes/your_resume.docx')

splitter = SectionSplitter()
sections = splitter.split(result['text'])

for name, text in sections.items():
    print(f"{name}: {len(text)} chars")
EOF
```

**Expected**: Should see experience and education sections with content  
**If not**: Section headers not being detected

---

### Step 3: Check Field Extraction

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from parsers.master_parser import MasterParser

parser = MasterParser()
result = parser.parse('../resumes/your_resume.docx')

pd = result['parsed_data']
print(f"Name: {pd.get('name')}")
print(f"Email: {pd.get('email')}")
print(f"Skills: {len(pd.get('skills', []))}")
print(f"Experience: {len(pd.get('work_experience', []))}")
EOF
```

**Expected**: Should see all fields populated  
**If not**: Check which specific field is failing

---

## 💡 Common Issues & Solutions

### Issue: "work_experience": []

**Cause**: No LLM API key configured

**Solution**:
```bash
# Add to backend/.env
GEMINI_API_KEY=your_key_here
```

---

### Issue: "text_loss_percentage": 77.2

**Possible Causes**:
1. Quality analyzer comparing wrong texts
2. Resume uses complex layout (tables, text boxes)
3. Headers/footers not extracted

**Solution**:
```bash
# Test if text is actually extracted
cd ai-service
python3 debug_extraction_quality.py

# Look at "Total characters" - should be ~7000+
# If it's low (< 2000), extraction is failing
# If it's high (> 6000), quality analyzer is wrong
```

---

### Issue: Name extraction wrong

**Example**: Getting "Senior Data Analyst" instead of "Rohan Shah"

**Cause**: Name extraction picking up job title

**Solution**: Already fixed in latest code. Restart AI service:
```bash
cd ai-service
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🎯 Expected Results After Fixes

### Before (Current State)
```json
{
  "work_experience": [],
  "education": [],
  "text_loss_percentage": 77.2
}
```

### After (With Fixes)
```json
{
  "work_experience": [
    {
      "company": "Insight Analytics Corp",
      "title": "Data Analyst",
      "location": "New York, NY",
      "start_date": "Jan 2020",
      "end_date": "Present"
    }
  ],
  "education": [
    {
      "degree": "Bachelor of Science",
      "field": "Statistics",
      "school": "University Name"
    }
  ],
  "text_loss_percentage": 15
}
```

---

## 📞 Need More Help?

### Run Full Debug Report

```bash
cd ai-service
source venv/bin/activate
python3 debug_extraction_quality.py > debug_report.txt

# Send debug_report.txt for analysis
```

### Check Logs

```bash
# AI service logs
cd ai-service
tail -f logs/ai-service.log

# Backend logs
cd backend/src
npm run dev  # Shows logs in console
```

---

## ✅ Quick Checklist

- [ ] LLM API key added to backend/.env
- [ ] AI service restarted
- [ ] Backend restarted
- [ ] Test resume uploaded
- [ ] Debug tool run to verify extraction
- [ ] Experience and education populated in JSON
- [ ] Text loss < 30%

---

*Last Updated: March 30, 2026*
