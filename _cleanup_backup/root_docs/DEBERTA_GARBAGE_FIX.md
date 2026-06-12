# DeBERTa Garbage Extraction Fix

## Problem Identified

The DeBERTa NER model was extracting garbage as degrees from the resume:

```json
{"degree": "("},              // Parenthesis!
{"degree": "Certified"},      // Random word
{"degree": "Project"},        // Random word
{"degree": "Fundamentals"},   // Random word
{"degree": "Operational"},    // Adjective
{"degree": "Administrative"}  // Adjective
```

## Root Cause

The DeBERTa model had validation filters for:
- ✅ Companies (`_is_valid_company`)
- ✅ Job titles (`_is_valid_job_title`)
- ✅ Locations (`_is_valid_location`)
- ❌ **Degrees (MISSING)**

Without a degree validation filter, the model was extracting random words tagged as "DEGREE" by the NER model without any quality checks.

## Solution Implemented

### 1. Created `_is_valid_degree()` Validation Method

**File:** `ai-service/parsers/deberta_ner_parser.py`

**Location:** Lines 765-807

**Logic:**
```python
def _is_valid_degree(self, text: str) -> bool:
    """Validate if text is a legitimate degree."""
    
    # Reject if too short (< 2 characters)
    if len(text) < 2:
        return False
    
    # Reject single punctuation: (, ), [, ], {, }, etc.
    if text in ['(', ')', '[', ']', '{', '}', ',', '.', ':', ';', '-', '_']:
        return False
    
    # Reject common non-degree single words
    invalid_single_words = [
        'certified', 'project', 'fundamentals', 'operational', 'administrative',
        'management', 'training', 'professional', 'business', 'technical',
        'advanced', 'basic', 'intermediate', 'senior', 'junior', 'lead',
        'the', 'and', 'or', 'in', 'at', 'of', 'for', 'with', 'to', 'from'
    ]
    if len(text.split()) == 1 and text.lower() in invalid_single_words:
        return False
    
    # Accept if contains degree keywords
    degree_keywords = [
        'bachelor', 'master', 'phd', 'doctorate', 'diploma', 'associate',
        'b.tech', 'm.tech', 'b.e', 'm.e', 'b.sc', 'm.sc', 'b.com', 'm.com',
        'b.a', 'm.a', 'mba', 'bba', 'bca', 'mca', 'llb', 'md', 'mbbs',
        'engineering', 'science', 'arts', 'commerce', 'technology',
        'degree', 'certification'
    ]
    if any(keyword in text.lower() for keyword in degree_keywords):
        return True
    
    # Accept multi-word degrees (likely legitimate)
    if len(text.split()) >= 2:
        # But reject common phrases
        common_phrases = ['business process', 'project management', 'risk management']
        if text.lower() in common_phrases:
            return False
        return True
    
    return False
```

### 2. Applied Filter to Entity Extraction

**Updated 3 locations in `_parse_single_section()` method:**

1. **Line 543:** When saving previous entity (B- tag)
2. **Line 575:** When ending entity (O tag)
3. **Line 596:** When saving final entity

**Code added:**
```python
elif current_entity == 'DEGREE' and not self._is_valid_degree(clean_text):
    pass  # Skip invalid degrees
```

## Expected Results

### Before Fix:
```json
"education": [
  {"degree": "("},
  {"degree": "Certified"},
  {"degree": "Project"},
  {"degree": "Fundamentals"},
  {"degree": "Operational"},
  {"degree": "Administrative"},
  {"degree": "Master of Business Administration"},  // Valid
  {"degree": "MBA"},                                 // Valid
  {"degree": "Bachelor of Commerce"}                 // Valid
]
```

### After Fix:
```json
"education": [
  {"degree": "Master of Business Administration"},  // Valid - contains "master"
  {"degree": "MBA"},                                 // Valid - contains "mba"
  {"degree": "Bachelor of Commerce"},                // Valid - contains "bachelor"
  {"degree": "Operations Management"}                // Valid - multi-word
]
```

**Garbage entries filtered out:**
- ❌ `"("` - Rejected (punctuation)
- ❌ `"Certified"` - Rejected (invalid single word)
- ❌ `"Project"` - Rejected (invalid single word)
- ❌ `"Fundamentals"` - Rejected (invalid single word)
- ❌ `"Operational"` - Rejected (invalid single word)
- ❌ `"Administrative"` - Rejected (invalid single word)

## Other Issues Still Present

### 1. Wrong Job Titles
```json
{"job_title": "internal business operations"}     // Should be "Senior Operations Manager"
{"job_title": "operational workflow"}             // Should be "Operations Manager"
```

**Cause:** DeBERTa model is extracting descriptions instead of actual job titles.

**Potential Fix:** The `_is_valid_job_title()` filter exists but may need stricter rules, OR the model needs retraining with better labeled data.

### 2. Missing Dates
All work experience has `null` dates despite resume containing:
- "2022 – Present"
- "2019 – 2022"
- "2017 – 2019"

**Cause:** DeBERTa model is not detecting date entities, OR the date extraction logic is failing.

**Potential Fix:** Check if the model is trained to detect START_DATE and END_DATE entities, and verify the date extraction code.

## Testing

To test the fix, re-upload the same resume and check the education section:

**Expected:**
- No parentheses as degrees
- No single-word adjectives as degrees
- Only legitimate degrees like "MBA", "Bachelor of Commerce", "Master of Business Administration"

## Files Modified

1. **`ai-service/parsers/deberta_ner_parser.py`**
   - Added `_is_valid_degree()` method (lines 765-807)
   - Applied filter at 3 locations (lines 543, 575, 596)

## Summary

✅ **Fixed:** Garbage degree extraction (parentheses, single words, adjectives)
⚠️ **Still needs fixing:** Wrong job titles, missing dates
🔧 **Method:** Added validation filter similar to existing company/job title/location filters

The pipeline now has proper post-processing validation for all major entity types:
- ✅ Companies
- ✅ Job Titles
- ✅ Locations
- ✅ **Degrees (NEW)**
