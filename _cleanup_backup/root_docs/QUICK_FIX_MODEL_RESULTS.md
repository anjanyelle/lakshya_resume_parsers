# Quick Fix: Add model_results Column

## 🎯 **Simple Solution (No Alembic Required)**

Since the Alembic migration has configuration issues, here's the quickest way to add the `model_results` column:

---

## **Option 1: Using SQLite (if using SQLite database)**

```bash
cd backend

# Open the database
sqlite3 resume_parser.db

# Add the column
ALTER TABLE candidates ADD COLUMN model_results TEXT;

# Verify
.schema candidates

# Exit
.quit
```

---

## **Option 2: Using PostgreSQL (if using PostgreSQL)**

```bash
# Connect to your database
psql -U your_username -d resume_parser

# Add the column
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS model_results JSONB;

# Verify
\d candidates

# Exit
\q
```

---

## **Option 3: The column might already exist!**

The code changes I made to the model are already in place. Try this:

### **Just restart your services and test:**

```bash
# 1. Restart backend (in one terminal)
cd backend/src
npm run dev

# 2. Restart AI service (in another terminal)
cd ai-service
source venv/bin/activate
python main.py

# 3. Upload a NEW resume and check if model_results appears
```

**Why this might work:** The SQLAlchemy ORM might automatically create the column when the backend starts if it doesn't exist (depending on your configuration).

---

## **Option 4: Manual SQL Script**

I've created a SQL file for you: `backend/add_model_results_column.sql`

Run it manually on your database:

```bash
# For SQLite
sqlite3 backend/resume_parser.db < backend/add_model_results_column.sql

# For PostgreSQL
psql -U your_username -d your_database_name -f backend/add_model_results_column.sql
```

---

## ✅ **Verification**

After adding the column, verify it exists:

### **SQLite:**
```bash
sqlite3 backend/resume_parser.db "PRAGMA table_info(candidates);" | grep model_results
```

### **PostgreSQL:**
```bash
psql -U your_username -d your_database_name -c "\d candidates" | grep model_results
```

---

## 🚀 **Then Test**

1. **Restart both services** (backend and AI service)
2. **Upload a NEW resume** (not an existing one)
3. **Check the browser console** - `model_results` should be populated
4. **Check the API response** at `/candidates/{id}` - should include `model_results`

---

## 🔍 **If Still Undefined**

The column might already exist but not being populated. Check the backend logs when uploading:

Look for this log message:
```
Saved model_results to candidate record
```

If you don't see it, the issue is in the data flow, not the database schema.

---

## 📝 **Summary**

**Simplest approach:**
1. Try Option 3 first (just restart services)
2. If that doesn't work, manually add the column using Option 1 or 2
3. Restart services
4. Upload a new resume
5. Check if `model_results` is populated

The code changes are already in place - you just need the database column to exist!
