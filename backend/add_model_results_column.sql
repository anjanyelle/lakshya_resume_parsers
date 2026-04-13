-- Add model_results column to candidates table
-- Run this SQL script directly on your database

ALTER TABLE candidates ADD COLUMN IF NOT EXISTS model_results JSONB;

-- Verify the column was added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'candidates' AND column_name = 'model_results';
