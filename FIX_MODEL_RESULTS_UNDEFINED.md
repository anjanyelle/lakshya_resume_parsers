# Fix: model_results Field Undefined

## 🔍 **Problem**
The `model_results` field is showing as `undefined` in the frontend because it's not being stored in the database or returned in the API response.

## ✅ **Solution Applied**

I've made the following changes to fix this issue:

### **1. Added `model_results` Column to Database Model**
**File**: `backend/app/models/candidate.py`

Added a new JSONB column to store the raw DeBERTa extraction results:
```python
model_results: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
```

### **2. Added `model_results` to API Response Schema**
**File**: `backend/app/schemas/public.py`

Added the field to `CandidatePublicRead` schema:
```python
model_results: Optional[dict] = None
```

### **3. Save `model_results` to Candidate Record**
**File**: `backend/app/workers/pipeline.py`

Added code to save model_results when updating candidate:
```python
# Store model_results for UI display
if parsed_data.get("model_results"):
    candidate.model_results = parsed_data.get("model_results")
    logger.info(f"Saved model_results to candidate record")
```

### **4. Created Database Migration**
**File**: `backend/alembic/versions/add_model_results_to_candidates.py`

Created migration to add the column to existing database.

---

## 🚀 **How to Apply These Changes**

### **Step 1: Run Database Migration**

```bash
cd backend

# Run the migration to add the column
alembic upgrade head
```

If you get an error about revision ID, update the migration file:
1. Find the latest revision: `alembic current`
2. Update `down_revision` in the migration file with that revision ID

### **Step 2: Restart Backend Server**

```bash
# Stop the current backend server (Ctrl+C)

# Restart it
cd backend/src
npm run dev
```

### **Step 3: Restart AI Service**

```bash
# Stop the current AI service (Ctrl+C)

# Restart it
cd ai-service
source venv/bin/activate
python main.py
```

### **Step 4: Test with a New Upload**

1. Upload a new resume (the fixes won't apply to already-parsed resumes)
2. Check the browser console - `model_results` should now be populated
3. The `ModelResultsView` component should display the raw extraction data

---

## 📊 **What `model_results` Contains**

The `model_results` field will contain:

```json
{
  "deberta_extraction": {
    "work_experience": [...],
    "education": [...],
    "companies": ["TechNova Solutions Pvt Ltd", "CodeCraft Technologies"],
    "job_titles": ["Software Engineer", "Frontend Developer"],
    "institutions": ["JNTU Hyderabad"],
    "degrees": ["Bachelor of Technology"],
    "source": "deberta_ner"
  }
}
```

---

## 🐛 **Additional Fixes Applied**

### **Fixed Experience Extraction Bugs**

I also fixed three critical bugs in the experience extraction:

1. **Prevented "SKILLS" section from being extracted as work experience**
2. **Fixed job title/company name swapping**
3. **Preserved full company names** (e.g., "TechNova Solutions Pvt Ltd" instead of truncating)

These fixes are in:
- `ai-service/parsers/experience_extractor.py`

---

## 🔍 **Troubleshooting**

### **If `model_results` is still undefined:**

1. **Check if migration ran successfully:**
   ```bash
   cd backend
   alembic current
   ```

2. **Check database column exists:**
   ```sql
   \d candidates
   ```
   Look for `model_results` column.

3. **Check backend logs:**
   Look for: `"Saved model_results to candidate record"`

4. **Upload a NEW resume** - existing candidates won't have this field populated.

5. **Check AI service response:**
   Look in AI service logs for `"Added model_results to merged_results"`

---

## ✅ **Verification Checklist**

- [ ] Database migration completed successfully
- [ ] Backend server restarted
- [ ] AI service restarted
- [ ] New resume uploaded (not an old one)
- [ ] Browser console shows `model_results` is populated
- [ ] `ModelResultsView` component displays extraction data
- [ ] No "SKILLS" entries in work experience
- [ ] Job titles and company names are correct
- [ ] Full company names preserved (with "Pvt Ltd", "Solutions", etc.)

---

## 📝 **Summary**

The `model_results` field was undefined because:
1. It wasn't stored in the database
2. It wasn't included in the API response schema
3. It wasn't being saved to the candidate record

All three issues have been fixed. After running the migration and restarting services, uploading a new resume will populate the `model_results` field with raw DeBERTa extraction data for debugging purposes.
