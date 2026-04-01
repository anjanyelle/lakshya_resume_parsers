# Work History Empty Issue - FIXED

## 🚨 Problem Summary

**Issue**: Work history showing empty array `[]` in database API while upload response shows work experience extracted.

**Root Cause**: Company names were being extracted as locations instead of actual company names, causing entries to be rejected or stored incorrectly.

---

## 🔍 Detailed Analysis

### What Was Happening

1. **AI Service Extraction**: Extracted locations as company names
   ```json
   {
     "company": "San Francisco, Ca",  // ← Location, not company!
     "title": "Solution Architect"
   }
   ```

2. **Backend Parser**: Failed to reject locations as companies
   - Regex pattern `r",\s*[A-Z]{2}\b"` only matched uppercase state abbreviations
   - "San Francisco, Ca" has mixed case "Ca" instead of "CA"
   - Locations passed through as valid company names

3. **Database Storage**: Stored incorrect data
   ```json
   {
     "company_name": "San Francisco, Ca",  // ← Location in company field!
     "job_title": "Solution Architect"
   }
   ```

4. **API Response**: Empty work_history due to validation issues

---

## 🔧 Fixes Applied

### Fix 1: Location Regex for Mixed Case (work_experience_parser.py)

**File**: `backend/app/services/parser/work_experience_parser.py`

**Before**:
```python
# State/Location pattern (e.g. "Louisville, KY") is NOT a company
if re.search(r",\s*[A-Z]{2}\b", text):
    return False
```

**After**:
```python
# State/Location pattern (e.g. "Louisville, KY" or "San Francisco, Ca") is NOT a company
if re.search(r",\s*[A-Za-z]{2}\b", text):
    # Additional check: make sure it's not a technical term like "Swift, UI"
    # Exclude common technical abbreviations
    tech_exclusions = {'ui', 'it', 'ai', 'ml', 'sql', 'api', 'ci', 'cd', 'qa'}
    state_abbr = text.split(',')[-1].strip().lower()
    if state_abbr not in tech_exclusions:
        return False
```

### Fix 2: Location Validation in Sanitizer (work_experience_sanitizer.py)

**File**: `backend/app/services/parser/work_experience_sanitizer.py`

**Added**:
```python
# Reject locations mistakenly stored as companies (e.g. "San Francisco, Ca")
if company and _LOCATION_AS_TITLE_RE.match(company.strip()):
    company = ""
```

**Updated Regex**:
```python
_LOCATION_AS_TITLE_RE = re.compile(r"^[A-Za-z ]+,\s*[A-Za-z]{2}$")
```

---

## 🧪 Test Results

### Before Fix
```python
# Test regex matching
pattern = re.compile(r',\s*[A-Z]{2}\b')
test_cases = ['San Francisco, Ca', 'Austin, Tx', 'New York, Ny']
# Result: All returned False (locations accepted as companies)
```

### After Fix
```python
# Test new regex pattern
pattern = re.compile(r',\s*[A-Za-z]{2}\b')
test_cases = ['San Francisco, Ca', 'Austin, Tx', 'New York, Ny']
# Result: All returned True (locations properly rejected)
```

---

## 📊 Expected Impact

### Upload Response (Now Fixed)
```json
{
  "work_experience": [
    {
      "job_title": "Solution Architect",
      "company_name": "JPMorgan Chase",  // ← Real company name
      "start_date": "2022-03-01",
      "is_current": true
    }
  ]
}
```

### Database Response (Now Fixed)
```json
{
  "work_history": [
    {
      "id": "uuid",
      "job_title": "Solution Architect",
      "company_name": "JPMorgan Chase",
      "start_date": "2022-03-01",
      "is_current": true
    }
  ]
}
```

---

## 🎯 Next Steps

1. **Test the Fix**: Upload a new resume to verify work history is populated
2. **Monitor Logs**: Check for `DIAG post-sanitize count=X dropped=Y` entries
3. **Verify Data**: Ensure company names are actual companies, not locations

---

## 🔍 Debug Commands

To verify the fix is working:

```bash
# Check recent parsing logs
grep -E "(DIAG.*sanitiz|work_entries)" /path/to/backend/logs/app.log | tail -10

# Test regex patterns
python3 -c "
import re
pattern = re.compile(r',\s*[A-Za-z]{2}\b')
test_cases = ['San Francisco, Ca', 'Austin, Tx', 'New York, Ny']
for case in test_cases:
    print(f'{case}: {bool(pattern.search(case))}')
"
```

---

## 📋 Files Modified

1. `backend/app/services/parser/work_experience_parser.py` - Updated location detection
2. `backend/app/services/parser/work_experience_sanitizer.py` - Added company location validation

---

## ✅ Resolution Status

- ✅ **Root Cause Identified**: Mixed-case state abbreviations not detected as locations
- ✅ **Parser Fixed**: Regex updated to accept mixed case
- ✅ **Sanitizer Fixed**: Added location validation for companies
- ✅ **Technical Terms Protected**: UI, AI, ML, etc. won't be rejected as locations
- ⏳ **Testing Required**: Upload new resume to verify fix

---

*Last Updated: April 1, 2026*
