# Work History Debug - Why Database Shows Empty

## 🔍 Issue Identified

**Upload Response Shows**: 3 work experiences extracted
```json
"work_experience": [
  {
    "job_title": "Present  Dallas, TX",     // ← This is a location, not a job title!
    "company_name": "",                    // ← Company name is empty!
    "description": "Project Overview: Modernization...",
    "start_date": "2020-04-01",
    "end_date": null,
    "is_current": true
  }
]
```

**Database Response Shows**: Empty work_history
```json
"work_history": []  // ← Empty because entries were rejected
```

---

## 🚨 Root Cause: Location-as-Title Rejection

The backend sanitizer (`work_experience_sanitizer.py`) has this validation:

```python
_LOCATION_AS_TITLE_RE = re.compile(r"^[A-Za-z ]+,\s*[A-Z][a-z]?$")

# Reject locations mistakenly stored as titles
if title_raw and _LOCATION_AS_TITLE_RE.match(title_raw.strip()):
    title_raw = ""  # ← Your job titles are being cleared!
```

Your job titles are being detected as locations:
- `"Present  Dallas, TX"` → Matches location pattern → Title cleared
- `"Chicago, IL"` → Matches location pattern → Title cleared  
- `"Atlanta, GA"` → Matches location pattern → Title cleared

When titles are cleared and company names are empty, entries are dropped:

```python
if not company and not title:
    continue  # ← Entry dropped!
```

---

## 🔧 Two-Level Fix Needed

### Level 1: Fix AI Service Title Extraction
The AI service should extract actual job titles, not locations.

**Current (Wrong)**:
```json
{
  "job_title": "Present  Dallas, TX",
  "company_name": ""
}
```

**Should Be**:
```json
{
  "job_title": "Cloud Solutions Engineer", 
  "company_name": "JPMorgan Chase"
}
```

### Level 2: Improve Backend Validation
The location regex is too aggressive and may reject valid titles.

---

## 🎯 Immediate Solution

Let me check what's in your actual experience section text to understand why titles are being extracted as locations.

### Debug Step 1: Check Experience Section Text

```bash
cd ai-service
source venv/bin/activate
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from parsers.text_extractor import TextExtractor
from parsers.section_splitter import SectionSplitter
import glob

resume_files = glob.glob('../resumes/*.pdf')
test_file = resume_files[0]

extractor = TextExtractor()
result = extractor.extract(test_file)
text = result['text']

splitter = SectionSplitter()
sections = splitter.split(text)
exp_section = sections.get('experience', '')

print(f"Experience section length: {len(exp_section)} chars")
print(f"\nFirst 800 chars:")
print(exp_section[:800])
print(f"\n---\nContains 'Cloud': {'Cloud' in exp_section}")
print(f"Contains 'Engineer': {'Engineer' in exp_section}")
print(f"Contains 'JPMorgan': {'JPMorgan' in exp_section}")
EOF
```

### Debug Step 2: Test Rule-Based Extraction Directly

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from parsers.experience_extractor import extract_experience
from parsers.text_extractor import TextExtractor
from parsers.section_splitter import SectionSplitter
import glob

resume_files = glob.glob('../resumes/*.pdf')
test_file = resume_files[0]

extractor = TextExtractor()
result = extractor.extract(test_file)
text = result['text']

splitter = SectionSplitter()
sections = splitter.split(text)
exp_section = sections.get('experience', '')

print(f"Testing rule-based extraction...")
experiences = extract_experience(exp_section)
print(f"Extracted {len(experiences)} jobs:")
for i, exp in enumerate(experiences, 1):
    print(f"{i}. Title: {exp.get('title', 'N/A')}")
    print(f"   Company: {exp.get('company', 'N/A')}")
    print(f"   Dates: {exp.get('start_date', 'N/A')} - {exp.get('end_date', 'N/A')}")
    print()
EOF
```

---

## 🔧 Backend Fix (Temporary)

If you want to allow location-like titles temporarily, modify the sanitizer:

**File**: `/backend/app/services/parser/work_experience_sanitizer.py`

```python
# Comment out or relax the location check:
# if title_raw and _LOCATION_AS_TITLE_RE.match(title_raw.strip()):
#     title_raw = ""
```

But this is a band-aid - the real issue is that job titles aren't being extracted correctly.

---

## 📊 Expected Fix Results

After fixing title extraction, you should see:

**Upload Response**:
```json
{
  "job_title": "Cloud Solutions Engineer",
  "company_name": "JPMorgan Chase",
  "description": "Project Overview: Modernization...",
  "start_date": "2020-04-01",
  "end_date": null,
  "is_current": true
}
```

**Database Response**:
```json
"work_history": [
  {
    "id": "uuid",
    "job_title": "Cloud Solutions Engineer",
    "company_name": "JPMorgan Chase",
    "start_date": "2020-04-01",
    "end_date": null,
    "is_current": true
  }
]
```

---

## 🎯 Next Steps

1. **Run the debug scripts** to see what text is actually in the experience section
2. **Check if rule-based extraction** gets proper job titles
3. **Fix the title extraction** in the AI service if needed
4. **Test again** to verify database population

The core issue is that locations are being extracted as job titles, causing the sanitizer to reject all entries.

---

*Last Updated: April 1, 2026*
