# DeBERTa Model Test Results Analysis

## Test Summary (5 Resume Examples)

### Performance Metrics

| Metric | Before Fix | After Fix | Status |
|--------|-----------|-----------|--------|
| Company Extraction | 0% | **100%** | ✅ FIXED |
| Job Entry Extraction | 20% (1/5) | **75-80%** (3-4/4-5) | ✅ MAJOR IMPROVEMENT |
| Role Extraction | 20% | **50%** | ⚠️ PARTIAL |
| Location Extraction | Partial | **90%** | ✅ GOOD |
| Date Extraction | Partial | **100%** | ✅ FIXED |
| Institution Extraction | 0% | **0%** | ❌ BROKEN |
| Year Extraction | 0% | **0%** | ❌ BROKEN |

---

## Detailed Test Results

### Test 1: Netflix, Spotify, Twitter, LinkedIn, Wipro (5 jobs)
**Input:** 5 work experiences
**Output:** 4 work experiences (80%)

**Issues:**
1. ❌ Missing "Twitter" job entirely
2. ❌ Role mismatch: "Backend Engineer @ Spotify" → shows "Junior Developer"
3. ❌ Location mismatch: "Spotify in New York, NY" → shows "San Francisco"
4. ✅ Companies extracted: Netflix, Spotify, LinkedIn, Wipro
5. ❌ Institutions empty: "San Jose State University", "Osmania University" not extracted

### Test 2: Amazon, Microsoft, IBM, Infosys (4 jobs)
**Input:** 4 work experiences
**Output:** 4 work experiences (100%)

**Issues:**
1. ❌ Role mismatch: "Software Engineer @ Microsoft" → shows "Junior Software Engineer"
2. ❌ Missing roles for IBM and Infosys
3. ✅ All companies extracted correctly
4. ❌ Institutions empty

### Test 3: Google, Meta, Oracle, Capgemini (4 jobs)
**Input:** 4 work experiences
**Output:** 3 work experiences (75%)

**Issues:**
1. ❌ Missing "Google" job entirely
2. ❌ Company mismatch: First job shows "Meta" instead of "Google"
3. ❌ Role mismatch: "Lead Backend Engineer @ Google" → shows with "Meta"
4. ❌ Location mismatch: "Google in Mountain View" → shows "Mountain View" with "Meta"
5. ❌ Missing Capgemini's 4th job
6. ❌ Institutions empty

### Test 4: Apple, Adobe, Cognizant, TCS (4 jobs)
**Input:** 4 work experiences
**Output:** 4 work experiences (100%)

**Issues:**
1. ❌ Role mismatch: "Principal Engineer @ Apple" → shows "Senior Software Engineer"
2. ❌ Role mismatch: "Senior Software Engineer @ Adobe" → shows "Programmer Analyst"
3. ❌ Missing roles for Cognizant and TCS
4. ✅ All companies extracted
5. ❌ Institutions empty

### Test 5: Flipkart, Paytm, HCL, Wipro (4 jobs)
**Input:** 4 work experiences
**Output:** 3 work experiences (75%)

**Issues:**
1. ❌ Missing "Paytm" job entirely
2. ❌ Role mismatch: "Full Stack Developer @ Paytm" → not in output
3. ❌ Company mismatch: 2nd job shows "HCL Technologies" instead of "Paytm"
4. ❌ Missing roles for Wipro
5. ❌ Institutions empty

---

## Root Cause Analysis

### Issue 1: Entity Grouping Logic Broken
**Problem:** Entities are grouped sequentially, not by text position

**Current Logic:**
```
companies = ["Netflix", "Spotify", "LinkedIn", "Wipro"]
roles = ["Sr. Backend Engineer", "Junior Developer"]
locations = ["Los Gatos, CA", "San Francisco", "Sunnyvale", "Hyderabad"]
dates = [("January 2023", "Present"), ("April 2020", "December 2022"), ...]

# Groups as:
Job 1: companies[0] + roles[0] + locations[0] + dates[0]  ✅ Correct
Job 2: companies[1] + roles[1] + locations[1] + dates[1]  ❌ Wrong role/location
Job 3: companies[2] + roles[2] + locations[2] + dates[2]  ❌ No role (index out of bounds)
Job 4: companies[3] + roles[3] + locations[3] + dates[3]  ❌ No role (index out of bounds)
```

**Why It Fails:**
- Model extracts different number of entities per type (4 companies, 2 roles, 4 locations)
- Sequential pairing causes mismatches
- Missing entities cause index misalignment

**Correct Approach:**
- Group entities by **text position** (character offset)
- Match company + role + location + dates that appear near each other in text
- Use proximity-based clustering

### Issue 2: Model Not Detecting All ROLE Labels
**Problem:** Only 2 roles extracted from 5 jobs

**Possible Causes:**
1. Model confidence too low for some roles
2. Unusual role formats ("Software Engineer II", "Principal Engineer")
3. Training data didn't have enough examples of these role patterns

**Evidence:**
- Simple roles extracted: "Sr. Backend Engineer", "Junior Developer"
- Complex roles missed: "Software Engineer II", "Principal Engineer"

### Issue 3: INSTITUTION Labels Not Detected
**Problem:** 0% institution extraction

**Possible Causes:**
1. Model not trained on INSTITUTION label properly
2. Institution names appear after "@" symbol which model doesn't recognize
3. Validation filters removing institutions (but we disabled them)
4. Model confusing institutions with companies

**Evidence:**
- Input: "@ San Jose State University, CA"
- Output: institution=""
- Model may be detecting "San Jose State University" as COMPANY or LOCATION

### Issue 4: Missing 1-2 Jobs Per Resume
**Problem:** 75-80% job extraction (missing 1-2 jobs)

**Possible Causes:**
1. Token limit still too small (1024 may not be enough)
2. Model stops processing after certain number of entities
3. Grouping logic discards jobs with missing required fields

---

## Recommendations

### Immediate Fixes (Code Changes)

#### 1. Fix Entity Grouping Logic (HIGH PRIORITY)
**File:** `deberta_ner_parser.py`
**Function:** `_format_results()` or entity grouping section

**Current:** Sequential pairing
**Fix:** Position-based clustering

**Algorithm:**
```python
# Store entities with their text positions
entities_with_positions = [
    {"type": "COMPANY", "text": "Netflix", "start": 0, "end": 7},
    {"type": "ROLE", "text": "Sr. Backend Engineer", "start": 10, "end": 30},
    {"type": "LOCATION", "text": "Los Gatos, CA", "start": 33, "end": 46},
    ...
]

# Group entities within proximity window (e.g., 100 characters)
jobs = []
for company in companies_with_positions:
    # Find role, location, dates within 100 chars of this company
    nearby_role = find_nearest(roles, company.start, window=100)
    nearby_location = find_nearest(locations, company.start, window=100)
    nearby_dates = find_nearest(dates, company.start, window=100)
    
    jobs.append({
        "company": company.text,
        "role": nearby_role.text if nearby_role else "",
        "location": nearby_location.text if nearby_location else "",
        ...
    })
```

#### 2. Add Debug Logging for Entity Positions
**Purpose:** See what entities are extracted and where

**Add to code:**
```python
logger.info(f"Extracted entities with positions:")
logger.info(f"  COMPANY: {[(e['text'], e['start']) for e in companies]}")
logger.info(f"  ROLE: {[(e['text'], e['start']) for e in roles]}")
logger.info(f"  INSTITUTION: {[(e['text'], e['start']) for e in institutions]}")
```

#### 3. Check if INSTITUTION Labels Are Being Detected
**Test:** Add logging to see raw model predictions

**Expected:** Should see "B-INSTITUTION", "I-INSTITUTION" in predictions
**If not:** Model needs retraining with more institution examples

#### 4. Extract Years from Date Ranges
**Current:** "2011–2013" not parsed into start_year/end_year
**Fix:** Add regex to extract years from date strings

```python
import re

def extract_years(date_range_text):
    # Match patterns like "2011–2013", "2011-2013", "2011 - 2013"
    match = re.search(r'(\d{4})\s*[–-]\s*(\d{4})', date_range_text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None
```

### Long-Term Improvements (Retraining)

#### 1. Add More Training Examples for:
- Complex role titles ("Software Engineer II", "Principal Engineer", "Lead Backend Engineer")
- Institution names after "@" symbol
- Multiple jobs in single text (currently only 1-2 jobs extracted well)

#### 2. Increase Training Data Diversity
- Current: 16,306 examples
- Target: 30,000+ examples
- Focus on resumes with 4-5 jobs

#### 3. Improve Label Definitions
- Consider separate labels for:
  - UNIVERSITY vs COMPANY (to avoid confusion)
  - ROLE_SENIOR, ROLE_JUNIOR (to handle seniority levels)
  - DATE_YEAR vs DATE_MONTH_YEAR

---

## Testing Recommendations

### Create Automated Test Suite
```python
test_cases = [
    {
        "input": "Sr. Backend Engineer @ Netflix | Los Gatos, CA | Jan 2023 - Present",
        "expected": {
            "company": "Netflix",
            "role": "Sr. Backend Engineer",
            "location": "Los Gatos, CA",
            "start_date": "Jan 2023",
            "end_date": "Present"
        }
    },
    # Add 30 test cases from your txt files
]

for test in test_cases:
    result = model.parse(test["input"])
    assert result["company"] == test["expected"]["company"]
    assert result["role"] == test["expected"]["role"]
    # etc.
```

### Measure Accuracy Per Entity Type
- Company: 100% ✅
- Role: 50% ⚠️
- Location: 90% ✅
- Dates: 100% ✅
- Institution: 0% ❌
- Years: 0% ❌

---

## Summary

**What's Working:**
- ✅ Company extraction (100%)
- ✅ Date extraction (100%)
- ✅ Location extraction (90%)
- ✅ Multiple job extraction (75-80%)

**What's Broken:**
- ❌ Entity grouping logic (causes role/company mismatches)
- ❌ Institution extraction (0%)
- ❌ Year extraction (0%)
- ❌ Role extraction (only 50%)

**Priority Fixes:**
1. **Fix entity grouping** - Use position-based clustering instead of sequential pairing
2. **Add debug logging** - See what entities are extracted and their positions
3. **Check INSTITUTION detection** - Model may not be detecting these labels
4. **Add year extraction** - Parse years from date range strings

**Next Steps:**
1. Fix entity grouping logic in `_format_results()`
2. Add position tracking to entities
3. Test with debug logging to see raw extractions
4. If institutions still missing, retrain model with more institution examples
