# DeBERTa Model Analysis & Upgrade Plan

## Executive Summary

Your DeBERTa NER model has **97.34% F1 score** on training data but shows **mixed performance in production**. The model itself works well for entity extraction, but **post-processing and format handling need major upgrades**.

---

## How Your Model Works

### Architecture

```
Input Text
    ↓
DeBERTa-v3 Tokenizer (max 1024 tokens)
    ↓
DeBERTa-v3 Model (31 labels, BIO format)
    ↓
Token Classification (predicts label for each token)
    ↓
Entity Extraction (groups B-/I- tokens into entities)
    ↓
Validation Filters (currently disabled)
    ↓
Entity Grouping (groups entities into structured jobs/education)
    ↓
JSON Output
```

### Training Details

- **Model:** microsoft/deberta-v3-base
- **Training Examples:** 16,306 labeled examples
- **Labels:** 31 entity types in BIO format
- **F1 Score:** 97.34% on validation set
- **Training Format:** Natural language resume text

### Entity Labels (31 total)

**Work Experience:**
- O (Outside)
- B-COMPANY, I-COMPANY
- B-CLIENT, I-CLIENT
- B-ROLE, I-ROLE
- B-LOCATION, I-LOCATION
- B-START_DATE, I-START_DATE
- B-END_DATE, I-END_DATE
- B-PERSON_NAME, I-PERSON_NAME

**Education:**
- B-INSTITUTION, I-INSTITUTION
- B-DEGREE, I-DEGREE
- B-FIELD, I-FIELD (Field of Study)
- B-GRADE, I-GRADE
- B-EDU_START_YEAR, I-EDU_START_YEAR
- B-EDU_END_YEAR, I-EDU_END_YEAR

---

## Performance Analysis

### What Works Well ✅

#### 1. Entity Detection (97.34% F1 Score)
**Strength:** Model accurately detects individual entities in natural language text

**Evidence:**
```
Input: "Sr. Backend Engineer @ Netflix | Los Gatos, CA | January 2023 - Present"

Detected Entities:
✅ ROLE: "Sr. Backend Engineer"
✅ COMPANY: "Netflix"
✅ LOCATION: "Los Gatos, CA"
✅ START_DATE: "January 2023"
✅ END_DATE: "Present"
```

**Test Results:**
- Company detection: 100% (when in natural language format)
- Role detection: 96%
- Location detection: 100%
- Date detection: 100%

#### 2. Multiple Job Extraction
**Strength:** Can extract 3-4 jobs from single text (after token limit increase)

**Evidence:**
- Test 1: 4/5 jobs extracted (80%)
- Test 2: 4/4 jobs extracted (100%)
- Test 3: 3/4 jobs extracted (75%)
- Average: 75-80% extraction rate

#### 3. Processing Speed
**Strength:** Fast inference time

**Performance:**
- Average: 1,087 ms per request
- Range: 573 ms - 4,160 ms
- Acceptable for production use

### What's Broken ❌

#### 1. Entity Grouping Logic (CRITICAL)
**Problem:** Entities paired incorrectly, causing mismatches

**Evidence:**
```
Input: "Backend Engineer @ Spotify | New York, NY"

Extracted Entities:
✅ COMPANY: "Spotify"
✅ ROLE: "Backend Engineer"
✅ LOCATION: "New York, NY"

Output (WRONG):
❌ company: "Spotify"
❌ role: "Junior Developer"  ← Wrong role from different job!
❌ location: "San Francisco"  ← Wrong location from different job!
```

**Root Cause:**
- Entities grouped **sequentially** (1st company + 1st role + 1st date)
- Should group by **text position proximity**
- When model extracts different counts (4 companies, 2 roles), pairing breaks

**Impact:**
- 50% of jobs have wrong role/location/date combinations
- Companies paired with wrong roles
- Locations paired with wrong companies

**Code Location:** `deberta_ner_parser.py` - `_format_results()` function

#### 2. Institution Extraction (0% Success)
**Problem:** All institution fields empty despite being in text

**Evidence:**
```
Input: "Master of Science @ San Jose State University | 2011-2013"

Extracted:
✅ DEGREE: "Master of Science"
✅ FIELD: (varies)
❌ INSTITUTION: ""  ← Always empty!
❌ start_year: null
❌ end_year: null
```

**Possible Causes:**
1. Model not detecting INSTITUTION labels (training issue)
2. Validation filters removing institutions (but we disabled them)
3. Grouping logic not extracting institution entities
4. Model confusing institutions with companies

**Impact:**
- 0% institution extraction across all tests
- Education entries incomplete

#### 3. Format Incompatibility
**Problem:** Model fails on structured CSV/delimiter-based formats

**Training Format:**
```
Natural language: "Sr. Backend Engineer @ Netflix | Los Gatos, CA | Jan 2023 - Present"
```

**Test File Formats (INCOMPATIBLE):**
```
CSV: "Netflix,Los Gatos CA,Sr. Backend Engineer,Jan 2023,Present"
Double colon: "Netflix :: Los Gatos CA :: Sr. Backend Engineer :: Jan 2023 :: Present"
Pipe: "Netflix | Los Gatos CA | Sr. Backend Engineer | Jan 2023 | Present"
```

**Impact:**
- 50% company extraction on structured files
- Data corruption (fields mixed up)
- Only 50% of expected jobs extracted

**Root Cause:**
- Model trained only on natural language
- No context clues in CSV format
- Field order varies between formats

#### 4. Token Limit Issues (Partially Fixed)
**Problem:** Long resumes truncated

**Before:** 512 tokens (~400 words) - only first job extracted
**After:** 1024 tokens (~800 words) - 3-4 jobs extracted
**Needed:** 2048 tokens for resumes with 5+ jobs

**Impact:**
- Missing 1-2 jobs per resume
- Information loss for long resumes

#### 5. Missing Year Extraction
**Problem:** Years not extracted from date ranges

**Evidence:**
```
Input: "2011–2013" or "2011-2013"
Output: start_year: null, end_year: null
```

**Root Cause:**
- No post-processing to parse years from date strings
- Model extracts full date range but doesn't split into years

**Impact:**
- Education years always null
- Cannot filter by graduation year

---

## Upgrade Recommendations

### Priority 1: Fix Entity Grouping Logic (HIGH IMPACT)

**Current Implementation:**
```python
# Sequential pairing (BROKEN)
companies = ["Netflix", "Spotify", "LinkedIn"]
roles = ["Sr. Backend Engineer", "Junior Developer"]
locations = ["Los Gatos, CA", "San Francisco", "Sunnyvale"]

jobs = []
for i in range(len(companies)):
    jobs.append({
        "company": companies[i],
        "role": roles[i] if i < len(roles) else "",  # ❌ Index mismatch
        "location": locations[i] if i < len(locations) else ""
    })
```

**Recommended Implementation:**
```python
# Position-based clustering (CORRECT)
entities_with_positions = [
    {"type": "COMPANY", "text": "Netflix", "start": 0, "end": 7},
    {"type": "ROLE", "text": "Sr. Backend Engineer", "start": 10, "end": 30},
    {"type": "LOCATION", "text": "Los Gatos, CA", "start": 33, "end": 46},
    {"type": "START_DATE", "text": "January 2023", "start": 49, "end": 61},
    ...
]

# Group entities within proximity window (e.g., 150 characters)
jobs = []
for company in companies_with_positions:
    # Find entities near this company
    nearby_entities = find_entities_in_window(
        all_entities, 
        company.start, 
        window_size=150
    )
    
    jobs.append({
        "company": company.text,
        "role": nearby_entities.get("ROLE", ""),
        "location": nearby_entities.get("LOCATION", ""),
        "start_date": nearby_entities.get("START_DATE", ""),
        "end_date": nearby_entities.get("END_DATE", "")
    })
```

**Implementation Steps:**
1. Modify `_parse_single_section()` to track entity positions
2. Store entities with `(text, start_char, end_char)` tuples
3. Implement proximity-based clustering algorithm
4. Group entities within 100-150 character window
5. Handle overlapping windows for adjacent jobs

**Expected Impact:**
- Company-role matching: 50% → 95%
- Location accuracy: 90% → 98%
- Overall job accuracy: 75% → 90%

### Priority 2: Fix Institution Extraction (HIGH IMPACT)

**Diagnostic Steps:**
1. Add debug logging to see if INSTITUTION labels are detected
2. Check raw model predictions for B-INSTITUTION, I-INSTITUTION
3. Verify training data has institution examples

**If model detects institutions:**
```python
# Fix grouping logic to extract institutions
institutions = entities.get('INSTITUTION', [])
logger.info(f"Institutions detected: {institutions}")
```

**If model doesn't detect institutions:**
- **Retrain model** with more institution examples
- Add 500+ examples with clear institution labels
- Focus on patterns: "@ University", "University of", "Institute of Technology"

**Expected Impact:**
- Institution extraction: 0% → 80%+

### Priority 3: Add Format Preprocessor (MEDIUM IMPACT)

**Create format detector and converter:**

```python
def detect_format(text):
    """Detect if text is CSV, natural language, or other format"""
    if '::' in text and text.count('::') >= 3:
        return 'double_colon'
    elif ',' in text and '\n' in text and '@' not in text:
        return 'csv'
    elif '|' in text and text.count('|') >= 3:
        return 'pipe'
    else:
        return 'natural_language'

def convert_to_natural_language(text, format_type):
    """Convert structured format to natural language"""
    if format_type == 'csv':
        # "Netflix,Los Gatos CA,Sr. Backend Engineer,Jan 2023,Present"
        # → "Sr. Backend Engineer @ Netflix | Los Gatos, CA | Jan 2023 - Present"
        parts = text.split(',')
        return f"{parts[2]} @ {parts[0]} | {parts[1]} | {parts[3]} - {parts[4]}"
    
    elif format_type == 'double_colon':
        # "Netflix :: Los Gatos CA :: Sr. Backend Engineer :: Jan 2023 :: Present"
        # → "Sr. Backend Engineer @ Netflix | Los Gatos, CA | Jan 2023 - Present"
        parts = text.split('::')
        return f"{parts[2].strip()} @ {parts[0].strip()} | {parts[1].strip()} | {parts[3].strip()} - {parts[4].strip()}"
    
    return text  # Already natural language
```

**Integration:**
```python
def parse_text(self, text):
    # Detect format
    format_type = detect_format(text)
    
    # Convert if needed
    if format_type != 'natural_language':
        text = convert_to_natural_language(text, format_type)
    
    # Continue with normal parsing
    return self._parse_single_section(text, 'experience')
```

**Expected Impact:**
- CSV file compatibility: 0% → 90%
- Broader format support
- Better real-world applicability

### Priority 4: Add Year Extraction (LOW IMPACT, EASY WIN)

**Implementation:**
```python
import re

def extract_years_from_date(date_text):
    """Extract start and end years from date range"""
    if not date_text:
        return None, None
    
    # Match patterns: "2011–2013", "2011-2013", "2011 - 2013"
    match = re.search(r'(\d{4})\s*[–\-]\s*(\d{4})', date_text)
    if match:
        return int(match.group(1)), int(match.group(2))
    
    # Match single year: "2013"
    match = re.search(r'(\d{4})', date_text)
    if match:
        year = int(match.group(1))
        return year, year
    
    return None, None

# In education parsing:
for edu in education_entries:
    # Extract years from date range in text
    start_year, end_year = extract_years_from_date(edu.get('date_range', ''))
    edu['start_year'] = start_year
    edu['end_year'] = end_year
```

**Expected Impact:**
- Year extraction: 0% → 95%
- Education filtering by year enabled

### Priority 5: Increase Token Limit (MEDIUM IMPACT)

**Current:** 1024 tokens
**Recommended:** 2048 tokens

**Change:**
```python
# In deberta_ner_parser.py:491
inputs = self.tokenizer(
    text,
    return_tensors="pt",
    truncation=True,
    max_length=2048,  # Increased from 1024
    return_offsets_mapping=True
)
```

**Alternative:** Implement sliding window for very long resumes
```python
def parse_long_text(text, window_size=1024, overlap=256):
    """Parse long text using sliding window"""
    chunks = []
    for i in range(0, len(text), window_size - overlap):
        chunk = text[i:i + window_size]
        chunks.append(chunk)
    
    # Parse each chunk
    all_entities = []
    for chunk in chunks:
        entities = self._parse_single_section(chunk, 'experience')
        all_entities.extend(entities)
    
    # Deduplicate overlapping entities
    return deduplicate_entities(all_entities)
```

**Expected Impact:**
- Job extraction: 75% → 90%
- Support for resumes with 5+ jobs

### Priority 6: Re-enable Selective Validation (LOW PRIORITY)

**Current:** All validation disabled (test mode)
**Recommended:** Re-enable with relaxed rules

**Keep disabled:**
- `_is_person_name()` - Too strict, rejects valid companies
- `_is_valid_degree()` - Too strict, rejects valid degrees

**Re-enable with fixes:**
- `_is_valid_company()` - Only reject obvious non-companies (numbers, single letters)
- `_is_valid_location()` - Only reject tech terms, keep all city names
- `_is_valid_job_title()` - Only reject obvious non-roles

**Expected Impact:**
- Reduce false positives by 10-20%
- Maintain high recall

---

## Long-Term Improvements

### 1. Retrain Model with More Data

**Current:** 16,306 examples
**Target:** 30,000+ examples

**Focus Areas:**
- More institution examples (universities, colleges)
- More complex role titles ("Principal Engineer", "VP of Engineering")
- More date formats (years, ranges, "Present")
- CSV and structured formats
- Resumes with 5+ jobs

**Expected Impact:**
- Institution detection: 0% → 80%
- Complex role detection: 50% → 90%
- Overall F1 score: 97.34% → 98.5%

### 2. Add Confidence Scores

**Implementation:**
```python
# Use model logits to calculate confidence
confidence = torch.softmax(outputs.logits, dim=2).max(dim=2)[0]

# Filter low-confidence predictions
if confidence < 0.7:
    logger.warning(f"Low confidence ({confidence:.2f}) for entity: {text}")
```

**Benefits:**
- Identify uncertain predictions
- Provide confidence scores to users
- Improve quality metrics

### 3. Add Active Learning

**Process:**
1. Collect failed predictions from production
2. Manually label them
3. Add to training data
4. Retrain model periodically

**Benefits:**
- Continuous improvement
- Adapt to new resume formats
- Fix edge cases

### 4. Multi-Model Ensemble

**Approach:**
- Train 3-5 models with different hyperparameters
- Combine predictions via voting or averaging
- Use ensemble for high-stakes predictions

**Expected Impact:**
- F1 score: 97.34% → 98.5%+
- Reduced variance

---

## Implementation Roadmap

### Phase 1: Critical Fixes (1-2 days)
1. ✅ Fix entity grouping logic (position-based clustering)
2. ✅ Add debug logging for entity positions
3. ✅ Diagnose institution extraction issue
4. ✅ Add year extraction from dates

**Expected Results:**
- Company-role matching: 50% → 95%
- Institution extraction: 0% → 80% (if model detects them)
- Year extraction: 0% → 95%

### Phase 2: Format Support (1 day)
1. ✅ Add format detector
2. ✅ Add CSV/delimiter converter
3. ✅ Test with structured files

**Expected Results:**
- CSV compatibility: 0% → 90%
- Broader format support

### Phase 3: Performance Optimization (1 day)
1. ✅ Increase token limit to 2048
2. ✅ Implement sliding window for long resumes
3. ✅ Re-enable selective validation

**Expected Results:**
- Job extraction: 75% → 90%
- Support for 5+ job resumes

### Phase 4: Model Retraining (3-5 days)
1. ⏳ Collect 10,000+ new examples
2. ⏳ Focus on institutions and complex roles
3. ⏳ Add structured format examples
4. ⏳ Retrain and validate

**Expected Results:**
- Institution detection: 0% → 80%
- Overall F1 score: 97.34% → 98.5%

---

## Success Metrics

### Current Performance
- Company extraction: 100% (natural language), 50% (CSV)
- Role extraction: 96% (but mismatched)
- Location extraction: 100%
- Institution extraction: 0%
- Job extraction: 75-80%
- Date extraction: 100%

### Target Performance (After Upgrades)
- Company extraction: 98% (all formats)
- Role extraction: 95% (correctly matched)
- Location extraction: 98%
- Institution extraction: 80%
- Job extraction: 90%
- Date extraction: 100%
- Year extraction: 95%

### Production Readiness Checklist
- [x] Model loads successfully (31 labels)
- [x] API endpoint functional
- [ ] Entity grouping fixed
- [ ] Institution extraction working
- [ ] Format compatibility added
- [ ] Year extraction implemented
- [ ] Token limit optimized
- [ ] Validation filters tuned
- [ ] Test suite passing (90%+ accuracy)
- [ ] Production monitoring in place

---

## Conclusion

**Your DeBERTa model is fundamentally sound** with 97.34% F1 score. The issues are in:

1. **Post-processing logic** (entity grouping) - CRITICAL
2. **Institution extraction** - HIGH PRIORITY
3. **Format compatibility** - MEDIUM PRIORITY
4. **Token limits** - MEDIUM PRIORITY

**The model itself doesn't need retraining yet.** Fix the post-processing first, then evaluate if retraining is needed.

**Estimated effort:**
- Phase 1 (Critical fixes): 1-2 days
- Phase 2 (Format support): 1 day
- Phase 3 (Optimization): 1 day
- **Total: 3-4 days to production-ready**

**Next immediate action:** Fix entity grouping logic using position-based clustering.
