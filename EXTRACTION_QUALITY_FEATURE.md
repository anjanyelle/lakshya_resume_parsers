# Text Extraction Quality Analysis Feature

## Overview
This feature analyzes the quality of text extraction from resumes by comparing the original extracted text with the parsed structured output. It provides metrics to help identify data loss, missing information, and extraction issues.

## Implementation

### Files Created/Modified

1. **`ai-service/parsers/text_quality_analyzer.py`** (NEW)
   - `TextQualityAnalyzer` class that performs quality analysis
   - Compares original text with reconstructed text from parsed data
   - Calculates quality metrics and generates recommendations

2. **`ai-service/parsers/master_parser.py`** (MODIFIED)
   - Added `TextQualityAnalyzer` import and initialization
   - Added `_analyze_extraction_quality()` method
   - Integrated quality analysis into `_parse_text_pipeline()`
   - Updated `_assemble_final_result()` to include quality report

## API Response Format

The parse endpoint now includes an `extraction_quality` field in the response:

```json
{
  "candidate_id": "test-123",
  "status": "success",
  "name": "John Doe",
  "email": "john@example.com",
  ...
  "extraction_quality": {
    "extraction_quality_percentage": 85.5,
    "text_similarity_percentage": 82.3,
    "text_loss_percentage": 17.7,
    "missing_keywords": ["performance", "leadership", "agile"],
    "missing_sections": ["certifications"],
    "structure_loss": [
      "Bullet points lost: 5",
      "Date information lost: 2 dates missing"
    ],
    "recommendation": "Good extraction quality. Consider reviewing certifications sections.",
    "metrics": {
      "original_text_length": 2500,
      "reconstructed_text_length": 2100,
      "original_word_count": 450,
      "reconstructed_word_count": 380,
      "missing_word_count": 15
    }
  }
}
```

## Quality Metrics Explained

### 1. **extraction_quality_percentage** (0-100%)
Overall quality score calculated from:
- Text similarity (base score)
- Penalty for missing keywords (max 10%)
- Penalty for missing sections (5% per section)
- Penalty for structure loss (3% per issue)

### 2. **text_similarity_percentage** (0-100%)
Similarity ratio between original and reconstructed text using SequenceMatcher.

### 3. **text_loss_percentage** (0-100%)
Percentage of text that was lost during parsing (100 - text_similarity).

### 4. **missing_keywords** (array)
Important words from original text that don't appear in parsed output.
- Filters out common stop words
- Sorted by word length (longer = more important)
- Limited to top 20 keywords

### 5. **missing_sections** (array)
Resume sections detected in original text but not properly extracted.
Common sections checked:
- experience, education, skills, summary, objective
- projects, certifications, awards, publications
- professional experience, work experience, employment history

### 6. **structure_loss** (array)
Structural elements lost during extraction:
- Bullet points removed
- Table structure lost
- Paragraph structure simplified
- Date information lost
- Contact information lost (email, phone)

### 7. **recommendation** (string)
Actionable recommendation based on quality score:
- **90-100%**: "Excellent extraction quality. No action needed."
- **75-89%**: "Good extraction quality." + specific suggestions
- **60-74%**: "Moderate extraction quality." + warnings about text/structure loss
- **0-59%**: "Poor extraction quality. Use OCR for scanned documents or better parser."

## Usage Example

```python
# The quality analysis is automatically included in all parse responses
response = requests.post('http://localhost:8000/parse', json={
    'file_path': '/path/to/resume.pdf',
    'candidate_id': 'candidate-123'
})

data = response.json()
quality = data.get('extraction_quality', {})

print(f"Quality: {quality['extraction_quality_percentage']}%")
print(f"Recommendation: {quality['recommendation']}")

# Use for visualization/charts
if quality['extraction_quality_percentage'] < 70:
    print("⚠️ Low quality extraction - review needed")
```

## Visualization Ideas

### 1. Quality Score Gauge
```
┌─────────────────────────────────┐
│  Extraction Quality: 85.5%      │
│  ████████████████░░░░  Good     │
└─────────────────────────────────┘
```

### 2. Text Loss Chart
```
Original Text: ████████████████████ 100%
Extracted:     ████████████████░░░░  82%
Lost:          ░░░░                  18%
```

### 3. Missing Elements Breakdown
```
Missing Keywords:  15 words
Missing Sections:  1 section
Structure Issues:  3 problems
```

### 4. Quality Trend Over Time
```
Quality %
100 ┤
 90 ┤     ●
 80 ┤   ●   ●
 70 ┤ ●       ●
 60 ┤
    └─────────────→ Time
```

## Testing

Run the test script to verify the analyzer works:

```bash
cd ai-service
source venv/bin/activate
python test_quality_analyzer.py
```

Expected output:
```
📊 EXTRACTION QUALITY REPORT:
  Extraction Quality: 65.2%
  Text Similarity: 72.5%
  Text Loss: 27.5%
  Missing Keywords: 12 keywords
  ...
```

## Current Status

✅ **Completed:**
- TextQualityAnalyzer class implemented
- Integration into master_parser.py
- Quality metrics calculation
- Recommendation generation
- Test script created

⚠️ **Pending Verification:**
- Quality report appearing in API response
- Service initialization of TextQualityAnalyzer
- Hot reload picking up code changes

## Troubleshooting

If `extraction_quality` field is not appearing in API response:

1. **Restart AI service** to load new code:
   ```bash
   pkill -9 -f "python main.py"
   lsof -ti:8000 | xargs kill -9
   cd ai-service && source venv/bin/activate && python main.py
   ```

2. **Check logs** for TextQualityAnalyzer initialization:
   ```bash
   # Should see: "✅ TextQualityAnalyzer initialized"
   ```

3. **Check for errors** during quality analysis:
   ```bash
   # Should see: "🔍 Starting extraction quality analysis..."
   # Should see: "📊 Extraction quality: XX.X%"
   ```

4. **Verify quality_analyzer is not None**:
   ```python
   # In master_parser.__init__, check if initialization succeeded
   ```

## Next Steps

1. ✅ Verify feature works in production
2. Add quality metrics to frontend dashboard
3. Create visualization charts/graphs
4. Set up quality alerts for low-quality extractions
5. Track quality trends over time
6. Use quality metrics to improve parsing algorithms
