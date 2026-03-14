# 🗄️ JSON Storage in PostgreSQL Database

## 📍 **Exact Location of JSON Data**

### **Table: `parsing_jobs`**
```sql
-- The JSON is stored in the `parsed_data` column (JSONB type)
SELECT id, filename, status, parsed_data FROM parsing_jobs;
```

### **Column Details:**
- **`parsed_data`** (JSONB) - **This is where your complete parsed JSON lives!**
- **`parsed_json_path`** (String) - File path to JSON backup
- **`confidence_score`** (Float) - Overall parsing confidence
- **`raw_text`** (Text) - Original extracted text

---

## 🔍 **How to Access the JSON**

### **Method 1: Direct SQL Query**
```sql
-- Connect to PostgreSQL database
-- Host: localhost:5432
-- Database: resume_parser
-- User: postgres

-- View complete JSON for a specific job
SELECT parsed_data 
FROM parsing_jobs 
WHERE id = 'your-job-id-uuid';

-- View all successful parsings with JSON
SELECT id, filename, parsed_data->'contact'->'name' as candidate_name,
       parsed_data->'parsing_metadata'->'overall_confidence' as confidence
FROM parsing_jobs 
WHERE status = 'success';

-- View JSON structure
SELECT jsonb_keys(parsed_data) as json_keys
FROM parsing_jobs 
WHERE status = 'success'
LIMIT 1;
```

### **Method 2: Python/psycopg2**
```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="resume_parser", 
    user="postgres",
    password="postgres"
)

cursor = conn.cursor()

# Get JSON for specific job
cursor.execute("""
    SELECT parsed_data 
    FROM parsing_jobs 
    WHERE id = %s
""", ('your-job-id-uuid',))

result = cursor.fetchone()
if result:
    parsed_json = result[0]
    print(f"Parsed JSON: {parsed_json}")

conn.close()
```

### **Method 3: Using pgAdmin or DBeaver**
1. Connect to PostgreSQL database
2. Navigate to `parsing_jobs` table
3. Double-click on `parsed_data` column to view JSON
4. Use JSON viewer to explore structure

---

## 📊 **JSON Structure in Database**

### **What's Stored in `parsed_data` (JSONB):**
```json
{
  "contact": {
    "name": {"name": "John Doe", "confidence": 0.95},
    "email": {"email": "john.doe@email.com", "confidence": 0.98},
    "phone": {"phone": "+1-555-123-4567", "confidence": 0.90}
  },
  "work_experience": [
    {
      "company": {"name": "Google", "confidence": 0.95},
      "title": {"title": "Senior Software Engineer", "confidence": 0.93},
      "location": "Mountain View, CA",
      "start_date": "2020-01-01",
      "bullet_points": ["Led team of 5 engineers"]
    }
  ],
  "education": [
    {
      "institution": {"name": "Stanford University", "confidence": 0.96},
      "degree": {"degree": "B.S. Computer Science", "confidence": 0.94}
    }
  ],
  "skills": {
    "technical_skills": [
      {"skill": "Python", "confidence": 0.95},
      {"skill": "AWS", "confidence": 0.88}
    ]
  },
  "parsing_metadata": {
    "models_used": ["spaCy", "rule_based"],
    "overall_confidence": 0.89,
    "processing_time": 2.34
  }
}
```

---

## 🎯 **Useful SQL Queries**

### **Monitor Parsing Results:**
```sql
-- Recent successful parsings
SELECT id, filename, created_at, 
       parsed_data->'parsing_metadata'->>'overall_confidence' as confidence,
       parsed_data->'parsing_metadata'->>'models_used' as models
FROM parsing_jobs 
WHERE status = 'success' 
ORDER BY created_at DESC 
LIMIT 10;

-- Failed parsings with errors
SELECT id, filename, error_message, created_at
FROM parsing_jobs 
WHERE status = 'failed'
ORDER BY created_at DESC;

-- Parsing statistics
SELECT 
    COUNT(*) as total_jobs,
    COUNT(CASE WHEN status = 'success' THEN 1 END) as successful,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
    AVG(confidence_score) as avg_confidence
FROM parsing_jobs;
```

### **Search Parsed Data:**
```sql
-- Find candidates with specific skills
SELECT id, filename, parsed_data->'contact'->'name'->>'name' as name
FROM parsing_jobs 
WHERE status = 'success'
  AND parsed_data->'skills'->'technical_skills' ? 'Python';

-- Find experience at specific companies
SELECT id, filename, 
       parsed_data->'work_experience' as experience
FROM parsing_jobs 
WHERE status = 'success'
  AND parsed_data->'work_experience' @> 
    '[{"company": {"name": "Google"}}]';

-- Find by confidence threshold
SELECT id, filename, confidence_score
FROM parsing_jobs 
WHERE status = 'success'
  AND confidence_score > 0.8;
```

---

## 🔧 **Database Connection Info**

### **Connection Details:**
```python
# From config.py
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/resume_parser"

# Connection parameters:
Host: localhost
Port: 5432
Database: resume_parser
Username: postgres
Password: postgres
```

### **Connect with psql:**
```bash
psql -h localhost -p 5432 -U postgres -d resume_parser
```

---

## 📈 **JSONB vs JSON Performance**

### **Why JSONB?**
- **Indexing**: Can create GIN indexes on JSONB data
- **Querying**: Supports JSON operators (`@>`, `?`, `->>`)
- **Storage**: More efficient than plain JSON
- **Performance**: Faster for complex queries

### **Create Index for Performance:**
```sql
-- Index on specific JSON paths
CREATE INDEX idx_parsed_data_name ON parsing_jobs 
USING GIN ((parsed_data->'contact'->'name'));

-- Index on skills array
CREATE INDEX idx_parsed_data_skills ON parsing_jobs 
USING GIN ((parsed_data->'skills'->'technical_skills'));
```

---

## 🚀 **Quick Access Script**

```python
import psycopg2
import json

def get_parsed_json(job_id):
    """Get parsed JSON from database"""
    conn = psycopg2.connect(
        host="localhost",
        database="resume_parser",
        user="postgres", 
        password="postgres"
    )
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT parsed_data, filename, status, confidence_score
        FROM parsing_jobs 
        WHERE id = %s
    """, (job_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        parsed_data, filename, status, confidence = result
        return {
            "job_id": job_id,
            "filename": filename,
            "status": status,
            "confidence": confidence,
            "parsed_json": parsed_data
        }
    else:
        return None

# Usage
result = get_parsed_json('your-job-id-uuid')
if result:
    print(f"Filename: {result['filename']}")
    print(f"Status: {result['status']}")
    print(f"Confidence: {result['confidence']}")
    print(f"JSON: {json.dumps(result['parsed_json'], indent=2)}")
```

---

## 🏆 **Summary**

**The complete parsed JSON is stored in:**
- **Database**: `parsing_jobs.parsed_data` (JSONB column)
- **File Backup**: `parsing_jobs.parsed_json_path` (file path)
- **Access via**: SQL queries, Python, or database tools

**Key Column**: `parsed_data` (JSONB) - This contains your complete structured resume data! 🎯
